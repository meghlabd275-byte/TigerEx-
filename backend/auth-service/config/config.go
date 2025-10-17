/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

package config

import (
	"os"
	"strconv"
	"time"
)

type Config struct {
	Environment     string
	Port            string
	DatabaseURL     string
	RedisURL        string
	JWTSecret       string
	JWTExpiresIn    time.Duration
	RefreshSecret   string
	RefreshExpiresIn time.Duration
	RateLimitWindow time.Duration
	RateLimitMax    int
	EncryptionKey   string
	SMTPHost        string
	SMTPPort        int
	SMTPUser        string
	SMTPPass        string
	SMSAPIKey       string
	KYCAPIKey       string
	KYCSecret       string
}

func Load() *Config {
	cfg := &Config{
		Environment:      getEnv("NODE_ENV", "development"),
		Port:             getEnv("PORT", "3000"),
		DatabaseURL:      getEnv("DATABASE_URL", "postgres://tigerex:tigerex123@localhost:5432/tigerex?sslmode=disable"),
		RedisURL:         getEnv("REDIS_URL", "redis://localhost:6379"),
		JWTSecret:        getEnv("JWT_SECRET", "your-jwt-secret-key"),
		JWTExpiresIn:     parseDuration(getEnv("JWT_EXPIRES_IN", "24h")),
		RefreshSecret:    getEnv("REFRESH_TOKEN_SECRET", "your-refresh-token-secret"),
		RefreshExpiresIn: parseDuration(getEnv("REFRESH_TOKEN_EXPIRES_IN", "168h")), // 7 days
		RateLimitWindow:  parseDuration(getEnv("RATE_LIMIT_WINDOW_MS", "15m")),
		RateLimitMax:     parseInt(getEnv("RATE_LIMIT_MAX_REQUESTS", "100")),
		EncryptionKey:    getEnv("ENCRYPTION_KEY", "your-32-character-encryption-key"),
		SMTPHost:         getEnv("SMTP_HOST", "smtp.gmail.com"),
		SMTPPort:         parseInt(getEnv("SMTP_PORT", "587")),
		SMTPUser:         getEnv("SMTP_USER", ""),
		SMTPPass:         getEnv("SMTP_PASS", ""),
		SMSAPIKey:        getEnv("SMS_PROVIDER_API_KEY", ""),
		KYCAPIKey:        getEnv("KYC_PROVIDER_API_KEY", ""),
		KYCSecret:        getEnv("KYC_PROVIDER_SECRET", ""),
	}

	return cfg
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func parseInt(s string) int {
	i, err := strconv.Atoi(s)
	if err != nil {
		return 0
	}
	return i
}

func parseDuration(s string) time.Duration {
	d, err := time.ParseDuration(s)
	if err != nil {
		return time.Hour
	}
	return d
}