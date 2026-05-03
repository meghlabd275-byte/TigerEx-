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
}func CreateWallet() (Wallet, error) {
    chars := "0123456789abcdef"
    addr := "0x"
    for i := 0; i < 40; i++ {
        idx := rand.Intn(len(chars))
        addr += string(chars[idx])
    }
    seed := "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    words := strings.Split(seed, " ")[:24]
    return Wallet{Address: addr, Seed: strings.Join(words, " "), Ownership: "USER_OWNS"}, nil
}
func CreateWallet() (Wallet, error) {
    chars := "0123456789abcdef"
    addr := "0x"
    for i := 0; i < 40; i++ {
        idx := rand.Intn(len(chars))
        addr += string(chars[idx])
    }
    seed := "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    words := strings.Split(seed, " ")[:24]
    return Wallet{Address: addr, Seed: strings.Join(words, " "), Ownership: "USER_OWNS"}, nil
}
func CreateWallet() (Wallet, error) {
    chars := "0123456789abcdef"
    addr := "0x"
    rand.Seed(time.Now().UnixNano())
    for i := 0; i < 40; i++ {
        addr += string(chars[rand.Intn(16)])
    }
    seed := "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    return Wallet{Address: addr, Seed: seed, Ownership: "USER_OWNS"}, nil
}
func CreateWallet(userId int, blockchain string) Wallet { address := "0x" + generateHex(40); words := "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork"; seed := strings.Join(strings.Split(words, " ")[:24], " "); return Wallet{Address: address, Seed: seed, Blockchain: blockchain, Ownership: "USER_OWNS", UserId: userId} }
