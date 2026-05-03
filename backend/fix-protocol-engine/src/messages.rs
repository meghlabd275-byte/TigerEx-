//! FIX Message Types and Field Definitions

use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub enum MsgType {
    Heartbeat,                  // 0
    TestRequest,                // 1
    ResendRequest,              // 2
    Reject,                     // 3
    SequenceReset,              // 4
    Logout,                     // 5
    Logon,                      // A
    NewOrderSingle,             // D
    OrderCancelRequest,         // F
    OrderCancelReplaceRequest,  // G
    OrderStatusRequest,         // H
    OrderCancelReject,          // 9
    MarketDataRequest,          // V
    MarketDataSnapshot,         // W
    MarketDataIncremental,      // X
    QuoteRequest,               // R
    Quote,                      // S
    SecurityListRequest,        // x
    SecurityList,               // y
    TradingSessionStatusRequest,// g
    TradingSessionStatus,       // h
    ExecutionReport,            // 8
    Allocation,                 // J
    News,                       // B
    Email,                      // C
    Advertisement,              // 7
    IndicationOfInterest,       // 6
    Unknown(String),
}

impl From<&str> for MsgType {
    fn from(s: &str) -> Self {
        match s {
            "0" => MsgType::Heartbeat,
            "1" => MsgType::TestRequest,
            "2" => MsgType::ResendRequest,
            "3" => MsgType::Reject,
            "4" => MsgType::SequenceReset,
            "5" => MsgType::Logout,
            "A" => MsgType::Logon,
            "D" => MsgType::NewOrderSingle,
            "F" => MsgType::OrderCancelRequest,
            "G" => MsgType::OrderCancelReplaceRequest,
            "H" => MsgType::OrderStatusRequest,
            "9" => MsgType::OrderCancelReject,
            "V" => MsgType::MarketDataRequest,
            "W" => MsgType::MarketDataSnapshot,
            "X" => MsgType::MarketDataIncremental,
            "R" => MsgType::QuoteRequest,
            "S" => MsgType::Quote,
            "x" => MsgType::SecurityListRequest,
            "y" => MsgType::SecurityList,
            "g" => MsgType::TradingSessionStatusRequest,
            "h" => MsgType::TradingSessionStatus,
            "8" => MsgType::ExecutionReport,
            "J" => MsgType::Allocation,
            "B" => MsgType::News,
            "C" => MsgType::Email,
            "7" => MsgType::Advertisement,
            "6" => MsgType::IndicationOfInterest,
            other => MsgType::Unknown(other.to_string()),
        }
    }
}

#[derive(Debug, Clone)]
pub struct FixField {
    pub tag: u32,
    pub value: String,
}

#[derive(Debug, Clone, Default)]
pub struct FixMessage {
    pub fields: Vec<FixField>,
}

impl FixMessage {
    pub fn new() -> Self {
        Self { fields: Vec::new() }
    }
    
    pub fn with_field(mut self, tag: impl Into<u32>, value: impl Into<String>) -> Self {
        self.fields.push(FixField {
            tag: tag.into(),
            value: value.into(),
        });
        self
    }
    
    pub fn get_field(&self, tag: u32) -> Option<&str> {
        self.fields.iter()
            .find(|f| f.tag == tag)
            .map(|f| f.value.as_str())
    }
    
    pub fn get_msg_type(&self) -> Option<MsgType> {
        self.get_field(35).map(|s| s.into())
    }
    
    pub fn get_sender_comp_id(&self) -> Option<&str> {
        self.get_field(49)
    }
    
    pub fn get_target_comp_id(&self) -> Option<&str> {
        self.get_field(56)
    }
    
    pub fn get_msg_seq_num(&self) -> Option<u64> {
        self.get_field(34).and_then(|s| s.parse().ok())
    }
    
    pub fn get_sending_time(&self) -> Option<&str> {
        self.get_field(52)
    }
    
    pub fn to_hashmap(&self) -> HashMap<u32, String> {
        self.fields.iter()
            .map(|f| (f.tag, f.value.clone()))
            .collect()
    }
}

/// FIX Tag Definitions (Common Tags)
pub mod tags {
    // Standard Header
    pub const BEGIN_STRING: u32 = 8;
    pub const BODY_LENGTH: u32 = 9;
    pub const MSG_TYPE: u32 = 35;
    pub const SENDER_COMP_ID: u32 = 49;
    pub const TARGET_COMP_ID: u32 = 56;
    pub const MSG_SEQ_NUM: u32 = 34;
    pub const SENDING_TIME: u32 = 52;
    
    // Standard Trailer
    pub const CHECKSUM: u32 = 10;
    
    // Logon/Logout
    pub const ENCRYPT_METHOD: u32 = 98;
    pub const HEART_BT_INT: u32 = 108;
    pub const USERNAME: u32 = 553;
    pub const PASSWORD: u32 = 554;
    pub const RESET_SEQ_NUM_FLAG: u32 = 141;
    pub const LOGOUT_TEXT: u32 = 58;
    
    // Heartbeat/Test Request
    pub const TEST_REQ_ID: u32 = 112;
    
    // Order Management
    pub const CL_ORD_ID: u32 = 11;
    pub const ORDER_ID: u32 = 37;
    pub const ORIG_CL_ORD_ID: u32 = 41;
    pub const EXEC_ID: u32 = 17;
    pub const EXEC_TYPE: u32 = 150;
    pub const ORD_STATUS: u32 = 39;
    pub const ORD_TYPE: u32 = 40;
    pub const SIDE: u32 = 54;
    pub const SYMBOL: u32 = 55;
    pub const ORDER_QTY: u32 = 38;
    pub const PRICE: u32 = 44;
    pub const STOP_PRICE: u32 = 99;
    pub const TIME_IN_FORCE: u32 = 59;
    pub const LEAVES_QTY: u32 = 151;
    pub const CUM_QTY: u32 = 14;
    pub const AVG_PX: u32 = 6;
    pub const LAST_PX: u32 = 31;
    pub const LAST_QTY: u32 = 32;
    pub const LAST_SHARES: u32 = 32;
    
    // Market Data
    pub const MD_REQ_ID: u32 = 262;
    pub const MD_ENTRY_TYPE: u32 = 269;
    pub const MD_ENTRY_PX: u32 = 270;
    pub const MD_ENTRY_SIZE: u32 = 271;
    pub const MD_ENTRY_DATE: u32 = 272;
    pub const MD_ENTRY_TIME: u32 = 273;
    pub const MARKET_DEPTH: u32 = 264;
    pub const MD_UPDATE_TYPE: u32 = 265;
    pub const SUBSCRIPTION_REQUEST_TYPE: u32 = 263;
    
    // Quote
    pub const QUOTE_REQ_ID: u32 = 131;
    pub const QUOTE_ID: u32 = 117;
    pub const BID_PX: u32 = 132;
    pub const OFFER_PX: u32 = 133;
    pub const BID_SIZE: u32 = 134;
    pub const OFFER_SIZE: u32 = 135;
    
    // Security List
    pub const SECURITY_REQ_ID: u32 = 320;
    pub const SECURITY_RESPONSE_ID: u32 = 322;
    pub const TOTAL_NUM_SECURITIES: u32 = 393;
    pub const NO_RELATED_SYM: u32 = 146;
    
    // Trading Session
    pub const TRAD_SES_REQ_ID: u32 = 335;
    pub const TRADING_SESSION_ID: u32 = 336;
    pub const TRADING_SESSION_SUB_ID: u32 = 625;
    pub const TRAD_SES_STATUS: u32 = 339;
    pub const TRAD_SES_STATUS_REJ_REASON: u32 = 340;
    
    // Session Status
    pub const SESSION_STATUS: u32 = 1137;
    
    // Account
    pub const ACCOUNT: u32 = 1;
    pub const ACCOUNT_TYPE: u32 = 581;
    
    // Instrument
    pub const SECURITY_TYPE: u32 = 167;
    pub const MATURITY_MONTH_YEAR: u32 = 200;
    pub const MATURITY_DATE: u32 = 541;
    pub const STRIKE_PRICE: u32 = 202;
    pub const OPT_ATTRIBUTE: u32 = 206;
    pub const SECURITY_EXCHANGE: u32 = 207;
    
    // Order Restrictions
    pub const ORDER_CAPACITY: u32 = 528;
    pub const ORDER_RESTRICTIONS: u32 = 529;
    
    // Commission
    pub const COMMISSION: u32 = 12;
    pub const COMMISSION_TYPE: u32 = 13;
    
    // Rejection
    pub const REF_SEQ_NUM: u32 = 45;
    pub const REF_MSG_TYPE: u32 = 372;
    pub const SESSION_REJECT_REASON: u32 = 373;
    pub const TEXT: u32 = 58;
    pub const BUSINESS_REJECT_REASON: u32 = 380;
    pub const BUSINESS_REJECT_REF_ID: u32 = 379;
    
    // Routing
    pub const NO_ROUTING_IDS: u32 = 215;
    pub const ROUTING_TYPE: u32 = 216;
    pub const ROUTING_ID: u32 = 217;
    
    // Party
    pub const NO_PARTY_IDS: u32 = 453;
    pub const PARTY_ID: u32 = 448;
    pub const PARTY_ID_SOURCE: u32 = 447;
    pub const PARTY_ROLE: u32 = 452;
    
    // Clearing
    pub const CLEARING_FIRM: u32 = 439;
    pub const CLEARING_ACCOUNT: u32 = 440;
}

/// Order Status Values
pub mod ord_status {
    pub const NEW: &str = "0";
    pub const PARTIALLY_FILLED: &str = "1";
    pub const FILLED: &str = "2";
    pub const DONE_FOR_DAY: &str = "3";
    pub const CANCELED: &str = "4";
    pub const REPLACED: &str = "5";
    pub const PENDING_CANCEL: &str = "6";
    pub const STOPPED: &str = "7";
    pub const REJECTED: &str = "8";
    pub const SUSPENDED: &str = "9";
    pub const PENDING_NEW: &str = "A";
    pub const CALCULATED: &str = "B";
    pub const EXPIRED: &str = "C";
    pub const ACCEPTED_FOR_BIDDING: &str = "D";
    pub const PENDING_REPLACE: &str = "E";
}

/// Execution Type Values
pub mod exec_type {
    pub const NEW: &str = "0";
    pub const PARTIAL_FILL: &str = "1";
    pub const FILL: &str = "2";
    pub const DONE_FOR_DAY: &str = "3";
    pub const CANCELED: &str = "4";
    pub const REPLACE: &str = "5";
    pub const PENDING_CANCEL: &str = "6";
    pub const STOPPED: &str = "7";
    pub const REJECTED: &str = "8";
    pub const SUSPENDED: &str = "9";
    pub const PENDING_NEW: &str = "A";
    pub const PENDING_REPLACE: &str = "E";
    pub const TRADE: &str = "F";
    pub const TRADE_CORRECT: &str = "G";
    pub const TRADE_CANCEL: &str = "H";
    pub const ORDER_STATUS: &str = "I";
    pub const TRADE_IN_CLEARING_HOLD: &str = "J";
}

/// Order Type Values
pub mod ord_type {
    pub const MARKET: &str = "1";
    pub const LIMIT: &str = "2";
    pub const STOP: &str = "3";
    pub const STOP_LIMIT: &str = "4";
    pub const MARKET_ON_CLOSE: &str = "5";
    pub const WITH_OR_WITHOUT: &str = "6";
    pub const LIMIT_OR_BETTER: &str = "7";
    pub const LIMIT_WITH_OR_WITHOUT: &str = "8";
    pub const ON_BASIS: &str = "9";
    pub const ON_CLOSE: &str = "A";
    pub const LIMIT_ON_CLOSE: &str = "B";
    pub const FOREX_MARKET: &str = "C";
    pub const PREVIOUSLY_QUOTED: &str = "D";
    pub const PREVIOUSLY_INDICATED: &str = "E";
    pub const FOREX_LIMIT: &str = "F";
    pub const FOREX_SWAP: &str = "G";
    pub const GOOD_TILL_CANCEL: &str = "H";
    pub const GOOD_TILL_CROSSING: &str = "I";
    pub const GOOD_TILL_DATE: &str = "J";
}

/// Side Values
pub mod side {
    pub const BUY: &str = "1";
    pub const SELL: &str = "2";
    pub const BUY_MINUS: &str = "3";
    pub const SELL_PLUS: &str = "4";
    pub const SELL_SHORT: &str = "5";
    pub const SELL_SHORT_EXEMPT: &str = "6";
    pub const UNDISCLOSED: &str = "7";
    pub const CROSS: &str = "8";
    pub const CROSS_SHORT: &str = "9";
}

/// Time In Force Values
pub mod time_in_force {
    pub const DAY: &str = "0";
    pub const GOOD_TILL_CANCEL: &str = "1";
    pub const AT_THE_OPENING: &str = "2";
    pub const IMMEDIATE_OR_CANCEL: &str = "3";
    pub const FILL_OR_KILL: &str = "4";
    pub const GOOD_TILL_CROSSING: &str = "5";
    pub const GOOD_TILL_DATE: &str = "6";
    pub const AT_THE_CLOSE: &str = "7";
}pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}
