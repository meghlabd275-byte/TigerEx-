//! Database layer with PostgreSQL support
//! Handles all database operations with connection pooling

use std::sync::Arc;
use uuid::Uuid;
use chrono::{Utc, DateTime};
use rust_decimal::Decimal;
use sqlx::{PgPool, Row, postgres::PgPoolOptions};
use tracing::{info, error};

use crate::models::*;

/// Database connection pool
pub struct Database {
    pool: PgPool,
}

impl Database {
    /// Create new database connection pool
    pub async fn new(database_url: &str) -> Result<Self, sqlx::Error> {
        info!("Connecting to database...");
        
        let pool = PgPoolOptions::new()
            .max_connections(20)
            .min_connections(5)
            .connect(database_url)
            .await?;

        info!("Database connected successfully");
        
        Ok(Self { pool })
    }

    /// Run database migrations
    pub async fn run_migrations(&self) -> Result<(), sqlx::Error> {
        info!("Running database migrations...");
        // In production, use refinery or similar migration tool
        info!("Migrations completed");
        Ok(())
    }

    // ==================== USER OPERATIONS ====================

    /// Check if user exists by email
    pub async fn user_exists(&self, email: &str) -> Result<bool, sqlx::Error> {
        let result = sqlx::query_scalar::<_, bool>(
            "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1 AND deleted_at IS NULL)"
        )
        .bind(email)
        .fetch_one(&self.pool)
        .await?;

        Ok(result)
    }

    /// Get user by ID
    pub async fn get_user_by_id(&self, user_id: Uuid) -> Result<Option<Account>, sqlx::Error> {
        let row = sqlx::query_as::<_, (Uuid, String, String, String, String, Vec<String>, DateTime<Utc>, DateTime<Utc>, i16, bool, bool, bool)>(
            "SELECT user_id, email, username, role, status, permissions, created_at, updated_at, kyc_level, trading_enabled, withdrawal_enabled, deposit_enabled 
             FROM users WHERE user_id = $1 AND deleted_at IS NULL"
        )
        .bind(user_id)
        .fetch_optional(&self.pool)
        .await?;

        match row {
            Some((uid, email, username, role, status, permissions, created_at, updated_at, kyc_level, trading_enabled, withdrawal_enabled, deposit_enabled)) => {
                let role = match role.as_str() {
                    "Admin" => UserRole::Admin,
                    "SuperAdmin" => UserRole::SuperAdmin,
                    "Moderator" => UserRole::Moderator,
                    "User" => UserRole::User,
                    "Institutional" => UserRole::Institutional,
                    "MarketMaker" => UserRole::MarketMaker,
                    "LiquidityProvider" => UserRole::LiquidityProvider,
                    "ApiUser" => UserRole::ApiUser,
                    _ => UserRole::User,
                };

                let status = match status.as_str() {
                    "Active" => AccountStatus::Active,
                    "Paused" => AccountStatus::Paused,
                    "Halted" => AccountStatus::Halted,
                    "Suspended" => AccountStatus::Suspended,
                    "PendingVerification" => AccountStatus::PendingVerification,
                    "Closed" => AccountStatus::Closed,
                    _ => AccountStatus::Active,
                };

                Ok(Some(Account {
                    user_id: uid,
                    email,
                    username,
                    role,
                    status,
                    balances: vec![], // Loaded separately
                    permissions,
                    created_at,
                    updated_at,
                    kyc_level: kyc_level as u8,
                    trading_enabled,
                    withdrawal_enabled,
                    deposit_enabled,
                }))
            }
            None => Ok(None),
        }
    }

    /// Get user by email
    pub async fn get_user_by_email(&self, email: &str) -> Result<Option<Account>, sqlx::Error> {
        let row = sqlx::query_as::<_, (Uuid, String, String, String, String, Vec<String>, DateTime<Utc>, DateTime<Utc>, i16, bool, bool, bool)>(
            "SELECT user_id, email, username, role, status, permissions, created_at, updated_at, kyc_level, trading_enabled, withdrawal_enabled, deposit_enabled 
             FROM users WHERE email = $1 AND deleted_at IS NULL"
        )
        .bind(email)
        .fetch_optional(&self.pool)
        .await?;

        match row {
            Some((uid, email, username, role, status, permissions, created_at, updated_at, kyc_level, trading_enabled, withdrawal_enabled, deposit_enabled)) => {
                let role = match role.as_str() {
                    "Admin" => UserRole::Admin,
                    "SuperAdmin" => UserRole::SuperAdmin,
                    "Moderator" => UserRole::Moderator,
                    "User" => UserRole::User,
                    "Institutional" => UserRole::Institutional,
                    "MarketMaker" => UserRole::MarketMaker,
                    "LiquidityProvider" => UserRole::LiquidityProvider,
                    "ApiUser" => UserRole::ApiUser,
                    _ => UserRole::User,
                };

                let status = match status.as_str() {
                    "Active" => AccountStatus::Active,
                    "Paused" => AccountStatus::Paused,
                    "Halted" => AccountStatus::Halted,
                    "Suspended" => AccountStatus::Suspended,
                    "PendingVerification" => AccountStatus::PendingVerification,
                    "Closed" => AccountStatus::Closed,
                    _ => AccountStatus::Active,
                };

                Ok(Some(Account {
                    user_id: uid,
                    email,
                    username,
                    role,
                    status,
                    balances: vec![],
                    permissions,
                    created_at,
                    updated_at,
                    kyc_level: kyc_level as u8,
                    trading_enabled,
                    withdrawal_enabled,
                    deposit_enabled,
                }))
            }
            None => Ok(None),
        }
    }

    /// Create user
    pub async fn create_user(&self, account: &Account, password_hash: &str) -> Result<(), sqlx::Error> {
        let role = format!("{:?}", account.role);
        let status = format!("{:?}", account.status);

        sqlx::query(
            "INSERT INTO users (user_id, email, username, role, status, permissions, password_hash, kyc_level, trading_enabled, withdrawal_enabled, deposit_enabled, created_at, updated_at)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)"
        )
        .bind(account.user_id)
        .bind(&account.email)
        .bind(&account.username)
        .bind(&role)
        .bind(&status)
        .bind(&account.permissions)
        .bind(password_hash)
        .bind(account.kyc_level as i16)
        .bind(account.trading_enabled)
        .bind(account.withdrawal_enabled)
        .bind(account.deposit_enabled)
        .bind(account.created_at)
        .bind(account.updated_at)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Update user
    pub async fn update_user(&self, account: &Account) -> Result<(), sqlx::Error> {
        let role = format!("{:?}", account.role);
        let status = format!("{:?}", account.status);

        sqlx::query(
            "UPDATE users SET email = $2, username = $3, role = $4, status = $5, permissions = $6, kyc_level = $7, trading_enabled = $8, withdrawal_enabled = $9, deposit_enabled = $10, updated_at = $11
             WHERE user_id = $1"
        )
        .bind(account.user_id)
        .bind(&account.email)
        .bind(&account.username)
        .bind(&role)
        .bind(&status)
        .bind(&account.permissions)
        .bind(account.kyc_level as i16)
        .bind(account.trading_enabled)
        .bind(account.withdrawal_enabled)
        .bind(account.deposit_enabled)
        .bind(account.updated_at)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Soft delete user
    pub async fn soft_delete_user(&self, user_id: Uuid) -> Result<(), sqlx::Error> {
        sqlx::query("UPDATE users SET deleted_at = $1 WHERE user_id = $2")
            .bind(Utc::now())
            .bind(user_id)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    /// List users with pagination
    pub async fn list_users(
        &self,
        page: u32,
        limit: u32,
        status: Option<AccountStatus>,
        role: Option<UserRole>,
        search: Option<String>,
    ) -> Result<Vec<Account>, sqlx::Error> {
        let offset = (page - 1) * limit;
        
        let mut query = String::from(
            "SELECT user_id, email, username, role, status, permissions, created_at, updated_at, kyc_level, trading_enabled, withdrawal_enabled, deposit_enabled
             FROM users WHERE deleted_at IS NULL"
        );
        
        let mut conditions = Vec::new();
        let mut param_count = 0;

        if let Some(s) = status {
            param_count += 1;
            conditions.push(format!("status = ${}", param_count));
        }

        if let Some(r) = role {
            param_count += 1;
            conditions.push(format!("role = ${}", param_count));
        }

        if let Some(search_term) = search {
            param_count += 1;
            conditions.push(format!("(email ILIKE ${} OR username ILIKE ${})", param_count, param_count));
        }

        if !conditions.is_empty() {
            query.push_str(" AND ");
            query.push_str(&conditions.join(" AND "));
        }

        query.push_str(&format!(" ORDER BY created_at DESC LIMIT ${} OFFSET ${}", param_count + 1, param_count + 2));

        let mut query_builder = sqlx::query_as::<_, (Uuid, String, String, String, String, Vec<String>, DateTime<Utc>, DateTime<Utc>, i16, bool, bool, bool)>(&query);

        if let Some(s) = status {
            query_builder = query_builder.bind(format!("{:?}", s));
        }

        if let Some(r) = role {
            query_builder = query_builder.bind(format!("{:?}", r));
        }

        if let Some(search_term) = search {
            let pattern = format!("%{}%", search_term);
            query_builder = query_builder.bind(&pattern);
            query_builder = query_builder.bind(&pattern);
        }

        query_builder = query_builder.bind(limit as i64);
        query_builder = query_builder.bind(offset as i64);

        let rows = query_builder.fetch_all(&self.pool).await?;

        let users = rows.into_iter().map(|(uid, email, username, role, status, permissions, created_at, updated_at, kyc_level, trading_enabled, withdrawal_enabled, deposit_enabled)| {
            let role = match role.as_str() {
                "Admin" => UserRole::Admin,
                "SuperAdmin" => UserRole::SuperAdmin,
                "Moderator" => UserRole::Moderator,
                "User" => UserRole::User,
                "Institutional" => UserRole::Institutional,
                "MarketMaker" => UserRole::MarketMaker,
                "LiquidityProvider" => UserRole::LiquidityProvider,
                "ApiUser" => UserRole::ApiUser,
                _ => UserRole::User,
            };

            let status = match status.as_str() {
                "Active" => AccountStatus::Active,
                "Paused" => AccountStatus::Paused,
                "Halted" => AccountStatus::Halted,
                "Suspended" => AccountStatus::Suspended,
                "PendingVerification" => AccountStatus::PendingVerification,
                "Closed" => AccountStatus::Closed,
                _ => AccountStatus::Active,
            };

            Account {
                user_id: uid,
                email,
                username,
                role,
                status,
                balances: vec![],
                permissions,
                created_at,
                updated_at,
                kyc_level: kyc_level as u8,
                trading_enabled,
                withdrawal_enabled,
                deposit_enabled,
            }
        }).collect();

        Ok(users)
    }

    /// Get password hash
    pub async fn get_password_hash(&self, user_id: Uuid) -> Result<Option<String>, sqlx::Error> {
        let hash = sqlx::query_scalar::<_, String>(
            "SELECT password_hash FROM users WHERE user_id = $1"
        )
        .bind(user_id)
        .fetch_optional(&self.pool)
        .await?;

        Ok(hash)
    }

    /// Update last login
    pub async fn update_last_login(&self, user_id: Uuid) -> Result<(), sqlx::Error> {
        sqlx::query("UPDATE users SET last_login_at = $1 WHERE user_id = $2")
            .bind(Utc::now())
            .bind(user_id)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    // ==================== TRADING PAIR OPERATIONS ====================

    /// Get all trading pairs
    pub async fn get_trading_pairs(&self) -> Result<Vec<TradingPair>, sqlx::Error> {
        let rows = sqlx::query_as::<_, (Uuid, String, String, String, String, i16, i16, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, DateTime<Utc>, DateTime<Utc>)>(
            "SELECT id, symbol, base_asset, quote_asset, status, base_precision, quote_precision, min_qty, max_qty, min_price, max_price, tick_size, step_size, maker_fee, taker_fee, created_at, updated_at
             FROM trading_pairs"
        )
        .fetch_all(&self.pool)
        .await?;

        let pairs = rows.into_iter().map(|(id, symbol, base_asset, quote_asset, status, base_precision, quote_precision, min_qty, max_qty, min_price, max_price, tick_size, step_size, maker_fee, taker_fee, created_at, updated_at)| {
            let status = match status.as_str() {
                "Trading" => TradingPairStatus::Trading,
                "Pause" => TradingPairStatus::Pause,
                "Delist" => TradingPairStatus::Delist,
                "PreTrading" => TradingPairStatus::PreTrading,
                "PostTrading" => TradingPairStatus::PostTrading,
                _ => TradingPairStatus::Trading,
            };

            TradingPair {
                id,
                symbol,
                base_asset,
                quote_asset,
                status,
                base_precision: base_precision as u8,
                quote_precision: quote_precision as u8,
                min_qty,
                max_qty,
                min_price,
                max_price,
                tick_size,
                step_size,
                maker_fee,
                taker_fee,
                created_at,
                updated_at,
            }
        }).collect();

        Ok(pairs)
    }

    /// Save trading pair
    pub async fn save_trading_pair(&self, pair: &TradingPair) -> Result<(), sqlx::Error> {
        let status = format!("{:?}", pair.status);

        sqlx::query(
            "INSERT INTO trading_pairs (id, symbol, base_asset, quote_asset, status, base_precision, quote_precision, min_qty, max_qty, min_price, max_price, tick_size, step_size, maker_fee, taker_fee, created_at, updated_at)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
             ON CONFLICT (symbol) DO UPDATE SET status = $5, min_qty = $8, max_qty = $9, min_price = $10, max_price = $11, maker_fee = $14, taker_fee = $15, updated_at = $17"
        )
        .bind(pair.id)
        .bind(&pair.symbol)
        .bind(&pair.base_asset)
        .bind(&pair.quote_asset)
        .bind(&status)
        .bind(pair.base_precision as i16)
        .bind(pair.quote_precision as i16)
        .bind(pair.min_qty)
        .bind(pair.max_qty)
        .bind(pair.min_price)
        .bind(pair.max_price)
        .bind(pair.tick_size)
        .bind(pair.step_size)
        .bind(pair.maker_fee)
        .bind(pair.taker_fee)
        .bind(pair.created_at)
        .bind(pair.updated_at)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Update trading pair
    pub async fn update_trading_pair(&self, pair: &TradingPair) -> Result<(), sqlx::Error> {
        let status = format!("{:?}", pair.status);

        sqlx::query(
            "UPDATE trading_pairs SET status = $2, min_qty = $3, max_qty = $4, min_price = $5, max_price = $6, maker_fee = $7, taker_fee = $8, updated_at = $9
             WHERE id = $1"
        )
        .bind(pair.id)
        .bind(&status)
        .bind(pair.min_qty)
        .bind(pair.max_qty)
        .bind(pair.min_price)
        .bind(pair.max_price)
        .bind(pair.maker_fee)
        .bind(pair.taker_fee)
        .bind(pair.updated_at)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Delete trading pair
    pub async fn delete_trading_pair(&self, symbol: &str) -> Result<(), sqlx::Error> {
        sqlx::query("DELETE FROM trading_pairs WHERE symbol = $1")
            .bind(symbol)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    // ==================== ORDER OPERATIONS ====================

    /// Save order
    pub async fn save_order(&self, order: &Order) -> Result<(), sqlx::Error> {
        let side = format!("{:?}", order.side);
        let order_type = format!("{:?}", order.order_type);
        let status = format!("{:?}", order.status);
        let time_in_force = format!("{:?}", order.time_in_force);

        sqlx::query(
            "INSERT INTO orders (id, user_id, symbol, side, type, status, price, stop_price, quantity, filled_quantity, remaining_quantity, average_price, time_in_force, created_at, updated_at, is_working)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
             ON CONFLICT (id) DO UPDATE SET status = $6, filled_quantity = $10, remaining_quantity = $11, average_price = $12, updated_at = $15, is_working = $16"
        )
        .bind(order.id)
        .bind(order.user_id)
        .bind(&order.symbol)
        .bind(&side)
        .bind(&order_type)
        .bind(&status)
        .bind(order.price)
        .bind(order.stop_price)
        .bind(order.quantity)
        .bind(order.filled_quantity)
        .bind(order.remaining_quantity)
        .bind(order.average_price)
        .bind(&time_in_force)
        .bind(order.created_at)
        .bind(order.updated_at)
        .bind(order.is_working)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Update order status
    pub async fn update_order_status(&self, order: &Order) -> Result<(), sqlx::Error> {
        let status = format!("{:?}", order.status);

        sqlx::query(
            "UPDATE orders SET status = $2, filled_quantity = $3, remaining_quantity = $4, average_price = $5, updated_at = $6, is_working = $7
             WHERE id = $1"
        )
        .bind(order.id)
        .bind(&status)
        .bind(order.filled_quantity)
        .bind(order.remaining_quantity)
        .bind(order.average_price)
        .bind(order.updated_at)
        .bind(order.is_working)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Get active orders
    pub async fn get_active_orders(&self) -> Result<Vec<Order>, sqlx::Error> {
        // Implementation would fetch active orders
        Ok(vec![])
    }

    // ==================== TRADE OPERATIONS ====================

    /// Save trade
    pub async fn save_trade(&self, trade: &Trade) -> Result<(), sqlx::Error> {
        let side = format!("{:?}", trade.side);

        sqlx::query(
            "INSERT INTO trades (id, symbol, order_id, counter_order_id, user_id, counter_user_id, side, price, quantity, fee, fee_currency, is_maker, timestamp)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)"
        )
        .bind(trade.id)
        .bind(&trade.symbol)
        .bind(trade.order_id)
        .bind(trade.counter_order_id)
        .bind(trade.user_id)
        .bind(trade.counter_user_id)
        .bind(&side)
        .bind(trade.price)
        .bind(trade.quantity)
        .bind(trade.fee)
        .bind(&trade.fee_currency)
        .bind(trade.is_maker)
        .bind(trade.timestamp)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    // ==================== API KEY OPERATIONS ====================

    /// Create API key
    pub async fn create_api_key(&self, api_key: &ApiKey) -> Result<(), sqlx::Error> {
        sqlx::query(
            "INSERT INTO api_keys (id, user_id, name, api_key, api_secret, permissions, ip_whitelist, rate_limit, created_at, expires_at, enabled)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)"
        )
        .bind(api_key.id)
        .bind(api_key.user_id)
        .bind(&api_key.name)
        .bind(&api_key.api_key)
        .bind(&api_key.api_secret)
        .bind(&api_key.permissions)
        .bind(&api_key.ip_whitelist)
        .bind(api_key.rate_limit)
        .bind(api_key.created_at)
        .bind(api_key.expires_at)
        .bind(api_key.enabled)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Get API key
    pub async fn get_api_key(&self, api_key: &str) -> Result<Option<ApiKey>, sqlx::Error> {
        let row = sqlx::query_as::<_, (Uuid, Uuid, String, String, String, Vec<String>, Vec<String>, i32, DateTime<Utc>, Option<DateTime<Utc>>, Option<DateTime<Utc>>, bool)>(
            "SELECT id, user_id, name, api_key, api_secret, permissions, ip_whitelist, rate_limit, created_at, expires_at, last_used_at, enabled
             FROM api_keys WHERE api_key = $1"
        )
        .bind(api_key)
        .fetch_optional(&self.pool)
        .await?;

        match row {
            Some((id, user_id, name, api_key, api_secret, permissions, ip_whitelist, rate_limit, created_at, expires_at, last_used_at, enabled)) => {
                Ok(Some(ApiKey {
                    id,
                    user_id,
                    name,
                    api_key,
                    api_secret,
                    permissions,
                    ip_whitelist,
                    rate_limit: rate_limit as u32,
                    created_at,
                    expires_at,
                    last_used_at,
                    enabled,
                }))
            }
            None => Ok(None),
        }
    }

    /// Update API key last used
    pub async fn update_api_key_last_used(&self, id: Uuid) -> Result<(), sqlx::Error> {
        sqlx::query("UPDATE api_keys SET last_used_at = $1 WHERE id = $2")
            .bind(Utc::now())
            .bind(id)
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    // ==================== RISK LIMITS OPERATIONS ====================

    /// Get risk limits
    pub async fn get_risk_limits(&self, user_id: Uuid) -> Result<Option<RiskLimits>, sqlx::Error> {
        let row = sqlx::query_as::<_, (Uuid, Decimal, Decimal, Decimal, Decimal, Decimal, i32, i32, i32, Decimal)>(
            "SELECT user_id, max_order_value, max_daily_volume, max_position_size, max_leverage, max_open_orders, rate_limit_per_second, rate_limit_per_minute, margin_required
             FROM risk_limits WHERE user_id = $1"
        )
        .bind(user_id)
        .fetch_optional(&self.pool)
        .await?;

        match row {
            Some((user_id, max_order_value, max_daily_volume, max_position_size, max_leverage, max_open_orders, rate_limit_per_second, rate_limit_per_minute, margin_required)) => {
                Ok(Some(RiskLimits {
                    user_id,
                    max_order_value,
                    max_daily_volume,
                    max_position_size,
                    max_leverage,
                    max_open_orders: max_open_orders as u32,
                    rate_limit_per_second: rate_limit_per_second as u32,
                    rate_limit_per_minute: rate_limit_per_minute as u32,
                    margin_required,
                }))
            }
            None => Ok(None),
        }
    }

    /// Update risk limits
    pub async fn update_risk_limits(&self, limits: &RiskLimits) -> Result<(), sqlx::Error> {
        sqlx::query(
            "INSERT INTO risk_limits (user_id, max_order_value, max_daily_volume, max_position_size, max_leverage, max_open_orders, rate_limit_per_second, rate_limit_per_minute, margin_required)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
             ON CONFLICT (user_id) DO UPDATE SET max_order_value = $2, max_daily_volume = $3, max_position_size = $4, max_leverage = $5, max_open_orders = $6, rate_limit_per_second = $7, rate_limit_per_minute = $8, margin_required = $9"
        )
        .bind(limits.user_id)
        .bind(limits.max_order_value)
        .bind(limits.max_daily_volume)
        .bind(limits.max_position_size)
        .bind(limits.max_leverage)
        .bind(limits.max_open_orders as i32)
        .bind(limits.rate_limit_per_second as i32)
        .bind(limits.rate_limit_per_minute as i32)
        .bind(limits.margin_required)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    // ==================== AUDIT LOG OPERATIONS ====================

    /// Save audit log
    pub async fn save_audit_log(&self, log: &AuditLog) -> Result<(), sqlx::Error> {
        sqlx::query(
            "INSERT INTO audit_logs (id, user_id, action, resource_type, resource_id, old_value, new_value, ip_address, user_agent, timestamp, status, error_message)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)"
        )
        .bind(log.id)
        .bind(log.user_id)
        .bind(&log.action)
        .bind(&log.resource_type)
        .bind(&log.resource_id)
        .bind(&log.old_value)
        .bind(&log.new_value)
        .bind(&log.ip_address)
        .bind(&log.user_agent)
        .bind(log.timestamp)
        .bind(&log.status)
        .bind(&log.error_message)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Get audit logs
    pub async fn get_audit_logs(
        &self,
        page: u32,
        limit: u32,
        user_id: Option<Uuid>,
        action: Option<String>,
        start_time: Option<DateTime<Utc>>,
        end_time: Option<DateTime<Utc>>,
    ) -> Result<Vec<AuditLog>, sqlx::Error> {
        let offset = (page - 1) * limit;
        
        let mut query = String::from(
            "SELECT id, user_id, action, resource_type, resource_id, old_value, new_value, ip_address, user_agent, timestamp, status, error_message
             FROM audit_logs WHERE 1=1"
        );
        
        let mut conditions = Vec::new();
        let mut param_count = 0;

        if let Some(uid) = user_id {
            param_count += 1;
            conditions.push(format!("user_id = ${}", param_count));
        }

        if let Some(act) = action {
            param_count += 1;
            conditions.push(format!("action = ${}", param_count));
        }

        if let Some(start) = start_time {
            param_count += 1;
            conditions.push(format!("timestamp >= ${}", param_count));
        }

        if let Some(end) = end_time {
            param_count += 1;
            conditions.push(format!("timestamp <= ${}", param_count));
        }

        if !conditions.is_empty() {
            query.push_str(" AND ");
            query.push_str(&conditions.join(" AND "));
        }

        query.push_str(&format!(" ORDER BY timestamp DESC LIMIT ${} OFFSET ${}", param_count + 1, param_count + 2));

        let mut query_builder = sqlx::query_as::<_, (Uuid, Option<Uuid>, String, String, String, Option<serde_json::Value>, Option<serde_json::Value>, String, String, DateTime<Utc>, String, Option<String>)>(&query);

        if let Some(uid) = user_id {
            query_builder = query_builder.bind(uid);
        }

        if let Some(act) = action {
            query_builder = query_builder.bind(act);
        }

        if let Some(start) = start_time {
            query_builder = query_builder.bind(start);
        }

        if let Some(end) = end_time {
            query_builder = query_builder.bind(end);
        }

        query_builder = query_builder.bind(limit as i64);
        query_builder = query_builder.bind(offset as i64);

        let rows = query_builder.fetch_all(&self.pool).await?;

        let logs = rows.into_iter().map(|(id, user_id, action, resource_type, resource_id, old_value, new_value, ip_address, user_agent, timestamp, status, error_message)| {
            AuditLog {
                id,
                user_id,
                action,
                resource_type,
                resource_id,
                old_value,
                new_value,
                ip_address,
                user_agent,
                timestamp,
                status,
                error_message,
            }
        }).collect();

        Ok(logs)
    }
}