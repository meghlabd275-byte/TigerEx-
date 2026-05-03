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
