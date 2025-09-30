package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/ethereum/go-ethereum/accounts/keystore"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
	"github.com/google/uuid"
	"github.com/gorilla/websocket"
	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// Models
type Wallet struct {
	ID                  uuid.UUID `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	UserID              uuid.UUID `json:"user_id" gorm:"type:uuid;not null"`
	CurrencyID          uuid.UUID `json:"currency_id" gorm:"type:uuid;not null"`
	WalletType          string    `json:"wallet_type" gorm:"type:varchar(20);default:'hot'"`
	Address             string    `json:"address" gorm:"type:varchar(255)"`
	PrivateKeyEncrypted string    `json:"-" gorm:"type:text"`
	Balance             float64   `json:"balance" gorm:"type:decimal(30,8);default:0"`
	LockedBalance       float64   `json:"locked_balance" gorm:"type:decimal(30,8);default:0"`
	IsActive            bool      `json:"is_active" gorm:"default:true"`
	CreatedAt           time.Time `json:"created_at"`
	UpdatedAt           time.Time `json:"updated_at"`
}

type Transaction struct {
	ID                     uuid.UUID `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	UserID                 uuid.UUID `json:"user_id" gorm:"type:uuid;not null"`
	CurrencyID             uuid.UUID `json:"currency_id" gorm:"type:uuid;not null"`
	TransactionType        string    `json:"transaction_type" gorm:"type:varchar(20);not null"`
	Status                 string    `json:"status" gorm:"type:varchar(20);default:'pending'"`
	Amount                 float64   `json:"amount" gorm:"type:decimal(30,8);not null"`
	Fee                    float64   `json:"fee" gorm:"type:decimal(30,8);default:0"`
	FromAddress            string    `json:"from_address" gorm:"type:varchar(255)"`
	ToAddress              string    `json:"to_address" gorm:"type:varchar(255)"`
	TxHash                 string    `json:"tx_hash" gorm:"type:varchar(255)"`
	BlockNumber            int64     `json:"block_number"`
	Confirmations          int       `json:"confirmations" gorm:"default:0"`
	RequiredConfirmations  int       `json:"required_confirmations" gorm:"default:6"`
	ReferenceID            uuid.UUID `json:"reference_id" gorm:"type:uuid"`
	Notes                  string    `json:"notes" gorm:"type:text"`
	CreatedAt              time.Time `json:"created_at"`
	UpdatedAt              time.Time `json:"updated_at"`
	ConfirmedAt            *time.Time `json:"confirmed_at"`
}

type WalletBalance struct {
	CurrencySymbol    string  `json:"currency_symbol"`
	Balance           float64 `json:"balance"`
	LockedBalance     float64 `json:"locked_balance"`
	AvailableBalance  float64 `json:"available_balance"`
	USDValue          float64 `json:"usd_value"`
}

type DepositAddress struct {
	Address string `json:"address"`
	Network string `json:"network"`
	QRCode  string `json:"qr_code"`
}

type WithdrawalRequest struct {
	CurrencyID uuid.UUID `json:"currency_id" binding:"required"`
	Amount     float64   `json:"amount" binding:"required,gt=0"`
	ToAddress  string    `json:"to_address" binding:"required"`
	Network    string    `json:"network"`
	TwoFACode  string    `json:"two_fa_code"`
}

type WalletService struct {
	db          *gorm.DB
	redis       *redis.Client
	ethClient   *ethclient.Client
	keystore    *keystore.KeyStore
	upgrader    websocket.Upgrader
}

// Initialize service
func NewWalletService() *WalletService {
	// Load environment variables
	godotenv.Load()

	// Database connection
	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=disable",
		os.Getenv("DB_HOST"), os.Getenv("DB_USER"), os.Getenv("DB_PASSWORD"),
		os.Getenv("DB_NAME"), os.Getenv("DB_PORT"))
	
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}

	// Redis connection
	rdb := redis.NewClient(&redis.Options{
		Addr:     os.Getenv("REDIS_ADDR"),
		Password: os.Getenv("REDIS_PASSWORD"),
		DB:       0,
	})

	// Ethereum client
	ethClient, err := ethclient.Dial(os.Getenv("ETHEREUM_RPC_URL"))
	if err != nil {
		log.Printf("Failed to connect to Ethereum client: %v", err)
	}

	// Keystore for wallet management
	ks := keystore.NewKeyStore("./keystore", keystore.StandardScryptN, keystore.StandardScryptP)

	return &WalletService{
		db:        db,
		redis:     rdb,
		ethClient: ethClient,
		keystore:  ks,
		upgrader: websocket.Upgrader{
			CheckOrigin: func(r *http.Request) bool {
				return true
			},
		},
	}
}

// Wallet Management Endpoints

func (ws *WalletService) GetWalletBalances(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var balances []WalletBalance
	query := `
		SELECT 
			cr.symbol as currency_symbol,
			COALESCE(w.balance, 0) as balance,
			COALESCE(w.locked_balance, 0) as locked_balance,
			COALESCE(w.balance, 0) - COALESCE(w.locked_balance, 0) as available_balance,
			COALESCE(w.balance, 0) * COALESCE(md.last_price, 0) as usd_value
		FROM cryptocurrencies cr
		LEFT JOIN wallets w ON cr.id = w.currency_id AND w.user_id = ?
		LEFT JOIN trading_pairs tp ON cr.id = tp.base_currency_id
		LEFT JOIN market_data md ON tp.id = md.trading_pair_id
		WHERE cr.is_active = true
		ORDER BY usd_value DESC
	`

	if err := ws.db.Raw(query, userID).Scan(&balances).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch balances"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"balances": balances})
}

func (ws *WalletService) GetDepositAddress(c *gin.Context) {
	userID := c.GetString("user_id")
	currencyID := c.Param("currency_id")
	network := c.DefaultQuery("network", "ethereum")

	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	// Check if wallet exists
	var wallet Wallet
	if err := ws.db.Where("user_id = ? AND currency_id = ? AND wallet_type = 'hot'", 
		userID, currencyID).First(&wallet).Error; err != nil {
		// Create new wallet if doesn't exist
		wallet = ws.createHotWallet(userID, currencyID)
	}

	depositAddr := DepositAddress{
		Address: wallet.Address,
		Network: network,
		QRCode:  fmt.Sprintf("data:image/png;base64,%s", ws.generateQRCode(wallet.Address)),
	}

	c.JSON(http.StatusOK, depositAddr)
}

func (ws *WalletService) CreateWithdrawal(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var req WithdrawalRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Verify 2FA if enabled
	if !ws.verify2FA(userID, req.TwoFACode) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid 2FA code"})
		return
	}

	// Check wallet balance
	var wallet Wallet
	if err := ws.db.Where("user_id = ? AND currency_id = ?", userID, req.CurrencyID).First(&wallet).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Wallet not found"})
		return
	}

	availableBalance := wallet.Balance - wallet.LockedBalance
	if availableBalance < req.Amount {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Insufficient balance"})
		return
	}

	// Create withdrawal transaction
	transaction := Transaction{
		ID:                    uuid.New(),
		UserID:                uuid.MustParse(userID),
		CurrencyID:            req.CurrencyID,
		TransactionType:       "withdrawal",
		Status:                "pending",
		Amount:                req.Amount,
		Fee:                   ws.calculateWithdrawalFee(req.CurrencyID, req.Amount),
		ToAddress:             req.ToAddress,
		RequiredConfirmations: 6,
		CreatedAt:             time.Now(),
		UpdatedAt:             time.Now(),
	}

	// Lock funds
	wallet.LockedBalance += req.Amount + transaction.Fee
	
	tx := ws.db.Begin()
	if err := tx.Save(&wallet).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to lock funds"})
		return
	}

	if err := tx.Create(&transaction).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create withdrawal"})
		return
	}

	tx.Commit()

	// Process withdrawal asynchronously
	go ws.processWithdrawal(transaction.ID)

	c.JSON(http.StatusOK, gin.H{
		"transaction_id": transaction.ID,
		"status":         "pending",
		"message":        "Withdrawal request submitted successfully",
	})
}

func (ws *WalletService) GetTransactionHistory(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))
	transactionType := c.Query("type")
	currencyID := c.Query("currency_id")

	offset := (page - 1) * limit

	query := ws.db.Where("user_id = ?", userID)
	
	if transactionType != "" {
		query = query.Where("transaction_type = ?", transactionType)
	}
	
	if currencyID != "" {
		query = query.Where("currency_id = ?", currencyID)
	}

	var transactions []Transaction
	var total int64

	query.Model(&Transaction{}).Count(&total)
	query.Order("created_at DESC").Limit(limit).Offset(offset).Find(&transactions)

	c.JSON(http.StatusOK, gin.H{
		"transactions": transactions,
		"pagination": gin.H{
			"page":       page,
			"limit":      limit,
			"total":      total,
			"total_pages": (total + int64(limit) - 1) / int64(limit),
		},
	})
}

// Advanced Wallet Features

func (ws *WalletService) CreateColdWallet(c *gin.Context) {
	userID := c.GetString("user_id")
	currencyID := c.Param("currency_id")

	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	// Generate cold wallet (offline)
	privateKey, err := crypto.GenerateKey()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate private key"})
		return
	}

	address := crypto.PubkeyToAddress(privateKey.PublicKey).Hex()
	
	// Encrypt private key
	encryptedKey, err := ws.encryptPrivateKey(hex.EncodeToString(crypto.FromECDSA(privateKey)))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to encrypt private key"})
		return
	}

	wallet := Wallet{
		ID:                  uuid.New(),
		UserID:              uuid.MustParse(userID),
		CurrencyID:          uuid.MustParse(currencyID),
		WalletType:          "cold",
		Address:             address,
		PrivateKeyEncrypted: encryptedKey,
		Balance:             0,
		LockedBalance:       0,
		IsActive:            true,
		CreatedAt:           time.Now(),
		UpdatedAt:           time.Now(),
	}

	if err := ws.db.Create(&wallet).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create cold wallet"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"wallet_id": wallet.ID,
		"address":   wallet.Address,
		"type":      "cold",
		"message":   "Cold wallet created successfully",
	})
}

func (ws *WalletService) ImportWallet(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var req struct {
		CurrencyID  uuid.UUID `json:"currency_id" binding:"required"`
		PrivateKey  string    `json:"private_key" binding:"required"`
		WalletType  string    `json:"wallet_type" binding:"required"`
		Password    string    `json:"password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Validate private key and derive address
	privateKey, err := crypto.HexToECDSA(req.PrivateKey)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid private key"})
		return
	}

	address := crypto.PubkeyToAddress(privateKey.PublicKey).Hex()

	// Encrypt private key
	encryptedKey, err := ws.encryptPrivateKey(req.PrivateKey)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to encrypt private key"})
		return
	}

	wallet := Wallet{
		ID:                  uuid.New(),
		UserID:              uuid.MustParse(userID),
		CurrencyID:          req.CurrencyID,
		WalletType:          req.WalletType,
		Address:             address,
		PrivateKeyEncrypted: encryptedKey,
		Balance:             0,
		LockedBalance:       0,
		IsActive:            true,
		CreatedAt:           time.Now(),
		UpdatedAt:           time.Now(),
	}

	if err := ws.db.Create(&wallet).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to import wallet"})
		return
	}

	// Sync wallet balance
	go ws.syncWalletBalance(wallet.ID)

	c.JSON(http.StatusOK, gin.H{
		"wallet_id": wallet.ID,
		"address":   wallet.Address,
		"type":      wallet.WalletType,
		"message":   "Wallet imported successfully",
	})
}

// White-label Wallet Creation
func (ws *WalletService) CreateWhiteLabelWallet(c *gin.Context) {
	var req struct {
		Name        string `json:"name" binding:"required"`
		Type        string `json:"type" binding:"required"` // "trust_wallet", "metamask"
		Features    []string `json:"features"`
		Branding    map[string]interface{} `json:"branding"`
		Networks    []string `json:"networks"`
		DomainName  string `json:"domain_name"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Generate wallet configuration
	walletConfig := map[string]interface{}{
		"id":          uuid.New(),
		"name":        req.Name,
		"type":        req.Type,
		"features":    req.Features,
		"branding":    req.Branding,
		"networks":    req.Networks,
		"domain_name": req.DomainName,
		"created_at":  time.Now(),
		"status":      "deploying",
	}

	// Store configuration
	configJSON, _ := json.Marshal(walletConfig)
	ws.redis.Set(context.Background(), fmt.Sprintf("white_label_wallet:%s", walletConfig["id"]), configJSON, 0)

	// Deploy wallet asynchronously
	go ws.deployWhiteLabelWallet(walletConfig)

	c.JSON(http.StatusOK, gin.H{
		"wallet_id": walletConfig["id"],
		"status":    "deploying",
		"message":   "White-label wallet deployment initiated",
	})
}

// Helper functions
func (ws *WalletService) createHotWallet(userID, currencyID string) Wallet {
	privateKey, _ := crypto.GenerateKey()
	address := crypto.PubkeyToAddress(privateKey.PublicKey).Hex()
	encryptedKey, _ := ws.encryptPrivateKey(hex.EncodeToString(crypto.FromECDSA(privateKey)))

	wallet := Wallet{
		ID:                  uuid.New(),
		UserID:              uuid.MustParse(userID),
		CurrencyID:          uuid.MustParse(currencyID),
		WalletType:          "hot",
		Address:             address,
		PrivateKeyEncrypted: encryptedKey,
		Balance:             0,
		LockedBalance:       0,
		IsActive:            true,
		CreatedAt:           time.Now(),
		UpdatedAt:           time.Now(),
	}

	ws.db.Create(&wallet)
	return wallet
}

func (ws *WalletService) encryptPrivateKey(privateKey string) (string, error) {
	// Implement AES encryption
	key := []byte(os.Getenv("ENCRYPTION_KEY"))
	// Simplified - use proper AES encryption in production
	return privateKey, nil
}

func (ws *WalletService) verify2FA(userID, code string) bool {
	// Implement 2FA verification
	return true // Simplified for demo
}

func (ws *WalletService) calculateWithdrawalFee(currencyID uuid.UUID, amount float64) float64 {
	// Implement dynamic fee calculation
	return amount * 0.001 // 0.1% fee
}

func (ws *WalletService) processWithdrawal(transactionID uuid.UUID) {
	// Implement withdrawal processing
	time.Sleep(5 * time.Second) // Simulate processing time
	
	var transaction Transaction
	ws.db.First(&transaction, "id = ?", transactionID)
	
	// Update transaction status
	transaction.Status = "confirmed"
	transaction.TxHash = "0x" + hex.EncodeToString([]byte(uuid.New().String()))
	now := time.Now()
	transaction.ConfirmedAt = &now
	
	ws.db.Save(&transaction)
}

func (ws *WalletService) syncWalletBalance(walletID uuid.UUID) {
	// Implement balance synchronization with blockchain
}

func (ws *WalletService) generateQRCode(address string) string {
	// Implement QR code generation
	return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
}

func (ws *WalletService) deployWhiteLabelWallet(config map[string]interface{}) {
	// Implement white-label wallet deployment
	time.Sleep(30 * time.Second) // Simulate deployment time
	
	// Update status
	config["status"] = "deployed"
	config["url"] = fmt.Sprintf("https://%s.tigerex-wallets.com", config["domain_name"])
	
	configJSON, _ := json.Marshal(config)
	ws.redis.Set(context.Background(), fmt.Sprintf("white_label_wallet:%s", config["id"]), configJSON, 0)
}

// WebSocket for real-time updates
func (ws *WalletService) HandleWebSocket(c *gin.Context) {
	conn, err := ws.upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		return
	}
	defer conn.Close()

	userID := c.GetString("user_id")
	
	// Subscribe to user's wallet updates
	pubsub := ws.redis.Subscribe(context.Background(), fmt.Sprintf("wallet_updates:%s", userID))
	defer pubsub.Close()

	ch := pubsub.Channel()
	
	for msg := range ch {
		if err := conn.WriteMessage(websocket.TextMessage, []byte(msg.Payload)); err != nil {
			log.Printf("WebSocket write error: %v", err)
			break
		}
	}
}

func main() {
	ws := NewWalletService()

	r := gin.Default()
	
	// CORS middleware
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"*"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "healthy", "service": "wallet-service"})
	})

	// API routes
	api := r.Group("/api/v1")
	{
		// Wallet management
		api.GET("/wallets/balances", ws.GetWalletBalances)
		api.GET("/wallets/deposit/:currency_id", ws.GetDepositAddress)
		api.POST("/wallets/withdraw", ws.CreateWithdrawal)
		api.GET("/wallets/transactions", ws.GetTransactionHistory)
		
		// Advanced wallet features
		api.POST("/wallets/cold/:currency_id", ws.CreateColdWallet)
		api.POST("/wallets/import", ws.ImportWallet)
		
		// White-label solutions
		api.POST("/white-label/wallet", ws.CreateWhiteLabelWallet)
		
		// WebSocket
		api.GET("/ws", ws.HandleWebSocket)
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "3003"
	}

	log.Printf("Wallet Service starting on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, r))
}