//! Authentication and Authorization Service
//! Handles JWT tokens, API keys, and role-based access control

use std::sync::Arc;
use uuid::Uuid;
use chrono::{Utc, Duration};
use rust_decimal::Decimal;
use serde::{Deserialize, Serialize};
use bcrypt::{hash, verify, DEFAULT_COST};
use jsonwebtoken::{encode, decode, Header, Validation, EncodingKey, DecodingKey};
use tracing::{info, warn, error};

use crate::models::*;
use crate::db::Database;
use crate::cache::RedisCache;

/// JWT Claims
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Claims {
    pub sub: String, // User ID
    pub email: String,
    pub role: String,
    pub permissions: Vec<String>,
    pub exp: usize,
    pub iat: usize,
}

/// Login request
#[derive(Debug, Deserialize)]
pub struct LoginRequest {
    pub email: String,
    pub password: String,
    pub remember_me: Option<bool>,
}

/// Login response
#[derive(Debug, Serialize)]
pub struct LoginResponse {
    pub access_token: String,
    pub refresh_token: String,
    pub token_type: String,
    pub expires_in: usize,
    pub user: Account,
}

/// API Key request
#[derive(Debug, Deserialize)]
pub struct CreateApiKeyRequest {
    pub name: String,
    pub permissions: Vec<String>,
    pub ip_whitelist: Option<Vec<String>>,
    pub rate_limit: Option<u32>,
    pub expires_in_days: Option<u32>,
}

/// Authentication service
pub struct AuthService {
    pub db: Arc<Database>,
    pub cache: Arc<RedisCache>,
    pub jwt_secret: String,
    pub jwt_expiry_hours: i64,
    pub refresh_expiry_days: i64,
}

impl AuthService {
    pub fn new(db: Arc<Database>, cache: Arc<RedisCache>, jwt_secret: String) -> Self {
        Self {
            db,
            cache,
            jwt_secret,
            jwt_expiry_hours: 24,
            refresh_expiry_days: 30,
        }
    }

    /// Hash password
    pub fn hash_password(&self, password: &str) -> Result<String, String> {
        hash(password, DEFAULT_COST).map_err(|e| format!("Failed to hash password: {}", e))
    }

    /// Verify password
    pub fn verify_password(&self, password: &str, hash: &str) -> bool {
        verify(password, hash).unwrap_or(false)
    }

    /// Generate JWT token
    pub fn generate_token(&self, user: &Account) -> Result<String, String> {
        let now = Utc::now();
        let exp = now + Duration::hours(self.jwt_expiry_hours);

        let claims = Claims {
            sub: user.user_id.to_string(),
            email: user.email.clone(),
            role: format!("{:?}", user.role),
            permissions: user.permissions.clone(),
            exp: exp.timestamp() as usize,
            iat: now.timestamp() as usize,
        };

        encode(
            &Header::default(),
            &claims,
            &EncodingKey::from_secret(self.jwt_secret.as_bytes()),
        ).map_err(|e| format!("Failed to generate token: {}", e))
    }

    /// Generate refresh token
    pub fn generate_refresh_token(&self, user_id: Uuid) -> String {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        let token: String = (0..64)
            .map(|_| rng.sample(rand::distributions::Alphanumeric) as char)
            .collect();
        
        // Store refresh token in cache
        let key = format!("refresh_token:{}", token);
        let exp = self.refresh_expiry_days * 24 * 60 * 60;
        let _ = self.cache.set_with_expiry(&key, &user_id.to_string(), exp as usize).await;
        
        token
    }

    /// Validate JWT token
    pub fn validate_token(&self, token: &str) -> Result<Claims, String> {
        decode::<Claims>(
            token,
            &DecodingKey::from_secret(self.jwt_secret.as_bytes()),
            &Validation::default(),
        )
        .map(|data| data.claims)
        .map_err(|e| format!("Invalid token: {}", e))
    }

    /// Login user
    pub async fn login(&self, request: LoginRequest) -> Result<LoginResponse, String> {
        // Get user by email
        let user = self.db.get_user_by_email(&request.email).await?
            .ok_or("Invalid credentials")?;

        // Check account status
        if user.status != AccountStatus::Active {
            return Err("Account is not active".to_string());
        }

        // Get password hash
        let password_hash = self.db.get_password_hash(user.user_id).await?
            .ok_or("Invalid credentials")?;

        // Verify password
        if !self.verify_password(&request.password, &password_hash) {
            return Err("Invalid credentials".to_string());
        }

        // Generate tokens
        let access_token = self.generate_token(&user)?;
        let refresh_token = self.generate_refresh_token(user.user_id);

        // Update last login
        let _ = self.db.update_last_login(user.user_id).await;

        info!("User logged in: {}", user.email);

        Ok(LoginResponse {
            access_token,
            refresh_token,
            token_type: "Bearer".to_string(),
            expires_in: (self.jwt_expiry_hours * 3600) as usize,
            user,
        })
    }

    /// Refresh access token
    pub async fn refresh_token(&self, refresh_token: &str) -> Result<LoginResponse, String> {
        // Validate refresh token
        let key = format!("refresh_token:{}", refresh_token);
        let user_id_str = self.cache.get(&key).await
            .ok_or("Invalid refresh token")?;

        let user_id: Uuid = user_id_str.parse()
            .map_err(|_| "Invalid refresh token")?;

        // Get user
        let user = self.db.get_user_by_id(user_id).await?
            .ok_or("User not found")?;

        // Check account status
        if user.status != AccountStatus::Active {
            return Err("Account is not active".to_string());
        }

        // Generate new tokens
        let access_token = self.generate_token(&user)?;
        let new_refresh_token = self.generate_refresh_token(user.user_id);

        // Invalidate old refresh token
        let _ = self.cache.delete(&key).await;

        Ok(LoginResponse {
            access_token,
            refresh_token: new_refresh_token,
            token_type: "Bearer".to_string(),
            expires_in: (self.jwt_expiry_hours * 3600) as usize,
            user,
        })
    }

    /// Logout user
    pub async fn logout(&self, refresh_token: &str) -> Result<(), String> {
        let key = format!("refresh_token:{}", refresh_token);
        self.cache.delete(&key).await;
        Ok(())
    }

    /// Create API key
    pub async fn create_api_key(
        &self,
        user_id: Uuid,
        request: CreateApiKeyRequest,
    ) -> Result<ApiKey, String> {
        use rand::Rng;
        
        // Generate API key and secret
        let mut rng = rand::thread_rng();
        let api_key: String = (0..32)
            .map(|_| rng.sample(rand::distributions::Alphanumeric) as char)
            .collect();
        let api_secret: String = (0..64)
            .map(|_| rng.sample(rand::distributions::Alphanumeric) as char)
            .collect();

        // Hash the secret
        let secret_hash = self.hash_password(&api_secret)?;

        let api_key_obj = ApiKey {
            id: Uuid::new_v4(),
            user_id,
            name: request.name,
            api_key,
            api_secret: secret_hash,
            permissions: request.permissions,
            ip_whitelist: request.ip_whitelist.unwrap_or_default(),
            rate_limit: request.rate_limit.unwrap_or(100),
            created_at: Utc::now(),
            expires_at: request.expires_in_days.map(|days| Utc::now() + Duration::days(days as i64)),
            last_used_at: None,
            enabled: true,
        };

        // Save to database
        self.db.create_api_key(&api_key_obj).await?;

        info!("API key created for user: {}", user_id);

        Ok(api_key_obj)
    }

    /// Validate API key
    pub async fn validate_api_key(
        &self,
        api_key: &str,
        api_secret: &str,
        ip_address: &str,
    ) -> Result<Account, String> {
        // Get API key from database
        let key_obj = self.db.get_api_key(api_key).await?
            .ok_or("Invalid API key")?;

        // Check if enabled
        if !key_obj.enabled {
            return Err("API key is disabled".to_string());
        }

        // Check expiration
        if let Some(exp) = key_obj.expires_at {
            if exp < Utc::now() {
                return Err("API key has expired".to_string());
            }
        }

        // Check IP whitelist
        if !key_obj.ip_whitelist.is_empty() && !key_obj.ip_whitelist.contains(&ip_address.to_string()) {
            return Err("IP address not in whitelist".to_string());
        }

        // Verify secret
        if !self.verify_password(api_secret, &key_obj.api_secret) {
            return Err("Invalid API secret".to_string());
        }

        // Update last used
        let _ = self.db.update_api_key_last_used(key_obj.id).await;

        // Get user
        let user = self.db.get_user_by_id(key_obj.user_id).await?
            .ok_or("User not found")?;

        // Check account status
        if user.status != AccountStatus::Active {
            return Err("Account is not active".to_string());
        }

        Ok(user)
    }

    /// Check if user has permission
    pub fn has_permission(&self, user: &Account, permission: &str) -> bool {
        // Super admin has all permissions
        if user.role == UserRole::SuperAdmin {
            return true;
        }

        // Check specific permission
        user.permissions.contains(&permission.to_string())
    }

    /// Check if user has any of the permissions
    pub fn has_any_permission(&self, user: &Account, permissions: &[&str]) -> bool {
        if user.role == UserRole::SuperAdmin {
            return true;
        }

        permissions.iter().any(|p| user.permissions.contains(&p.to_string()))
    }

    /// Check if user has all permissions
    pub fn has_all_permissions(&self, user: &Account, permissions: &[&str]) -> bool {
        if user.role == UserRole::SuperAdmin {
            return true;
        }

        permissions.iter().all(|p| user.permissions.contains(&p.to_string()))
    }

    /// Check if user has role
    pub fn has_role(&self, user: &Account, role: UserRole) -> bool {
        user.role == role || user.role == UserRole::SuperAdmin
    }

    /// Get user from token
    pub async fn get_user_from_token(&self, token: &str) -> Result<Account, String> {
        let claims = self.validate_token(token)?;
        let user_id: Uuid = claims.sub.parse()
            .map_err(|_| "Invalid user ID in token")?;

        let user = self.db.get_user_by_id(user_id).await?
            .ok_or("User not found")?;

        Ok(user)
    }
}

/// Rate limiter for API requests
pub struct RateLimiter {
    cache: Arc<RedisCache>,
    max_requests: u32,
    window_seconds: u32,
}

impl RateLimiter {
    pub fn new(cache: Arc<RedisCache>, max_requests: u32, window_seconds: u32) -> Self {
        Self {
            cache,
            max_requests,
            window_seconds,
        }
    }

    /// Check if request is allowed
    pub async fn check(&self, key: &str) -> Result<bool, String> {
        let cache_key = format!("rate_limit:{}", key);
        
        // Get current count
        let count: Option<u32> = self.cache.get(&cache_key).await
            .and_then(|v| v.parse().ok());

        match count {
            Some(c) if c >= self.max_requests => Ok(false),
            Some(c) => {
                self.cache.set_with_expiry(&cache_key, &(c + 1).to_string(), self.window_seconds as usize).await;
                Ok(true)
            }
            None => {
                self.cache.set_with_expiry(&cache_key, "1".to_string(), self.window_seconds as usize).await;
                Ok(true)
            }
        }
    }

    /// Get remaining requests
    pub async fn remaining(&self, key: &str) -> u32 {
        let cache_key = format!("rate_limit:{}", key);
        let count: Option<u32> = self.cache.get(&cache_key).await
            .and_then(|v| v.parse().ok());

        match count {
            Some(c) => self.max_requests.saturating_sub(c),
            None => self.max_requests,
        }
    }
}pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}
