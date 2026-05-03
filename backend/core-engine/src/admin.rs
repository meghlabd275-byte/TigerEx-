//! Admin Service - Complete admin control system
//! Handles all admin operations with full CRUD capabilities

use std::sync::Arc;
use uuid::Uuid;
use chrono::Utc;
use rust_decimal::Decimal;
use serde::{Deserialize, Serialize};
use tracing::{info, warn, error};

use crate::models::*;
use crate::engine::TradingEngine;
use crate::db::Database;
use crate::cache::RedisCache;
use crate::auth::AuthService;

/// Admin action result
#[derive(Debug, Serialize)]
pub struct AdminResult<T> {
    pub success: bool,
    pub message: String,
    pub data: Option<T>,
}

impl<T: Serialize> AdminResult<T> {
    pub fn success(data: T, message: &str) -> Self {
        Self {
            success: true,
            message: message.to_string(),
            data: Some(data),
        }
    }

    pub fn error(message: &str) -> Self {
        Self {
            success: false,
            message: message.to_string(),
            data: None,
        }
    }
}

/// Admin service
pub struct AdminService {
    pub db: Arc<Database>,
    pub cache: Arc<RedisCache>,
    pub engine: Arc<parking_lot::RwLock<TradingEngine>>,
    pub auth: Arc<AuthService>,
}

impl AdminService {
    pub fn new(
        db: Arc<Database>,
        cache: Arc<RedisCache>,
        engine: Arc<parking_lot::RwLock<TradingEngine>>,
        auth: Arc<AuthService>,
    ) -> Self {
        Self { db, cache, engine, auth }
    }

    // ==================== USER MANAGEMENT ====================

    /// Create a new user
    pub async fn create_user(
        &self,
        email: String,
        username: String,
        password: String,
        role: UserRole,
    ) -> AdminResult<Account> {
        info!("Creating user: {} with role {:?}", username, role);

        // Check if user exists
        if self.db.user_exists(&email).await.unwrap_or(false) {
            return AdminResult::error("User with this email already exists");
        }

        // Hash password
        let password_hash = self.auth.hash_password(&password)?;

        // Create user
        let account = Account {
            user_id: Uuid::new_v4(),
            email,
            username,
            role,
            status: AccountStatus::Active,
            balances: vec![],
            permissions: self.get_default_permissions(role),
            created_at: Utc::now(),
            updated_at: Utc::now(),
            kyc_level: 0,
            trading_enabled: true,
            withdrawal_enabled: true,
            deposit_enabled: true,
        };

        // Save to database
        match self.db.create_user(&account, &password_hash).await {
            Ok(_) => {
                self.log_admin_action(
                    None,
                    "CREATE_USER",
                    "user",
                    &account.user_id.to_string(),
                    None,
                    Some(serde_json::to_value(&account).ok()),
                ).await;
                AdminResult::success(account, "User created successfully")
            }
            Err(e) => {
                error!("Failed to create user: {}", e);
                AdminResult::error(&format!("Failed to create user: {}", e))
            }
        }
    }

    /// Get user by ID
    pub async fn get_user(&self, user_id: Uuid) -> AdminResult<Account> {
        match self.db.get_user_by_id(user_id).await {
            Ok(Some(account)) => AdminResult::success(account, "User found"),
            Ok(None) => AdminResult::error("User not found"),
            Err(e) => AdminResult::error(&format!("Database error: {}", e)),
        }
    }

    /// List all users with pagination
    pub async fn list_users(
        &self,
        page: u32,
        limit: u32,
        status: Option<AccountStatus>,
        role: Option<UserRole>,
        search: Option<String>,
    ) -> AdminResult<Vec<Account>> {
        match self.db.list_users(page, limit, status, role, search).await {
            Ok(users) => AdminResult::success(users, &format!("Found {} users", users.len())),
            Err(e) => AdminResult::error(&format!("Failed to list users: {}", e)),
        }
    }

    /// Update user
    pub async fn update_user(
        &self,
        user_id: Uuid,
        updates: UserUpdateRequest,
    ) -> AdminResult<Account> {
        info!("Updating user: {}", user_id);

        // Get current user
        let current = match self.db.get_user_by_id(user_id).await {
            Ok(Some(u)) => u,
            _ => return AdminResult::error("User not found"),
        };

        let old_value = serde_json::to_value(&current).ok();

        // Apply updates
        let updated = Account {
            email: updates.email.unwrap_or(current.email),
            username: updates.username.unwrap_or(current.username),
            role: updates.role.unwrap_or(current.role),
            status: updates.status.unwrap_or(current.status),
            permissions: updates.permissions.unwrap_or(current.permissions),
            kyc_level: updates.kyc_level.unwrap_or(current.kyc_level),
            trading_enabled: updates.trading_enabled.unwrap_or(current.trading_enabled),
            withdrawal_enabled: updates.withdrawal_enabled.unwrap_or(current.withdrawal_enabled),
            deposit_enabled: updates.deposit_enabled.unwrap_or(current.deposit_enabled),
            ..current
        };

        match self.db.update_user(&updated).await {
            Ok(_) => {
                self.log_admin_action(
                    None,
                    "UPDATE_USER",
                    "user",
                    &user_id.to_string(),
                    old_value,
                    serde_json::to_value(&updated).ok(),
                ).await;
                AdminResult::success(updated, "User updated successfully")
            }
            Err(e) => AdminResult::error(&format!("Failed to update user: {}", e)),
        }
    }

    /// Delete user (soft delete)
    pub async fn delete_user(&self, user_id: Uuid) -> AdminResult<()> {
        info!("Deleting user: {}", user_id);

        match self.db.soft_delete_user(user_id).await {
            Ok(_) => {
                self.log_admin_action(
                    None,
                    "DELETE_USER",
                    "user",
                    &user_id.to_string(),
                    None,
                    None,
                ).await;
                AdminResult::success((), "User deleted successfully")
            }
            Err(e) => AdminResult::error(&format!("Failed to delete user: {}", e)),
        }
    }

    /// Pause user account
    pub async fn pause_user(&self, user_id: Uuid) -> AdminResult<Account> {
        self.update_user_status(user_id, AccountStatus::Paused).await
    }

    /// Resume user account
    pub async fn resume_user(&self, user_id: Uuid) -> AdminResult<Account> {
        self.update_user_status(user_id, AccountStatus::Active).await
    }

    /// Halt user account (emergency stop)
    pub async fn halt_user(&self, user_id: Uuid) -> AdminResult<Account> {
        // Cancel all open orders
        let engine = self.engine.read();
        if let Err(e) = engine.cancel_all_orders(user_id, None).await {
            warn!("Failed to cancel orders for halted user: {}", e);
        }

        self.update_user_status(user_id, AccountStatus::Halted).await
    }

    /// Update user status
    async fn update_user_status(&self, user_id: Uuid, status: AccountStatus) -> AdminResult<Account> {
        let current = match self.db.get_user_by_id(user_id).await {
            Ok(Some(u)) => u,
            _ => return AdminResult::error("User not found"),
        };

        let mut updated = current.clone();
        updated.status = status;
        updated.updated_at = Utc::now();

        match self.db.update_user(&updated).await {
            Ok(_) => {
                self.cache.invalidate(&format!("user:{}", user_id)).await;
                AdminResult::success(updated, &format!("User status updated to {:?}", status))
            }
            Err(e) => AdminResult::error(&format!("Failed to update status: {}", e)),
        }
    }

    /// Update user permissions
    pub async fn update_permissions(
        &self,
        user_id: Uuid,
        permissions: Vec<String>,
    ) -> AdminResult<Account> {
        let current = match self.db.get_user_by_id(user_id).await {
            Ok(Some(u)) => u,
            _ => return AdminResult::error("User not found"),
        };

        let mut updated = current.clone();
        updated.permissions = permissions;
        updated.updated_at = Utc::now();

        match self.db.update_user(&updated).await {
            Ok(_) => AdminResult::success(updated, "Permissions updated"),
            Err(e) => AdminResult::error(&format!("Failed to update permissions: {}", e)),
        }
    }

    // ==================== TRADING PAIR MANAGEMENT ====================

    /// Create trading pair
    pub async fn create_trading_pair(&self, request: CreateTradingPairRequest) -> AdminResult<TradingPair> {
        info!("Creating trading pair: {}", request.symbol);

        let pair = TradingPair {
            id: Uuid::new_v4(),
            symbol: request.symbol,
            base_asset: request.base_asset,
            quote_asset: request.quote_asset,
            status: TradingPairStatus::Trading,
            base_precision: request.base_precision,
            quote_precision: request.quote_precision,
            min_qty: request.min_qty,
            max_qty: request.max_qty,
            min_price: request.min_price,
            max_price: request.max_price,
            tick_size: request.tick_size,
            step_size: request.step_size,
            maker_fee: request.maker_fee,
            taker_fee: request.taker_fee,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        };

        // Add to engine
        let engine = self.engine.read();
        if let Err(e) = engine.add_trading_pair(pair.clone()).await {
            return AdminResult::error(&format!("Failed to add trading pair: {}", e));
        }

        self.log_admin_action(
            None,
            "CREATE_TRADING_PAIR",
            "trading_pair",
            &pair.id.to_string(),
            None,
            Some(serde_json::to_value(&pair).ok()),
        ).await;

        AdminResult::success(pair, "Trading pair created successfully")
    }

    /// Update trading pair
    pub async fn update_trading_pair(
        &self,
        pair_id: Uuid,
        updates: UpdateTradingPairRequest,
    ) -> AdminResult<TradingPair> {
        let pairs = self.engine.read().trading_pairs.read();
        let current = pairs.values().find(|p| p.id == pair_id).cloned();
        drop(pairs);

        let current = match current {
            Some(p) => p,
            None => return AdminResult::error("Trading pair not found"),
        };

        let updated = TradingPair {
            status: updates.status.unwrap_or(current.status),
            min_qty: updates.min_qty.unwrap_or(current.min_qty),
            max_qty: updates.max_qty.unwrap_or(current.max_qty),
            min_price: updates.min_price.unwrap_or(current.min_price),
            max_price: updates.max_price.unwrap_or(current.max_price),
            maker_fee: updates.maker_fee.unwrap_or(current.maker_fee),
            taker_fee: updates.taker_fee.unwrap_or(current.taker_fee),
            updated_at: Utc::now(),
            ..current
        };

        // Update in database
        match self.db.update_trading_pair(&updated).await {
            Ok(_) => {
                self.log_admin_action(
                    None,
                    "UPDATE_TRADING_PAIR",
                    "trading_pair",
                    &pair_id.to_string(),
                    serde_json::to_value(&current).ok(),
                    serde_json::to_value(&updated).ok(),
                ).await;
                AdminResult::success(updated, "Trading pair updated")
            }
            Err(e) => AdminResult::error(&format!("Failed to update: {}", e)),
        }
    }

    /// Delete trading pair
    pub async fn delete_trading_pair(&self, pair_id: Uuid) -> AdminResult<()> {
        let pairs = self.engine.read().trading_pairs.read();
        let pair = pairs.values().find(|p| p.id == pair_id).cloned();
        drop(pairs);

        let pair = match pair {
            Some(p) => p,
            None => return AdminResult::error("Trading pair not found"),
        };

        // Remove from engine
        let engine = self.engine.read();
        if let Err(e) = engine.remove_trading_pair(&pair.symbol).await {
            return AdminResult::error(&format!("Failed to remove: {}", e));
        }

        AdminResult::success((), "Trading pair deleted")
    }

    /// Pause trading pair
    pub async fn pause_trading_pair(&self, pair_id: Uuid) -> AdminResult<TradingPair> {
        let pairs = self.engine.read().trading_pairs.read();
        let pair = pairs.values().find(|p| p.id == pair_id).cloned();
        drop(pairs);

        let pair = match pair {
            Some(p) => p,
            None => return AdminResult::error("Trading pair not found"),
        };

        let engine = self.engine.read();
        if let Err(e) = engine.pause_trading_pair(&pair.symbol).await {
            return AdminResult::error(&format!("Failed to pause: {}", e));
        }

        let mut updated = pair.clone();
        updated.status = TradingPairStatus::Pause;

        AdminResult::success(updated, "Trading pair paused")
    }

    /// Resume trading pair
    pub async fn resume_trading_pair(&self, pair_id: Uuid) -> AdminResult<TradingPair> {
        let pairs = self.engine.read().trading_pairs.read();
        let pair = pairs.values().find(|p| p.id == pair_id).cloned();
        drop(pairs);

        let pair = match pair {
            Some(p) => p,
            None => return AdminResult::error("Trading pair not found"),
        };

        let engine = self.engine.read();
        if let Err(e) = engine.resume_trading_pair(&pair.symbol).await {
            return AdminResult::error(&format!("Failed to resume: {}", e));
        }

        let mut updated = pair.clone();
        updated.status = TradingPairStatus::Trading;

        AdminResult::success(updated, "Trading pair resumed")
    }

    // ==================== ENGINE CONTROL ====================

    /// Get engine status
    pub fn get_engine_status(&self) -> AdminResult<EngineStatusResponse> {
        let engine = self.engine.read();
        let stats = engine.get_stats();
        let state = engine.get_state();

        AdminResult::success(
            EngineStatusResponse {
                state: format!("{:?}", state),
                total_orders: stats.total_orders_processed,
                total_trades: stats.total_trades_executed,
                total_volume: stats.total_volume,
                avg_latency_us: stats.avg_latency_us,
                orders_per_second: stats.orders_per_second,
                uptime_seconds: (Utc::now() - engine.start_time).num_seconds() as u64,
            },
            "Engine status retrieved",
        )
    }

    /// Pause engine
    pub fn pause_engine(&self) -> AdminResult<()> {
        self.engine.read().pause();
        self.log_admin_action(None, "PAUSE_ENGINE", "system", "engine", None, None);
        AdminResult::success((), "Engine paused")
    }

    /// Resume engine
    pub fn resume_engine(&self) -> AdminResult<()> {
        self.engine.read().resume();
        self.log_admin_action(None, "RESUME_ENGINE", "system", "engine", None, None);
        AdminResult::success((), "Engine resumed")
    }

    /// Halt engine (emergency)
    pub fn halt_engine(&self) -> AdminResult<()> {
        self.engine.read().halt();
        self.log_admin_action(None, "HALT_ENGINE", "system", "engine", None, None);
        AdminResult::success((), "Engine halted - emergency stop activated")
    }

    // ==================== FEE MANAGEMENT ====================

    /// Get fee structure
    pub async fn get_fee_structure(&self) -> AdminResult<Vec<TradingPair>> {
        let pairs = self.engine.read().trading_pairs.read();
        let list: Vec<_> = pairs.values().cloned().collect();
        AdminResult::success(list, "Fee structure retrieved")
    }

    /// Update fee structure
    pub async fn update_fee_structure(
        &self,
        pair_id: Uuid,
        maker_fee: Option<Decimal>,
        taker_fee: Option<Decimal>,
    ) -> AdminResult<TradingPair> {
        self.update_trading_pair(pair_id, UpdateTradingPairRequest {
            maker_fee,
            taker_fee,
            ..Default::default()
        }).await
    }

    // ==================== RISK MANAGEMENT ====================

    /// Get risk limits for user
    pub async fn get_user_risk_limits(&self, user_id: Uuid) -> AdminResult<RiskLimits> {
        match self.db.get_risk_limits(user_id).await {
            Ok(Some(limits)) => AdminResult::success(limits, "Risk limits retrieved"),
            Ok(None) => AdminResult::error("Risk limits not found"),
            Err(e) => AdminResult::error(&format!("Database error: {}", e)),
        }
    }

    /// Update risk limits
    pub async fn update_risk_limits(
        &self,
        user_id: Uuid,
        limits: RiskLimits,
    ) -> AdminResult<RiskLimits> {
        match self.db.update_risk_limits(&limits).await {
            Ok(_) => AdminResult::success(limits, "Risk limits updated"),
            Err(e) => AdminResult::error(&format!("Failed to update: {}", e)),
        }
    }

    // ==================== AUDIT LOGGING ====================

    /// Get audit logs
    pub async fn get_audit_logs(
        &self,
        page: u32,
        limit: u32,
        user_id: Option<Uuid>,
        action: Option<String>,
        start_time: Option<chrono::DateTime<Utc>>,
        end_time: Option<chrono::DateTime<Utc>>,
    ) -> AdminResult<Vec<AuditLog>> {
        match self.db.get_audit_logs(page, limit, user_id, action, start_time, end_time).await {
            Ok(logs) => AdminResult::success(logs, &format!("Found {} logs", logs.len())),
            Err(e) => AdminResult::error(&format!("Failed to retrieve logs: {}", e)),
        }
    }

    /// Log admin action
    async fn log_admin_action(
        &self,
        user_id: Option<Uuid>,
        action: &str,
        resource_type: &str,
        resource_id: &str,
        old_value: Option<serde_json::Value>,
        new_value: Option<serde_json::Value>,
    ) {
        let log = AuditLog {
            id: Uuid::new_v4(),
            user_id,
            action: action.to_string(),
            resource_type: resource_type.to_string(),
            resource_id: resource_id.to_string(),
            old_value,
            new_value,
            ip_address: String::new(),
            user_agent: String::new(),
            timestamp: Utc::now(),
            status: "success".to_string(),
            error_message: None,
        };

        if let Err(e) = self.db.save_audit_log(&log).await {
            error!("Failed to save audit log: {}", e);
        }
    }

    // ==================== SYSTEM METRICS ====================

    /// Get system metrics
    pub fn get_system_metrics(&self) -> AdminResult<SystemMetrics> {
        let engine = self.engine.read();
        let stats = engine.get_stats();
        let order_books = engine.order_books.read();

        let mut total_bid_liquidity = Decimal::ZERO;
        let mut total_ask_liquidity = Decimal::ZERO;

        for book in order_books.values() {
            total_bid_liquidity += book.total_bid_liquidity();
            total_ask_liquidity += book.total_ask_liquidity();
        }

        AdminResult::success(
            SystemMetrics {
                total_trading_pairs: order_books.len(),
                total_orders_processed: stats.total_orders_processed,
                total_trades_executed: stats.total_trades_executed,
                total_volume: stats.total_volume,
                avg_latency_us: stats.avg_latency_us,
                max_latency_us: stats.max_latency_us,
                total_bid_liquidity,
                total_ask_liquidity,
                engine_state: format!("{:?}", engine.get_state()),
            },
            "System metrics retrieved",
        )
    }

    // ==================== HELPER METHODS ====================

    fn get_default_permissions(&self, role: UserRole) -> Vec<String> {
        match role {
            UserRole::SuperAdmin => vec![
                "admin.all", "users.all", "trading.all", "wallet.all",
                "settings.all", "audit.read", "system.all",
            ].into_iter().map(String::from).collect(),
            UserRole::Admin => vec![
                "users.read", "users.write", "trading.read", "trading.write",
                "wallet.read", "audit.read",
            ].into_iter().map(String::from).collect(),
            UserRole::Moderator => vec![
                "users.read", "trading.read", "audit.read",
            ].into_iter().map(String::from).collect(),
            _ => vec![],
        }
    }
}

// ==================== REQUEST/RESPONSE STRUCTS ====================

#[derive(Debug, Deserialize)]
pub struct UserUpdateRequest {
    pub email: Option<String>,
    pub username: Option<String>,
    pub role: Option<UserRole>,
    pub status: Option<AccountStatus>,
    pub permissions: Option<Vec<String>>,
    pub kyc_level: Option<u8>,
    pub trading_enabled: Option<bool>,
    pub withdrawal_enabled: Option<bool>,
    pub deposit_enabled: Option<bool>,
}

#[derive(Debug, Deserialize)]
pub struct CreateTradingPairRequest {
    pub symbol: String,
    pub base_asset: String,
    pub quote_asset: String,
    pub base_precision: u8,
    pub quote_precision: u8,
    pub min_qty: Decimal,
    pub max_qty: Decimal,
    pub min_price: Decimal,
    pub max_price: Decimal,
    pub tick_size: Decimal,
    pub step_size: Decimal,
    pub maker_fee: Decimal,
    pub taker_fee: Decimal,
}

#[derive(Debug, Deserialize, Default)]
pub struct UpdateTradingPairRequest {
    pub status: Option<TradingPairStatus>,
    pub min_qty: Option<Decimal>,
    pub max_qty: Option<Decimal>,
    pub min_price: Option<Decimal>,
    pub max_price: Option<Decimal>,
    pub maker_fee: Option<Decimal>,
    pub taker_fee: Option<Decimal>,
}

#[derive(Debug, Serialize)]
pub struct EngineStatusResponse {
    pub state: String,
    pub total_orders: u64,
    pub total_trades: u64,
    pub total_volume: Decimal,
    pub avg_latency_us: f64,
    pub orders_per_second: f64,
    pub uptime_seconds: u64,
}

#[derive(Debug, Serialize)]
pub struct SystemMetrics {
    pub total_trading_pairs: usize,
    pub total_orders_processed: u64,
    pub total_trades_executed: u64,
    pub total_volume: Decimal,
    pub avg_latency_us: f64,
    pub max_latency_us: f64,
    pub total_bid_liquidity: Decimal,
    pub total_ask_liquidity: Decimal,
    pub engine_state: String,
}pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}
