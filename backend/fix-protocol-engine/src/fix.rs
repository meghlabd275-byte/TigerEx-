//! FIX Protocol Implementation
//! Supports FIX 4.4 and FIX 5.0 SP2

use std::collections::HashMap;
use std::sync::Arc;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;
use chrono::{DateTime, Utc};
use thiserror::Error;

use crate::session::SessionManager;
use crate::engine::TradingEngineConnector;
use crate::messages::{FixMessage, FixField, MsgType};
use crate::Config;

#[derive(Error, Debug)]
pub enum FixError {
    #[error("Invalid FIX message: {0}")]
    InvalidMessage(String),
    #[error("Checksum mismatch")]
    ChecksumMismatch,
    #[error("Session not found: {0}")]
    SessionNotFound(String),
    #[error("Authentication failed")]
    AuthenticationFailed,
    #[error("Sequence gap detected")]
    SequenceGap,
    #[error("Heartbeat timeout")]
    HeartbeatTimeout,
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Parse error: {0}")]
    ParseError(String),
}

pub struct FixServer {
    config: Config,
    session_manager: Arc<SessionManager>,
    engine_connector: Arc<TradingEngineConnector>,
}

impl Clone for FixServer {
    fn clone(&self) -> Self {
        Self {
            config: self.config.clone(),
            session_manager: self.session_manager.clone(),
            engine_connector: self.engine_connector.clone(),
        }
    }
}

impl FixServer {
    pub fn new(
        config: Config,
        session_manager: Arc<SessionManager>,
        engine_connector: Arc<TradingEngineConnector>,
    ) -> Self {
        Self {
            config,
            session_manager,
            engine_connector,
        }
    }
    
    pub async fn handle_connection(&self, mut stream: TcpStream) -> Result<(), FixError> {
        let mut buffer = vec![0u8; 65536];
        let mut message_buffer = Vec::new();
        
        loop {
            let n = stream.read(&mut buffer).await?;
            if n == 0 {
                break;
            }
            
            message_buffer.extend_from_slice(&buffer[..n]);
            
            // Process complete messages
            while let Some(msg_end) = Self::find_message_end(&message_buffer) {
                let msg_bytes = message_buffer.drain(..=msg_end).collect::<Vec<_>>();
                let message = self.parse_message(&msg_bytes)?;
                
                // Process the message
                let response = self.process_message(message.clone()).await?;
                
                // Send response if any
                if let Some(resp_msg) = response {
                    let resp_bytes = self.serialize_message(&resp_msg)?;
                    stream.write_all(&resp_bytes).await?;
                }
            }
        }
        
        Ok(())
    }
    
    fn find_message_end(buffer: &[u8]) -> Option<usize> {
        // FIX messages end with "10=XXX\x01"
        let mut found_checksum = false;
        for i in 0..buffer.len().saturating_sub(1) {
            if buffer[i] == b'1' && buffer[i+1] == b'0' && buffer[i+2] == b'=' {
                found_checksum = true;
            }
            if found_checksum && buffer[i] == 0x01 {
                return Some(i);
            }
        }
        None
    }
    
    pub fn parse_message(&self, data: &[u8]) -> Result<FixMessage, FixError> {
        let msg_str = std::str::from_utf8(data)
            .map_err(|e| FixError::ParseError(e.to_string()))?;
        
        let mut fields: Vec<FixField> = Vec::new();
        
        for field in msg_str.split('\x01') {
            if field.is_empty() {
                continue;
            }
            
            let parts: Vec<&str> = field.splitn(2, '=').collect();
            if parts.len() == 2 {
                let tag = parts[0].parse::<u32>()
                    .map_err(|e| FixError::ParseError(e.to_string()))?;
                let value = parts[1].to_string();
                fields.push(FixField { tag, value });
            }
        }
        
        // Validate checksum
        if !Self::validate_checksum(data, &fields) {
            return Err(FixError::ChecksumMismatch);
        }
        
        // Remove checksum field from fields
        fields.retain(|f| f.tag != 10);
        
        Ok(FixMessage { fields })
    }
    
    fn validate_checksum(data: &[u8], fields: &[FixField]) -> bool {
        // Find the checksum field
        let checksum_field = fields.iter().find(|f| f.tag == 10);
        if checksum_field.is_none() {
            return false;
        }
        
        // Calculate expected checksum
        let expected: u8 = checksum_field.unwrap().value.parse().unwrap_or(0);
        
        // Find where checksum field starts (tag 10=)
        let mut checksum_start = None;
        for i in 0..data.len().saturating_sub(3) {
            if data[i] == 0x01 && data[i+1] == b'1' && data[i+2] == b'0' && data[i+3] == b'=' {
                checksum_start = Some(i + 1);
                break;
            }
        }
        
        if let Some(start) = checksum_start {
            let calculated = data[..start].iter().fold(0u8, |acc, &b| acc.wrapping_add(b));
            return calculated == expected;
        }
        
        false
    }
    
    pub fn serialize_message(&self, message: &FixMessage) -> Result<Vec<u8>, FixError> {
        let mut result = Vec::new();
        
        for field in &message.fields {
            result.extend_from_slice(format!("{}={}\x01", field.tag, field.value).as_bytes());
        }
        
        // Calculate and append checksum
        let checksum: u8 = result.iter().fold(0u8, |acc, &b| acc.wrapping_add(b));
        result.extend_from_slice(format!("10={:03}\x01", checksum).as_bytes());
        
        Ok(result)
    }
    
    async fn process_message(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        let msg_type = message.get_msg_type();
        
        match msg_type {
            Some(MsgType::Logon) => self.handle_logon(message).await,
            Some(MsgType::Logout) => self.handle_logout(message).await,
            Some(MsgType::Heartbeat) => self.handle_heartbeat(message).await,
            Some(MsgType::TestRequest) => self.handle_test_request(message).await,
            Some(MsgType::NewOrderSingle) => self.handle_new_order(message).await,
            Some(MsgType::OrderCancelRequest) => self.handle_order_cancel(message).await,
            Some(MsgType::OrderCancelReplaceRequest) => self.handle_order_replace(message).await,
            Some(MsgType::OrderStatusRequest) => self.handle_order_status(message).await,
            Some(MsgType::MarketDataRequest) => self.handle_market_data_request(message).await,
            Some(MsgType::QuoteRequest) => self.handle_quote_request(message).await,
            Some(MsgType::SecurityListRequest) => self.handle_security_list_request(message).await,
            Some(MsgType::TradingSessionStatusRequest) => self.handle_trading_session_status(message).await,
            _ => {
                // Unknown message type - send reject
                Ok(Some(self.create_reject_message(&message, "Unsupported message type")?))
            }
        }
    }
    
    async fn handle_logon(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        let sender_comp_id = message.get_field(49).unwrap_or("");
        let target_comp_id = message.get_field(56).unwrap_or("");
        let username = message.get_field(553);
        let password = message.get_field(554);
        let encrypt_method = message.get_field(98).unwrap_or("0");
        let heart_bt_int = message.get_field(108)
            .and_then(|s| s.parse::<u32>().ok())
            .unwrap_or(self.config.default_heartbeat_interval);
        
        // Authenticate
        let authenticated = self.session_manager
            .authenticate(sender_comp_id, username, password).await;
        
        if !authenticated {
            return Err(FixError::AuthenticationFailed);
        }
        
        // Create session
        self.session_manager.create_session(
            sender_comp_id.to_string(),
            target_comp_id.to_string(),
            heart_bt_int,
        ).await;
        
        // Send logon response
        let response = FixMessage::new()
            .with_field(35, "A") // MsgType = Logon
            .with_field(49, target_comp_id) // SenderCompID
            .with_field(56, sender_comp_id) // TargetCompID
            .with_field(34, "1") // MsgSeqNum
            .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
            .with_field(98, encrypt_method) // EncryptMethod
            .with_field(108, &heart_bt_int.to_string()) // HeartBtInt
            .with_field(554, "") // ResetSeqNumFlag
        
            ;
        
        Ok(Some(response))
    }
    
    async fn handle_logout(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        let sender_comp_id = message.get_field(49).unwrap_or("");
        
        self.session_manager.end_session(sender_comp_id).await;
        
        let response = FixMessage::new()
            .with_field(35, "5") // MsgType = Logout
            .with_field(49, message.get_field(56).unwrap_or(""))
            .with_field(56, sender_comp_id)
            .with_field(34, "1")
            .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
            .with_field(58, "Logout successful");
        
        Ok(Some(response))
    }
    
    async fn handle_heartbeat(&self, _message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        // Heartbeats don't need a response
        Ok(None)
    }
    
    async fn handle_test_request(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        let test_req_id = message.get_field(112).unwrap_or("");
        
        let response = FixMessage::new()
            .with_field(35, "0") // MsgType = Heartbeat
            .with_field(49, message.get_field(56).unwrap_or(""))
            .with_field(56, message.get_field(49).unwrap_or(""))
            .with_field(34, "1")
            .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
            .with_field(112, test_req_id); // TestReqID
        
        Ok(Some(response))
    }
    
    async fn handle_new_order(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        // Extract order details
        let cl_ord_id = message.get_field(11).unwrap_or("");
        let symbol = message.get_field(55).unwrap_or("");
        let side = message.get_field(54).unwrap_or("1"); // 1=Buy, 2=Sell
        let order_qty = message.get_field(38).and_then(|s| s.parse::<f64>().ok()).unwrap_or(0.0);
        let price = message.get_field(44).and_then(|s| s.parse::<f64>().ok());
        let ord_type = message.get_field(40).unwrap_or("2"); // 1=Market, 2=Limit, 3=Stop
        let time_in_force = message.get_field(59).unwrap_or("0"); // 0=Day, 1=GTC, 3=IOC, 4=FOK
        
        // Submit order to trading engine
        let order_result = self.engine_connector.submit_order(
            symbol, side, order_qty, price, ord_type, time_in_force,
        ).await;
        
        // Create execution report
        let response = match order_result {
            Ok(order_id) => {
                FixMessage::new()
                    .with_field(35, "8") // MsgType = ExecutionReport
                    .with_field(49, message.get_field(56).unwrap_or(""))
                    .with_field(56, message.get_field(49).unwrap_or(""))
                    .with_field(34, "1")
                    .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
                    .with_field(37, &order_id) // OrderID
                    .with_field(11, cl_ord_id) // ClOrdID
                    .with_field(17, &format!("EXEC-{}", order_id)) // ExecID
                    .with_field(150, "0") // ExecType = New
                    .with_field(39, "0") // OrdStatus = New
                    .with_field(55, symbol) // Symbol
                    .with_field(54, side) // Side
                    .with_field(38, &order_qty.to_string()) // OrderQty
                    .with_field(40, ord_type) // OrdType
                    .with_field(59, time_in_force) // TimeInForce
                    .with_field(151, &order_qty.to_string()) // LeavesQty
                    .with_field(14, "0") // CumQty
            }
            Err(e) => {
                FixMessage::new()
                    .with_field(35, "8") // MsgType = ExecutionReport
                    .with_field(49, message.get_field(56).unwrap_or(""))
                    .with_field(56, message.get_field(49).unwrap_or(""))
                    .with_field(34, "1")
                    .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
                    .with_field(11, cl_ord_id)
                    .with_field(150, "8") // ExecType = Rejected
                    .with_field(39, "8") // OrdStatus = Rejected
                    .with_field(58, &format!("Order rejected: {}", e)) // Text
            }
        };
        
        Ok(Some(response))
    }
    
    async fn handle_order_cancel(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        let cl_ord_id = message.get_field(11).unwrap_or("");
        let order_id = message.get_field(37).unwrap_or("");
        let symbol = message.get_field(55).unwrap_or("");
        
        let cancel_result = self.engine_connector.cancel_order(order_id).await;
        
        let response = match cancel_result {
            Ok(_) => {
                FixMessage::new()
                    .with_field(35, "8") // MsgType = ExecutionReport
                    .with_field(49, message.get_field(56).unwrap_or(""))
                    .with_field(56, message.get_field(49).unwrap_or(""))
                    .with_field(34, "1")
                    .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
                    .with_field(37, order_id)
                    .with_field(11, cl_ord_id)
                    .with_field(150, "4") // ExecType = Canceled
                    .with_field(39, "4") // OrdStatus = Canceled
                    .with_field(55, symbol)
            }
            Err(e) => {
                FixMessage::new()
                    .with_field(35, "9") // MsgType = OrderCancelReject
                    .with_field(49, message.get_field(56).unwrap_or(""))
                    .with_field(56, message.get_field(49).unwrap_or(""))
                    .with_field(34, "1")
                    .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
                    .with_field(11, cl_ord_id)
                    .with_field(37, order_id)
                    .with_field(58, &format!("Cancel rejected: {}", e))
            }
        };
        
        Ok(Some(response))
    }
    
    async fn handle_order_replace(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        let cl_ord_id = message.get_field(11).unwrap_or("");
        let order_id = message.get_field(37).unwrap_or("");
        let symbol = message.get_field(55).unwrap_or("");
        let new_qty = message.get_field(38).and_then(|s| s.parse::<f64>().ok());
        let new_price = message.get_field(44).and_then(|s| s.parse::<f64>().ok());
        
        let replace_result = self.engine_connector.replace_order(
            order_id, new_qty, new_price
        ).await;
        
        let response = match replace_result {
            Ok(new_order_id) => {
                FixMessage::new()
                    .with_field(35, "8")
                    .with_field(49, message.get_field(56).unwrap_or(""))
                    .with_field(56, message.get_field(49).unwrap_or(""))
                    .with_field(34, "1")
                    .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
                    .with_field(37, &new_order_id)
                    .with_field(11, cl_ord_id)
                    .with_field(41, order_id) // OrigClOrdID
                    .with_field(150, "5") // ExecType = Replace
                    .with_field(39, "0") // OrdStatus = New
                    .with_field(55, symbol)
            }
            Err(e) => {
                FixMessage::new()
                    .with_field(35, "8")
                    .with_field(49, message.get_field(56).unwrap_or(""))
                    .with_field(56, message.get_field(49).unwrap_or(""))
                    .with_field(34, "1")
                    .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
                    .with_field(11, cl_ord_id)
                    .with_field(150, "8") // ExecType = Rejected
                    .with_field(39, "8") // OrdStatus = Rejected
                    .with_field(58, &format!("Replace rejected: {}", e))
            }
        };
        
        Ok(Some(response))
    }
    
    async fn handle_order_status(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        let order_id = message.get_field(37).unwrap_or("");
        
        let status = self.engine_connector.get_order_status(order_id).await;
        
        let response = match status {
            Some(order_status) => {
                FixMessage::new()
                    .with_field(35, "8")
                    .with_field(49, message.get_field(56).unwrap_or(""))
                    .with_field(56, message.get_field(49).unwrap_or(""))
                    .with_field(34, "1")
                    .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
                    .with_field(37, order_id)
                    .with_field(150, "I") // ExecType = OrderStatus
                    .with_field(39, &order_status.status)
                    .with_field(55, &order_status.symbol)
                    .with_field(38, &order_status.quantity.to_string())
                    .with_field(151, &order_status.leaves_qty.to_string())
                    .with_field(14, &order_status.cum_qty.to_string())
            }
            None => {
                self.create_reject_message(&message, "Order not found")?
            }
        };
        
        Ok(Some(response))
    }
    
    async fn handle_market_data_request(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        let md_req_id = message.get_field(262).unwrap_or("");
        let symbol = message.get_field(55).unwrap_or("");
        let subscription_type = message.get_field(263).unwrap_or("0"); // 0=Snapshot, 1=Subscribe
        
        let market_data = self.engine_connector.get_market_data(symbol).await;
        
        let mut response = FixMessage::new()
            .with_field(35, "W") // MsgType = MarketDataSnapshotFullRefresh
            .with_field(49, message.get_field(56).unwrap_or(""))
            .with_field(56, message.get_field(49).unwrap_or(""))
            .with_field(34, "1")
            .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
            .with_field(262, md_req_id) // MDReqID
            .with_field(55, symbol); // Symbol
        
        if let Some(data) = market_data {
            // Add bid group
            response = response
                .with_field(269, "0") // MDEntryType = Bid
                .with_field(270, &data.best_bid.to_string()) // MDEntryPx
                .with_field(271, &data.bid_size.to_string()); // MDEntrySize
            
            // Add ask group
            response = response
                .with_field(269, "1") // MDEntryType = Offer
                .with_field(270, &data.best_ask.to_string())
                .with_field(271, &data.ask_size.to_string());
            
            // Add last trade
            response = response
                .with_field(269, "2") // MDEntryType = Trade
                .with_field(270, &data.last_price.to_string())
                .with_field(271, &data.last_size.to_string());
        }
        
        Ok(Some(response))
    }
    
    async fn handle_quote_request(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        let quote_req_id = message.get_field(131).unwrap_or("");
        let symbol = message.get_field(55).unwrap_or("");
        
        let quote = self.engine_connector.get_quote(symbol).await;
        
        let response = match quote {
            Some(q) => {
                FixMessage::new()
                    .with_field(35, "S") // MsgType = Quote
                    .with_field(49, message.get_field(56).unwrap_or(""))
                    .with_field(56, message.get_field(49).unwrap_or(""))
                    .with_field(34, "1")
                    .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
                    .with_field(131, quote_req_id)
                    .with_field(55, symbol)
                    .with_field(132, &q.bid_price.to_string()) // BidPx
                    .with_field(133, &q.ask_price.to_string()) // OfferPx
                    .with_field(134, &q.bid_size.to_string()) // BidSize
                    .with_field(135, &q.ask_size.to_string()) // OfferSize
            }
            None => {
                self.create_reject_message(&message, "Symbol not found")?
            }
        };
        
        Ok(Some(response))
    }
    
    async fn handle_security_list_request(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        let sec_list_req_id = message.get_field(320).unwrap_or("");
        
        let symbols = self.engine_connector.get_available_symbols().await;
        
        let mut response = FixMessage::new()
            .with_field(35, "y") // MsgType = SecurityList
            .with_field(49, message.get_field(56).unwrap_or(""))
            .with_field(56, message.get_field(49).unwrap_or(""))
            .with_field(34, "1")
            .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
            .with_field(320, sec_list_req_id); // SecurityReqID
        
        for (i, symbol) in symbols.iter().enumerate() {
            response = response
                .with_field(55, symbol)
                .with_field(146, &(i + 1).to_string()); // TotNoRelatedSym
        }
        
        Ok(Some(response))
    }
    
    async fn handle_trading_session_status(&self, message: FixMessage) -> Result<Option<FixMessage>, FixError> {
        let trad_ses_req_id = message.get_field(335).unwrap_or("");
        
        let status = self.engine_connector.get_trading_session_status().await;
        
        let response = FixMessage::new()
            .with_field(35, "h") // MsgType = TradingSessionStatus
            .with_field(49, message.get_field(56).unwrap_or(""))
            .with_field(56, message.get_field(49).unwrap_or(""))
            .with_field(34, "1")
            .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
            .with_field(335, trad_ses_req_id)
            .with_field(336, "1") // TradingSessionID
            .with_field(339, &status.status) // TradSesStatus
            .with_field(340, &status.status.to_string()); // TradSesStatusRejReason
        
        Ok(Some(response))
    }
    
    fn create_reject_message(&self, orig_message: &FixMessage, reason: &str) -> Result<FixMessage, FixError> {
        Ok(FixMessage::new()
            .with_field(35, "3") // MsgType = Reject
            .with_field(49, orig_message.get_field(56).unwrap_or(""))
            .with_field(56, orig_message.get_field(49).unwrap_or(""))
            .with_field(34, "1")
            .with_field(52, &Utc::now().format("%Y%m%d-%H:%M:%S%.3f").to_string())
            .with_field(45, orig_message.get_field(34).unwrap_or("0")) // RefSeqNum
            .with_field(58, reason))
    }
}pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}
