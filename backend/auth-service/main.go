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
}