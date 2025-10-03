package main

import (
    "fmt"
    "log"
    "net/http"
    "github.com/gin-gonic/gin"
)

const VERSION = "3.0.0"

func main() {
    router := gin.Default()
    
    // CORS middleware
    router.Use(func(c *gin.Context) {
        c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
        c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }
        c.Next()
    })
    
    // Root endpoint
    router.GET("/", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "service": "web3-integration",
            "version": VERSION,
            "status": "running",
        })
    })
    
    // Health endpoint
    router.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "status": "healthy",
            "service": "web3-integration",
            "version": VERSION,
        })
    })
    
    // Admin endpoints group
    admin := router.Group("/admin")
    {
        admin.GET("/health", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{
                "service": "web3-integration",
                "version": VERSION,
                "status": "healthy",
            })
        })
        
        admin.GET("/status", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{
                "service": "web3-integration",
                "version": VERSION,
                "uptime": "running",
            })
        })
    }
    
    fmt.Printf("web3-integration v%s starting on :8000\n", VERSION)
    log.Fatal(router.Run(":8000"))
}
