//! FIX Session Management

use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// FIX Session State
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SessionState {
    Disconnected,
    Connected,
    LogonReceived,
    LogonSent,
    Active,
    LogoutReceived,
    LogoutSent,
    WaitingForResend,
    PendingTimeout,
}

/// FIX Session Information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Session {
    pub sender_comp_id: String,
    pub target_comp_id: String,
    pub state: SessionState,
    pub incoming_seq_num: u64,
    pub outgoing_seq_num: u64,
    pub heart_bt_int: u32,
    pub last_heartbeat: DateTime<Utc>,
    pub last_received: DateTime<Utc>,
    pub last_sent: DateTime<Utc>,
    pub username: Option<String>,
    pub password: Option<String>,
    pub encrypt_method: u8,
    pub reset_seq_num_flag: bool,
    pub test_req_id: Option<String>,
    pub pending_test_req: bool,
    pub test_req_sent_time: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub remote_ip: Option<String>,
    pub remote_port: Option<u16>,
    pub session_qualifier: Option<String>,
    pub default_appl_ver_id: Option<String>,
}

impl Session {
    pub fn new(sender_comp_id: String, target_comp_id: String, heart_bt_int: u32) -> Self {
        Self {
            sender_comp_id,
            target_comp_id,
            state: SessionState::Connected,
            incoming_seq_num: 1,
            outgoing_seq_num: 1,
            heart_bt_int,
            last_heartbeat: Utc::now(),
            last_received: Utc::now(),
            last_sent: Utc::now(),
            username: None,
            password: None,
            encrypt_method: 0,
            reset_seq_num_flag: false,
            test_req_id: None,
            pending_test_req: false,
            test_req_sent_time: None,
            created_at: Utc::now(),
            updated_at: Utc::now(),
            remote_ip: None,
            remote_port: None,
            session_qualifier: None,
            default_appl_ver_id: None,
        }
    }
    
    pub fn is_active(&self) -> bool {
        matches!(self.state, SessionState::Active)
    }
    
    pub fn next_incoming_seq(&mut self) -> u64 {
        let seq = self.incoming_seq_num;
        self.incoming_seq_num += 1;
        self.updated_at = Utc::now();
        seq
    }
    
    pub fn next_outgoing_seq(&mut self) -> u64 {
        let seq = self.outgoing_seq_num;
        self.outgoing_seq_num += 1;
        self.updated_at = Utc::now();
        seq
    }
    
    pub fn set_state(&mut self, state: SessionState) {
        self.state = state;
        self.updated_at = Utc::now();
    }
    
    pub fn update_heartbeat(&mut self) {
        self.last_heartbeat = Utc::now();
        self.updated_at = Utc::now();
    }
    
    pub fn update_received(&mut self) {
        self.last_received = Utc::now();
        self.updated_at = Utc::now();
    }
    
    pub fn update_sent(&mut self) {
        self.last_sent = Utc::now();
        self.updated_at = Utc::now();
    }
    
    pub fn reset_sequence(&mut self) {
        self.incoming_seq_num = 1;
        self.outgoing_seq_num = 1;
        self.updated_at = Utc::now();
    }
    
    pub fn set_test_request_pending(&mut self, test_req_id: String) {
        self.test_req_id = Some(test_req_id);
        self.pending_test_req = true;
        self.test_req_sent_time = Some(Utc::now());
    }
    
    pub fn clear_test_request(&mut self) {
        self.test_req_id = None;
        self.pending_test_req = false;
        self.test_req_sent_time = None;
    }
}

/// Session Manager
pub struct SessionManager {
    sessions: RwLock<HashMap<String, Session>>,
    credentials: RwLock<HashMap<String, Credential>>,
    max_sessions: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Credential {
    pub sender_comp_id: String,
    pub username: String,
    pub password_hash: String,
    pub role: String,
    pub permissions: Vec<String>,
    pub enabled: bool,
    pub created_at: DateTime<Utc>,
    pub last_login: Option<DateTime<Utc>>,
}

impl SessionManager {
    pub fn new(max_sessions: usize) -> Self {
        Self {
            sessions: RwLock::new(HashMap::new()),
            credentials: RwLock::new(HashMap::new()),
            max_sessions,
        }
    }
    
    pub async fn add_credential(&self, credential: Credential) {
        let mut creds = self.credentials.write().await;
        creds.insert(credential.sender_comp_id.clone(), credential);
    }
    
    pub async fn authenticate(
        &self,
        sender_comp_id: &str,
        username: Option<&str>,
        password: Option<&str>,
    ) -> bool {
        let creds = self.credentials.read().await;
        
        if let Some(cred) = creds.get(sender_comp_id) {
            if !cred.enabled {
                return false;
            }
            
            // Check username if provided
            if let Some(user) = username {
                if user != cred.username {
                    return false;
                }
            }
            
            // Check password if provided (in production, use proper password hashing)
            if let Some(pass) = password {
                // TODO: Use proper password verification
                if pass != cred.password_hash {
                    return false;
                }
            }
            
            return true;
        }
        
        // Allow authentication without stored credentials for development
        // In production, this should return false
        true
    }
    
    pub async fn create_session(
        &self,
        sender_comp_id: String,
        target_comp_id: String,
        heart_bt_int: u32,
    ) -> String {
        let session_key = format!("{}->{}", sender_comp_id, target_comp_id);
        let session = Session::new(sender_comp_id, target_comp_id, heart_bt_int);
        
        let mut sessions = self.sessions.write().await;
        sessions.insert(session_key.clone(), session);
        
        session_key
    }
    
    pub async fn get_session(&self, session_key: &str) -> Option<Session> {
        let sessions = self.sessions.read().await;
        sessions.get(session_key).cloned()
    }
    
    pub async fn get_session_by_sender(&self, sender_comp_id: &str) -> Option<Session> {
        let sessions = self.sessions.read().await;
        sessions.values()
            .find(|s| s.sender_comp_id == sender_comp_id)
            .cloned()
    }
    
    pub async fn update_session(&self, session_key: &str, session: Session) {
        let mut sessions = self.sessions.write().await;
        sessions.insert(session_key.to_string(), session);
    }
    
    pub async fn end_session(&self, sender_comp_id: &str) {
        let mut sessions = self.sessions.write().await;
        sessions.retain(|_, s| s.sender_comp_id != sender_comp_id);
    }
    
    pub async fn get_active_sessions(&self) -> Vec<Session> {
        let sessions = self.sessions.read().await;
        sessions.values()
            .filter(|s| s.is_active())
            .cloned()
            .collect()
    }
    
    pub async fn get_all_sessions(&self) -> Vec<Session> {
        let sessions = self.sessions.read().await;
        sessions.values().cloned().collect()
    }
    
    pub async fn session_count(&self) -> usize {
        let sessions = self.sessions.read().await;
        sessions.len()
    }
    
    pub async fn can_create_session(&self) -> bool {
        let sessions = self.sessions.read().await;
        sessions.len() < self.max_sessions
    }
    
    /// Check for stale sessions and return their keys
    pub async fn get_stale_sessions(&self, timeout_seconds: i64) -> Vec<String> {
        let sessions = self.sessions.read().await;
        let now = Utc::now();
        
        sessions.iter()
            .filter(|(_, s)| {
                let elapsed = (now - s.last_heartbeat).num_seconds();
                elapsed > timeout_seconds
            })
            .map(|(k, _)| k.clone())
            .collect()
    }
    
    /// Get sessions pending test request
    pub async fn get_sessions_pending_test_request(&self) -> Vec<String> {
        let sessions = self.sessions.read().await;
        sessions.iter()
            .filter(|(_, s)| s.pending_test_req)
            .map(|(k, _)| k.clone())
            .collect()
    }
}

impl Default for SessionManager {
    fn default() -> Self {
        Self::new(1000)
    }
}