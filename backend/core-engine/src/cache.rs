//! Redis Cache Layer
//! High-performance caching with pub/sub support

use std::sync::Arc;
use serde::{de::DeserializeOwned, Serialize};
use redis::AsyncCommands;
use tracing::{info, warn, error};

/// Redis cache wrapper
pub struct RedisCache {
    client: redis::Client,
    pool: deadpool_redis::Pool,
}

impl RedisCache {
    /// Create new Redis connection pool
    pub async fn new(redis_url: &str) -> Result<Arc<Self>, String> {
        info!("Connecting to Redis...");
        
        let client = redis::Client::open(redis_url)
            .map_err(|e| format!("Failed to create Redis client: {}", e))?;

        let cfg = deadpool_redis::Config::from_url(redis_url);
        let pool = cfg.create_pool(Some(deadpool_redis::Runtime::Tokio1))
            .map_err(|e| format!("Failed to create Redis pool: {}", e))?;

        info!("Redis connected successfully");
        
        Ok(Arc::new(Self { client, pool }))
    }

    /// Get value from cache
    pub async fn get<T: DeserializeOwned>(&self, key: &str) -> Option<T> {
        let mut conn = self.pool.get().await.ok()?;
        let result: Option<String> = conn.get(key).await.ok()?;
        
        result.and_then(|v| serde_json::from_str(&v).ok())
    }

    /// Set value in cache
    pub async fn set<T: Serialize>(&self, key: &str, value: &T) -> Result<(), String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;
        
        let serialized = serde_json::to_string(value)
            .map_err(|e| format!("Failed to serialize: {}", e))?;

        conn.set(key, serialized).await
            .map_err(|e| format!("Failed to set: {}", e))?;

        Ok(())
    }

    /// Set value with expiry
    pub async fn set_with_expiry<T: Serialize>(&self, key: &str, value: &T, seconds: usize) -> Result<(), String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;
        
        let serialized = serde_json::to_string(value)
            .map_err(|e| format!("Failed to serialize: {}", e))?;

        conn.set_ex(key, serialized, seconds).await
            .map_err(|e| format!("Failed to set with expiry: {}", e))?;

        Ok(())
    }

    /// Delete key from cache
    pub async fn delete(&self, key: &str) -> Result<(), String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;

        conn.del(key).await
            .map_err(|e| format!("Failed to delete: {}", e))?;

        Ok(())
    }

    /// Check if key exists
    pub async fn exists(&self, key: &str) -> bool {
        let mut conn = match self.pool.get().await {
            Ok(c) => c,
            Err(_) => return false,
        };

        conn.exists(key).await.unwrap_or(false)
    }

    /// Increment counter
    pub async fn increment(&self, key: &str) -> Result<i64, String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;

        conn.incr(key, 1).await
            .map_err(|e| format!("Failed to increment: {}", e))
    }

    /// Decrement counter
    pub async fn decrement(&self, key: &str) -> Result<i64, String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;

        conn.decr(key, 1).await
            .map_err(|e| format!("Failed to decrement: {}", e))
    }

    /// Set hash field
    pub async fn hset<T: Serialize>(&self, key: &str, field: &str, value: &T) -> Result<(), String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;
        
        let serialized = serde_json::to_string(value)
            .map_err(|e| format!("Failed to serialize: {}", e))?;

        conn.hset(key, field, serialized).await
            .map_err(|e| format!("Failed to hset: {}", e))?;

        Ok(())
    }

    /// Get hash field
    pub async fn hget<T: DeserializeOwned>(&self, key: &str, field: &str) -> Option<T> {
        let mut conn = self.pool.get().await.ok()?;
        let result: Option<String> = conn.hget(key, field).await.ok()?;
        
        result.and_then(|v| serde_json::from_str(&v).ok())
    }

    /// Get all hash fields
    pub async fn hgetall<T: DeserializeOwned>(&self, key: &str) -> Option<std::collections::HashMap<String, T>> {
        let mut conn = self.pool.get().await.ok()?;
        let result: std::collections::HashMap<String, String> = conn.hgetall(key).await.ok()?;
        
        let mut map = std::collections::HashMap::new();
        for (k, v) in result {
            if let Ok(parsed) = serde_json::from_str(&v) {
                map.insert(k, parsed);
            }
        }
        
        Some(map)
    }

    /// Delete hash field
    pub async fn hdel(&self, key: &str, field: &str) -> Result<(), String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;

        conn.hdel(key, field).await
            .map_err(|e| format!("Failed to hdel: {}", e))?;

        Ok(())
    }

    /// Add to set
    pub async fn sadd(&self, key: &str, member: &str) -> Result<(), String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;

        conn.sadd(key, member).await
            .map_err(|e| format!("Failed to sadd: {}", e))?;

        Ok(())
    }

    /// Check if member in set
    pub async fn sismember(&self, key: &str, member: &str) -> bool {
        let mut conn = match self.pool.get().await {
            Ok(c) => c,
            Err(_) => return false,
        };

        conn.sismember(key, member).await.unwrap_or(false)
    }

    /// Get set members
    pub async fn smembers(&self, key: &str) -> Option<Vec<String>> {
        let mut conn = self.pool.get().await.ok()?;
        conn.smembers(key).await.ok()
    }

    /// Remove from set
    pub async fn srem(&self, key: &str, member: &str) -> Result<(), String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;

        conn.srem(key, member).await
            .map_err(|e| format!("Failed to srem: {}", e))?;

        Ok(())
    }

    /// Push to list
    pub async fn lpush<T: Serialize>(&self, key: &str, value: &T) -> Result<(), String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;
        
        let serialized = serde_json::to_string(value)
            .map_err(|e| format!("Failed to serialize: {}", e))?;

        conn.lpush(key, serialized).await
            .map_err(|e| format!("Failed to lpush: {}", e))?;

        Ok(())
    }

    /// Pop from list
    pub async fn rpop<T: DeserializeOwned>(&self, key: &str) -> Option<T> {
        let mut conn = self.pool.get().await.ok()?;
        let result: Option<String> = conn.rpop(key).await.ok()?;
        
        result.and_then(|v| serde_json::from_str(&v).ok())
    }

    /// Get list range
    pub async fn lrange<T: DeserializeOwned>(&self, key: &str, start: i64, stop: i64) -> Option<Vec<T>> {
        let mut conn = self.pool.get().await.ok()?;
        let result: Vec<String> = conn.lrange(key, start, stop).await.ok()?;
        
        Some(result.into_iter().filter_map(|v| serde_json::from_str(&v).ok()).collect())
    }

    /// Publish message
    pub async fn publish<T: Serialize>(&self, channel: &str, message: &T) -> Result<(), String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;
        
        let serialized = serde_json::to_string(message)
            .map_err(|e| format!("Failed to serialize: {}", e))?;

        conn.publish(channel, serialized).await
            .map_err(|e| format!("Failed to publish: {}", e))?;

        Ok(())
    }

    /// Get connection for pub/sub
    pub fn get_connection(&self) -> Result<redis::aio::Connection, String> {
        self.client
            .get_async_connection()
            .map_err(|e| format!("Failed to get connection: {}", e))
    }

    /// Cache invalidation by pattern
    pub async fn invalidate_pattern(&self, pattern: &str) -> Result<usize, String> {
        let mut conn = self.pool.get().await
            .map_err(|e| format!("Failed to get connection: {}", e))?;

        let keys: Vec<String> = redis::cmd("KEYS")
            .arg(pattern)
            .query_async(&mut conn)
            .await
            .map_err(|e| format!("Failed to scan keys: {}", e))?;

        let count = keys.len();
        
        if count > 0 {
            conn.del(&keys).await
                .map_err(|e| format!("Failed to delete keys: {}", e))?;
        }

        Ok(count)
    }

    /// Invalidate a single key
    pub async fn invalidate(&self, key: &str) -> Result<(), String> {
        self.delete(key).await
    }
}