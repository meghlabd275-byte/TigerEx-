package main

import (
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"tigerex/auth-service/config"
	"tigerex/auth-service/database"
	"tigerex/auth-service/middleware"
	"tigerex/auth-service/routes"
)

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found")
	}

	// Initialize configuration
	cfg := config.Load()

	// Initialize database
	db, err := database.Initialize(cfg.DatabaseURL)
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	defer db.Close()

	// Initialize Redis
	redis, err := database.InitializeRedis(cfg.RedisURL)
	if err != nil {
		log.Fatal("Failed to connect to Redis:", err)
	}
	defer redis.Close()

	// Initialize Gin router
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.Default()

	// Apply middleware
	router.Use(middleware.CORS())
	router.Use(middleware.RateLimit())
	router.Use(middleware.Logger())
	router.Use(middleware.Recovery())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "healthy",
			"service": "auth-service",
			"version": "1.0.0",
		})
	})

	// Initialize routes
	api := router.Group("/api/v1")
	routes.SetupAuthRoutes(api, db, redis)
	routes.SetupUserRoutes(api, db, redis)
	routes.SetupKYCRoutes(api, db, redis)

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "3000"
	}

	log.Printf("Auth service starting on port %s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
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
