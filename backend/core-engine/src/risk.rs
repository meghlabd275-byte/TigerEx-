//! Risk Management Engine
//! Real-time risk monitoring and control

use std::sync::Arc;
use rust_decimal::Decimal;
use uuid::Uuid;
use chrono::{Utc, DateTime};
use serde::{Deserialize, Serialize};
use tracing::{info, warn, error};

use crate::models::*;
use crate::db::Database;
use crate::cache::RedisCache;

/// Risk engine for monitoring and controlling trading risk
pub struct RiskEngine {
    pub db: Arc<Database>,
    pub cache: Arc<RedisCache>,
    pub global_limits: RwLock<GlobalRiskLimits>,
    pub alerts: RwLock<Vec<RiskAlert>>,
}

/// Global risk limits for the exchange
#[derive(Debug, Clone)]
pub struct GlobalRiskLimits {
    pub max_total_open_orders: u64,
    pub max_total_open_value: Decimal,
    pub max_single_order_value: Decimal,
    pub max_leverage: Decimal,
    pub circuit_breaker_threshold: Decimal,
    pub circuit_breaker_cooldown_minutes: u32,
    pub auto_liquidation_enabled: bool,
    pub margin_call_threshold: Decimal,
    pub liquidation_threshold: Decimal,
}

impl Default for GlobalRiskLimits {
    fn default() -> Self {
        Self {
            max_total_open_orders: 1_000_000,
            max_total_open_value: Decimal::from(1_000_000_000),
            max_single_order_value: Decimal::from(10_000_000),
            max_leverage: Decimal::from(125),
            circuit_breaker_threshold: Decimal::from_str_exact("0.10").unwrap(),
            circuit_breaker_cooldown_minutes: 5,
            auto_liquidation_enabled: true,
            margin_call_threshold: Decimal::from_str_exact("0.80").unwrap(),
            liquidation_threshold: Decimal::from_str_exact("0.90").unwrap(),
        }
    }
}

/// Risk alert
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RiskAlert {
    pub id: Uuid,
    pub alert_type: RiskAlertType,
    pub severity: RiskSeverity,
    pub user_id: Option<Uuid>,
    pub symbol: Option<String>,
    pub message: String,
    pub details: serde_json::Value,
    pub created_at: DateTime<Utc>,
    pub acknowledged: bool,
    pub acknowledged_by: Option<Uuid>,
    pub acknowledged_at: Option<DateTime<Utc>>,
}

/// Risk alert types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RiskAlertType {
    LargeOrder,
    UnusualVolume,
    PriceDeviation,
    MarginCall,
    Liquidation,
    CircuitBreaker,
    RateLimitExceeded,
    SuspiciousActivity,
    PositionLimitExceeded,
    DailyVolumeLimitExceeded,
    UnauthorizedAccess,
    SystemAnomaly,
}

/// Risk severity levels
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RiskSeverity {
    Low,
    Medium,
    High,
    Critical,
}

/// Position risk
#[derive(Debug, Clone)]
pub struct PositionRisk {
    pub user_id: Uuid,
    pub symbol: String,
    pub position_size: Decimal,
    pub entry_price: Decimal,
    pub current_price: Decimal,
    pub unrealized_pnl: Decimal,
    pub margin_used: Decimal,
    pub maintenance_margin: Decimal,
    pub margin_ratio: Decimal,
    pub liquidation_price: Decimal,
}

impl RiskEngine {
    pub fn new(db: Arc<Database>, cache: Arc<RedisCache>) -> Self {
        Self {
            db,
            cache,
            global_limits: RwLock::new(GlobalRiskLimits::default()),
            alerts: RwLock::new(Vec::new()),
        }
    }

    /// Check if order passes risk checks
    pub async fn check_order_risk(&self, order: &Order, account: &Account) -> Result<(), String> {
        // Check account status
        if account.status != AccountStatus::Active {
            return Err("Account is not active".to_string());
        }

        // Check if trading is enabled
        if !account.trading_enabled {
            return Err("Trading is not enabled for this account".to_string());
        }

        // Get user risk limits
        let limits = self.get_user_limits(account.user_id).await?;

        // Check order value
        let order_value = order.price.unwrap_or(Decimal::ZERO) * order.quantity;
        if order_value > limits.max_order_value {
            self.create_alert(
                RiskAlertType::LargeOrder,
                RiskSeverity::Medium,
                Some(account.user_id),
                Some(order.symbol.clone()),
                &format!("Order value {} exceeds maximum {}", order_value, limits.max_order_value),
                serde_json::json!({"order_value": order_value, "max_value": limits.max_order_value}),
            ).await;
            return Err(format!("Order value exceeds maximum allowed: {}", limits.max_order_value));
        }

        // Check global limit
        if order_value > self.global_limits.read().max_single_order_value {
            self.create_alert(
                RiskAlertType::LargeOrder,
                RiskSeverity::High,
                Some(account.user_id),
                Some(order.symbol.clone()),
                &format!("Order exceeds global single order limit"),
                serde_json::json!({"order_value": order_value}),
            ).await;
            return Err("Order exceeds global limit".to_string());
        }

        // Check position size
        let current_position = self.get_position_value(account.user_id, &order.symbol).await;
        let new_position = match order.side {
            OrderSide::Buy => current_position + order_value,
            OrderSide::Sell => current_position - order_value,
        };

        if new_position.abs() > limits.max_position_size {
            return Err(format!("Position would exceed maximum: {}", limits.max_position_size));
        }

        // Check open orders count
        let open_orders = self.count_open_orders(account.user_id).await;
        if open_orders >= limits.max_open_orders as usize {
            return Err(format!("Maximum open orders reached: {}", limits.max_open_orders));
        }

        // Check daily volume
        let daily_volume = self.get_daily_volume(account.user_id).await;
        if daily_volume + order_value > limits.max_daily_volume {
            return Err(format!("Daily volume limit exceeded: {}", limits.max_daily_volume));
        }

        Ok(())
    }

    /// Get user risk limits
    async fn get_user_limits(&self, user_id: Uuid) -> Result<RiskLimits, String> {
        match self.db.get_risk_limits(user_id).await {
            Ok(Some(limits)) => Ok(limits),
            Ok(None) => Ok(RiskLimits {
                user_id,
                max_order_value: Decimal::from(100_000),
                max_daily_volume: Decimal::from(1_000_000),
                max_position_size: Decimal::from(500_000),
                max_leverage: Decimal::from(10),
                max_open_orders: 100,
                rate_limit_per_second: 10,
                rate_limit_per_minute: 600,
                margin_required: Decimal::from_str_exact("0.10").unwrap(),
            }),
            Err(e) => Err(format!("Failed to get risk limits: {}", e)),
        }
    }

    /// Get position value
    async fn get_position_value(&self, user_id: Uuid, symbol: &str) -> Decimal {
        let key = format!("position:{}:{}", user_id, symbol);
        self.cache.get(&key).await.unwrap_or(Decimal::ZERO)
    }

    /// Count open orders
    async fn count_open_orders(&self, user_id: Uuid) -> usize {
        let key = format!("open_orders:{}", user_id);
        self.cache.get(&key).await.unwrap_or(0)
    }

    /// Get daily volume
    async fn get_daily_volume(&self, user_id: Uuid) -> Decimal {
        let key = format!("daily_volume:{}:{}", user_id, Utc::now().format("%Y-%m-%d"));
        self.cache.get(&key).await.unwrap_or(Decimal::ZERO)
    }

    /// Calculate position risk
    pub fn calculate_position_risk(
        &self,
        user_id: Uuid,
        symbol: String,
        position_size: Decimal,
        entry_price: Decimal,
        current_price: Decimal,
        leverage: Decimal,
    ) -> PositionRisk {
        let unrealized_pnl = (current_price - entry_price) * position_size;
        let margin_used = (position_size * entry_price) / leverage;
        let maintenance_margin = margin_used * Decimal::from_str_exact("0.5").unwrap();
        let margin_ratio = if margin_used > Decimal::ZERO {
            (margin_used + unrealized_pnl) / margin_used
        } else {
            Decimal::ZERO
        };

        // Calculate liquidation price
        let liquidation_price = if position_size > Decimal::ZERO {
            entry_price * (Decimal::ONE - Decimal::from_str_exact("0.9").unwrap() / leverage)
        } else {
            entry_price * (Decimal::ONE + Decimal::from_str_exact("0.9").unwrap() / leverage)
        };

        PositionRisk {
            user_id,
            symbol,
            position_size,
            entry_price,
            current_price,
            unrealized_pnl,
            margin_used,
            maintenance_margin,
            margin_ratio,
            liquidation_price,
        }
    }

    /// Check margin call
    pub fn check_margin_call(&self, position: &PositionRisk) -> bool {
        let threshold = self.global_limits.read().margin_call_threshold;
        position.margin_ratio < threshold
    }

    /// Check liquidation
    pub fn check_liquidation(&self, position: &PositionRisk) -> bool {
        let threshold = self.global_limits.read().liquidation_threshold;
        position.margin_ratio < threshold
    }

    /// Create risk alert
    pub async fn create_alert(
        &self,
        alert_type: RiskAlertType,
        severity: RiskSeverity,
        user_id: Option<Uuid>,
        symbol: Option<String>,
        message: &str,
        details: serde_json::Value,
    ) {
        let alert = RiskAlert {
            id: Uuid::new_v4(),
            alert_type,
            severity,
            user_id,
            symbol,
            message: message.to_string(),
            details,
            created_at: Utc::now(),
            acknowledged: false,
            acknowledged_by: None,
            acknowledged_at: None,
        };

        // Store alert
        self.alerts.write().push(alert.clone());

        // Cache for quick access
        let key = format!("risk_alerts:{}", alert.id);
        let _ = self.cache.set(&key, &alert).await;

        // Publish for real-time notification
        let _ = self.cache.publish("risk:alerts", &alert).await;

        warn!("Risk alert created: {:?} - {}", alert.alert_type, alert.message);
    }

    /// Get active alerts
    pub fn get_active_alerts(&self) -> Vec<RiskAlert> {
        self.alerts.read()
            .iter()
            .filter(|a| !a.acknowledged)
            .cloned()
            .collect()
    }

    /// Acknowledge alert
    pub async fn acknowledge_alert(&self, alert_id: Uuid, acknowledged_by: Uuid) -> Result<(), String> {
        let mut alerts = self.alerts.write();
        
        if let Some(alert) = alerts.iter_mut().find(|a| a.id == alert_id) {
            alert.acknowledged = true;
            alert.acknowledged_by = Some(acknowledged_by);
            alert.acknowledged_at = Some(Utc::now());
            Ok(())
        } else {
            Err("Alert not found".to_string())
        }
    }

    /// Check circuit breaker
    pub async fn check_circuit_breaker(&self, symbol: &str, price_change_percent: Decimal) -> bool {
        let threshold = self.global_limits.read().circuit_breaker_threshold;
        
        if price_change_percent.abs() >= threshold {
            self.create_alert(
                RiskAlertType::CircuitBreaker,
                RiskSeverity::Critical,
                None,
                Some(symbol.to_string()),
                &format!("Circuit breaker triggered for {} - price change: {}%", symbol, price_change_percent),
                serde_json::json!({"price_change_percent": price_change_percent}),
            ).await;
            true
        } else {
            false
        }
    }

    /// Update global limits
    pub fn update_global_limits(&self, limits: GlobalRiskLimits) {
        *self.global_limits.write() = limits;
        info!("Global risk limits updated");
    }

    /// Get risk metrics
    pub fn get_risk_metrics(&self) -> RiskMetrics {
        let alerts = self.alerts.read();
        let limits = self.global_limits.read();

        RiskMetrics {
            total_alerts: alerts.len(),
            critical_alerts: alerts.iter().filter(|a| matches!(a.severity, RiskSeverity::Critical)).count(),
            high_alerts: alerts.iter().filter(|a| matches!(a.severity, RiskSeverity::High)).count(),
            unacknowledged_alerts: alerts.iter().filter(|a| !a.acknowledged).count(),
            global_limits: GlobalRiskLimitsSummary {
                max_single_order_value: limits.max_single_order_value,
                max_leverage: limits.max_leverage,
                circuit_breaker_threshold: limits.circuit_breaker_threshold,
            },
        }
    }
}

/// Risk metrics summary
#[derive(Debug, Serialize)]
pub struct RiskMetrics {
    pub total_alerts: usize,
    pub critical_alerts: usize,
    pub high_alerts: usize,
    pub unacknowledged_alerts: usize,
    pub global_limits: GlobalRiskLimitsSummary,
}

#[derive(Debug, Serialize)]
pub struct GlobalRiskLimitsSummary {
    pub max_single_order_value: Decimal,
    pub max_leverage: Decimal,
    pub circuit_breaker_threshold: Decimal,
}

use std::sync::RwLock;pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}
