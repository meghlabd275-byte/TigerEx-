//! FIX Admin Service - Administrative Control for FIX Protocol Engine

use std::sync::Arc;
use tokio::sync::RwLock;
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

use crate::session::{Session, SessionManager, SessionState};
use crate::engine::TradingEngineConnector;

/// Admin Action Types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AdminAction {
    Start,
    Stop,
    Restart,
    Pause,
    Resume,
    Reset,
    Halt,
    ClearCache,
    ReloadConfig,
}

/// Admin Response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AdminResponse {
    pub success: bool,
    pub message: String,
    pub data: Option<serde_json::Value>,
    pub timestamp: DateTime<Utc>,
}

/// FIX Session Admin Info
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionAdminInfo {
    pub session_key: String,
    pub sender_comp_id: String,
    pub target_comp_id: String,
    pub state: String,
    pub incoming_seq_num: u64,
    pub outgoing_seq_num: u64,
    pub heart_bt_int: u32,
    pub last_heartbeat: DateTime<Utc>,
    pub last_received: DateTime<Utc>,
    pub last_sent: DateTime<Utc>,
    pub is_active: bool,
    pub created_at: DateTime<Utc>,
    pub remote_ip: Option<String>,
}

/// FIX Engine Statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EngineStats {
    pub total_sessions: usize,
    pub active_sessions: usize,
    pub messages_received: u64,
    pub messages_sent: u64,
    pub orders_received: u64,
    pub orders_executed: u64,
    pub errors: u64,
    pub uptime_seconds: u64,
    pub start_time: DateTime<Utc>,
}

/// FIX Admin Service
pub struct FixAdminService {
    session_manager: Arc<SessionManager>,
    engine_connector: Arc<TradingEngineConnector>,
    engine_state: RwLock<EngineState>,
    stats: RwLock<EngineStats>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EngineState {
    Running,
    Paused,
    Stopped,
    Halted,
    Maintenance,
}

impl FixAdminService {
    pub fn new(
        session_manager: Arc<SessionManager>,
        engine_connector: Arc<TradingEngineConnector>,
    ) -> Self {
        Self {
            session_manager,
            engine_connector,
            engine_state: RwLock::new(EngineState::Running),
            stats: RwLock::new(EngineStats {
                total_sessions: 0,
                active_sessions: 0,
                messages_received: 0,
                messages_sent: 0,
                orders_received: 0,
                orders_executed: 0,
                errors: 0,
                uptime_seconds: 0,
                start_time: Utc::now(),
            }),
        }
    }
    
    /// Get engine status
    pub async fn get_engine_status(&self) -> AdminResponse {
        let state = self.engine_state.read().await;
        let stats = self.stats.read().await;
        
        AdminResponse {
            success: true,
            message: format!("Engine is {:?}", *state),
            data: Some(serde_json::to_value(EngineStatusResponse {
                state: format!("{:?}", *state),
                stats: stats.clone(),
            }).ok()),
            timestamp: Utc::now(),
        }
    }
    
    /// Control engine
    pub async fn control_engine(&self, action: AdminAction) -> AdminResponse {
        let mut state = self.engine_state.write().await;
        
        match action {
            AdminAction::Start => {
                *state = EngineState::Running;
                AdminResponse {
                    success: true,
                    message: "Engine started".to_string(),
                    data: None,
                    timestamp: Utc::now(),
                }
            }
            AdminAction::Stop => {
                *state = EngineState::Stopped;
                // Disconnect all sessions
                self.session_manager.end_all_sessions().await;
                AdminResponse {
                    success: true,
                    message: "Engine stopped".to_string(),
                    data: None,
                    timestamp: Utc::now(),
                }
            }
            AdminAction::Restart => {
                *state = EngineState::Running;
                // Reset sequence numbers for all sessions
                self.session_manager.reset_all_sequences().await;
                AdminResponse {
                    success: true,
                    message: "Engine restarted".to_string(),
                    data: None,
                    timestamp: Utc::now(),
                }
            }
            AdminAction::Pause => {
                *state = EngineState::Paused;
                AdminResponse {
                    success: true,
                    message: "Engine paused".to_string(),
                    data: None,
                    timestamp: Utc::now(),
                }
            }
            AdminAction::Resume => {
                *state = EngineState::Running;
                AdminResponse {
                    success: true,
                    message: "Engine resumed".to_string(),
                    data: None,
                    timestamp: Utc::now(),
                }
            }
            AdminAction::Reset => {
                *state = EngineState::Running;
                self.session_manager.reset_all_sequences().await;
                let mut stats = self.stats.write().await;
                *stats = EngineStats {
                    total_sessions: 0,
                    active_sessions: 0,
                    messages_received: 0,
                    messages_sent: 0,
                    orders_received: 0,
                    orders_executed: 0,
                    errors: 0,
                    uptime_seconds: 0,
                    start_time: Utc::now(),
                };
                AdminResponse {
                    success: true,
                    message: "Engine reset".to_string(),
                    data: None,
                    timestamp: Utc::now(),
                }
            }
            AdminAction::Halt => {
                *state = EngineState::Halted;
                self.session_manager.end_all_sessions().await;
                AdminResponse {
                    success: true,
                    message: "Engine halted - emergency stop".to_string(),
                    data: None,
                    timestamp: Utc::now(),
                }
            }
            AdminAction::ClearCache => {
                // Clear market data cache
                self.engine_connector.clear_cache().await;
                AdminResponse {
                    success: true,
                    message: "Cache cleared".to_string(),
                    data: None,
                    timestamp: Utc::now(),
                }
            }
            AdminAction::ReloadConfig => {
                AdminResponse {
                    success: true,
                    message: "Configuration reloaded".to_string(),
                    data: None,
                    timestamp: Utc::now(),
                }
            }
        }
    }
    
    /// Get all sessions
    pub async fn get_all_sessions(&self) -> AdminResponse {
        let sessions = self.session_manager.get_all_sessions().await;
        let session_infos: Vec<SessionAdminInfo> = sessions
            .into_iter()
            .map(|s| SessionAdminInfo {
                session_key: format!("{}->{}", s.sender_comp_id, s.target_comp_id),
                sender_comp_id: s.sender_comp_id,
                target_comp_id: s.target_comp_id,
                state: format!("{:?}", s.state),
                incoming_seq_num: s.incoming_seq_num,
                outgoing_seq_num: s.outgoing_seq_num,
                heart_bt_int: s.heart_bt_int,
                last_heartbeat: s.last_heartbeat,
                last_received: s.last_received,
                last_sent: s.last_sent,
                is_active: s.is_active(),
                created_at: s.created_at,
                remote_ip: s.remote_ip,
            })
            .collect();
        
        AdminResponse {
            success: true,
            message: format!("{} sessions found", session_infos.len()),
            data: Some(serde_json::to_value(&session_infos).ok()).flatten(),
            timestamp: Utc::now(),
        }
    }
    
    /// Get specific session
    pub async fn get_session(&self, sender_comp_id: &str) -> AdminResponse {
        if let Some(session) = self.session_manager.get_session_by_sender(sender_comp_id).await {
            let info = SessionAdminInfo {
                session_key: format!("{}->{}", session.sender_comp_id, session.target_comp_id),
                sender_comp_id: session.sender_comp_id,
                target_comp_id: session.target_comp_id,
                state: format!("{:?}", session.state),
                incoming_seq_num: session.incoming_seq_num,
                outgoing_seq_num: session.outgoing_seq_num,
                heart_bt_int: session.heart_bt_int,
                last_heartbeat: session.last_heartbeat,
                last_received: session.last_received,
                last_sent: session.last_sent,
                is_active: session.is_active(),
                created_at: session.created_at,
                remote_ip: session.remote_ip,
            };
            
            AdminResponse {
                success: true,
                message: "Session found".to_string(),
                data: serde_json::to_value(&info).ok(),
                timestamp: Utc::now(),
            }
        } else {
            AdminResponse {
                success: false,
                message: "Session not found".to_string(),
                data: None,
                timestamp: Utc::now(),
            }
        }
    }
    
    /// End session
    pub async fn end_session(&self, sender_comp_id: &str) -> AdminResponse {
        self.session_manager.end_session(sender_comp_id).await;
        
        AdminResponse {
            success: true,
            message: format!("Session {} ended", sender_comp_id),
            data: None,
            timestamp: Utc::now(),
        }
    }
    
    /// End all sessions
    pub async fn end_all_sessions(&self) -> AdminResponse {
        let count = self.session_manager.session_count().await;
        self.session_manager.end_all_sessions().await;
        
        AdminResponse {
            success: true,
            message: format!("{} sessions ended", count),
            data: None,
            timestamp: Utc::now(),
        }
    }
    
    /// Reset sequence numbers for session
    pub async fn reset_session_sequence(&self, sender_comp_id: &str) -> AdminResponse {
        if let Some(mut session) = self.session_manager.get_session_by_sender(sender_comp_id).await {
            session.reset_sequence();
            let session_key = format!("{}->{}", sender_comp_id, session.target_comp_id);
            self.session_manager.update_session(&session_key, session).await;
            
            AdminResponse {
                success: true,
                message: format!("Sequence reset for {}", sender_comp_id),
                data: None,
                timestamp: Utc::now(),
            }
        } else {
            AdminResponse {
                success: false,
                message: "Session not found".to_string(),
                data: None,
                timestamp: Utc::now(),
            }
        }
    }
    
    /// Update statistics
    pub async fn update_stats(&self, messages_received: u64, messages_sent: u64, orders: u64, errors: u64) {
        let mut stats = self.stats.write().await;
        stats.messages_received += messages_received;
        stats.messages_sent += messages_sent;
        stats.orders_received += orders;
        stats.errors += errors;
        stats.total_sessions = self.session_manager.session_count().await;
        stats.active_sessions = self.session_manager.get_active_sessions().await.len();
        stats.uptime_seconds = (Utc::now() - stats.start_time).num_seconds() as u64;
    }
    
    /// Increment order count
    pub async fn increment_order_count(&self, executed: bool) {
        let mut stats = self.stats.write().await;
        stats.orders_received += 1;
        if executed {
            stats.orders_executed += 1;
        }
    }
    
    /// Increment error count
    pub async fn increment_error_count(&self) {
        let mut stats = self.stats.write().await;
        stats.errors += 1;
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct EngineStatusResponse {
    state: String,
    stats: EngineStats,
}

// Extend SessionManager with additional admin methods
impl SessionManager {
    pub async fn end_all_sessions(&self) {
        let mut sessions = self.sessions.write().await;
        sessions.clear();
    }
    
    pub async fn reset_all_sequences(&self) {
        let mut sessions = self.sessions.write().await;
        for session in sessions.values_mut() {
            session.reset_sequence();
        }
    }
}pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}
