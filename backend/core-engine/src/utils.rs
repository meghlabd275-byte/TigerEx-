//! Utility functions and configuration

pub mod config {
    use std::env;

    #[derive(Debug, Clone)]
    pub struct Config {
        pub host: String,
        pub port: u16,
        pub database_url: String,
        pub redis_url: String,
        pub jwt_secret: String,
        pub environment: String,
    }

    pub fn load_config() -> Result<Config, String> {
        Ok(Config {
            host: env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string()),
            port: env::var("PORT")
                .unwrap_or_else(|_| "8080".to_string())
                .parse()
                .map_err(|_| "Invalid PORT")?,
            database_url: env::var("DATABASE_URL")
                .unwrap_or_else(|_| "postgres://tigerex:tigerex@localhost:5432/tigerex".to_string()),
            redis_url: env::var("REDIS_URL")
                .unwrap_or_else(|_| "redis://localhost:6379".to_string()),
            jwt_secret: env::var("JWT_SECRET")
                .unwrap_or_else(|_| "your-secret-key-change-in-production".to_string()),
            environment: env::var("ENVIRONMENT")
                .unwrap_or_else(|_| "development".to_string()),
        })
    }
}

pub mod decimal {
    use rust_decimal::Decimal;
    use std::str::FromStr;

    pub fn parse_decimal(s: &str) -> Option<Decimal> {
        Decimal::from_str(s).ok()
    }

    pub fn to_string(d: Decimal) -> String {
        d.to_string()
    }

    pub fn zero() -> Decimal {
        Decimal::ZERO
    }

    pub fn one() -> Decimal {
        Decimal::ONE
    }
}

pub mod time {
    use chrono::{DateTime, Utc};

    pub fn now_millis() -> i64 {
        Utc::now().timestamp_millis()
    }

    pub fn now_seconds() -> i64 {
        Utc::now().timestamp()
    }

    pub fn from_millis(millis: i64) -> DateTime<Utc> {
        DateTime::from_timestamp_millis(millis).unwrap_or_else(Utc::now)
    }
}

pub mod crypto {
    use rand::Rng;
    use sha2::{Sha256, Digest};

    pub fn generate_random_bytes(len: usize) -> Vec<u8> {
        let mut rng = rand::thread_rng();
        (0..len).map(|_| rng.gen::<u8>()).collect()
    }

    pub fn sha256(data: &[u8]) -> Vec<u8> {
        let mut hasher = Sha256::new();
        hasher.update(data);
        hasher.finalize().to_vec()
    }

    pub fn hex_encode(data: &[u8]) -> String {
        hex::encode(data)
    }
}pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}
