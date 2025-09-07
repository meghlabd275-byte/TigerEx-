package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

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
type P2POrder struct {
	ID                uuid.UUID `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	UserID            uuid.UUID `json:"user_id" gorm:"type:uuid;not null"`
	CurrencyID        uuid.UUID `json:"currency_id" gorm:"type:uuid;not null"`
	FiatCurrency      string    `json:"fiat_currency" gorm:"type:varchar(3);not null"`
	OrderType         string    `json:"order_type" gorm:"type:varchar(10);not null"` // 'buy' or 'sell'
	Status            string    `json:"status" gorm:"type:varchar(20);default:'active'"`
	Quantity          float64   `json:"quantity" gorm:"type:decimal(20,8);not null"`
	RemainingQuantity float64   `json:"remaining_quantity" gorm:"type:decimal(20,8)"`
	Price             float64   `json:"price" gorm:"type:decimal(20,8);not null"`
	MinAmount         float64   `json:"min_amount" gorm:"type:decimal(20,2)"`
	MaxAmount         float64   `json:"max_amount" gorm:"type:decimal(20,2)"`
	PaymentMethods    string    `json:"payment_methods" gorm:"type:jsonb"`
	Terms             string    `json:"terms" gorm:"type:text"`
	AutoReply         string    `json:"auto_reply" gorm:"type:text"`
	TimeLimit         int       `json:"time_limit" gorm:"default:30"` // minutes
	CreatedAt         time.Time `json:"created_at"`
	UpdatedAt         time.Time `json:"updated_at"`
	
	// Relations
	User     User           `json:"user,omitempty" gorm:"foreignKey:UserID"`
	Currency Cryptocurrency `json:"currency,omitempty" gorm:"foreignKey:CurrencyID"`
}

type P2PTrade struct {
	ID              uuid.UUID `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	OrderID         uuid.UUID `json:"order_id" gorm:"type:uuid;not null"`
	BuyerID         uuid.UUID `json:"buyer_id" gorm:"type:uuid;not null"`
	SellerID        uuid.UUID `json:"seller_id" gorm:"type:uuid;not null"`
	Quantity        float64   `json:"quantity" gorm:"type:decimal(20,8);not null"`
	Price           float64   `json:"price" gorm:"type:decimal(20,8);not null"`
	TotalAmount     float64   `json:"total_amount" gorm:"type:decimal(20,2);not null"`
	FiatCurrency    string    `json:"fiat_currency" gorm:"type:varchar(3);not null"`
	PaymentMethod   string    `json:"payment_method" gorm:"type:varchar(50)"`
	Status          string    `json:"status" gorm:"type:varchar(20);default:'pending'"`
	PaymentDeadline time.Time `json:"payment_deadline"`
	ChatMessages    string    `json:"chat_messages" gorm:"type:jsonb"`
	DisputeReason   string    `json:"dispute_reason" gorm:"type:text"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       time.Time `json:"updated_at"`
	CompletedAt     *time.Time `json:"completed_at"`
	
	// Relations
	Order  P2POrder `json:"order,omitempty" gorm:"foreignKey:OrderID"`
	Buyer  User     `json:"buyer,omitempty" gorm:"foreignKey:BuyerID"`
	Seller User     `json:"seller,omitempty" gorm:"foreignKey:SellerID"`
}

type P2PDispute struct {
	ID          uuid.UUID  `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	TradeID     uuid.UUID  `json:"trade_id" gorm:"type:uuid;not null"`
	InitiatorID uuid.UUID  `json:"initiator_id" gorm:"type:uuid;not null"`
	Reason      string     `json:"reason" gorm:"type:text;not null"`
	Evidence    string     `json:"evidence" gorm:"type:jsonb"`
	Status      string     `json:"status" gorm:"type:varchar(20);default:'open'"`
	Resolution  string     `json:"resolution" gorm:"type:text"`
	ResolvedBy  *uuid.UUID `json:"resolved_by" gorm:"type:uuid"`
	ResolvedAt  *time.Time `json:"resolved_at"`
	CreatedAt   time.Time  `json:"created_at"`
	UpdatedAt   time.Time  `json:"updated_at"`
}

type P2PPaymentMethod struct {
	ID          uuid.UUID `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	UserID      uuid.UUID `json:"user_id" gorm:"type:uuid;not null"`
	Name        string    `json:"name" gorm:"type:varchar(100);not null"`
	Type        string    `json:"type" gorm:"type:varchar(50);not null"`
	Details     string    `json:"details" gorm:"type:jsonb"`
	IsActive    bool      `json:"is_active" gorm:"default:true"`
	IsVerified  bool      `json:"is_verified" gorm:"default:false"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

type ChatMessage struct {
	ID        uuid.UUID `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()"`
	TradeID   uuid.UUID `json:"trade_id" gorm:"type:uuid;not null"`
	SenderID  uuid.UUID `json:"sender_id" gorm:"type:uuid;not null"`
	Message   string    `json:"message" gorm:"type:text;not null"`
	MessageType string  `json:"message_type" gorm:"type:varchar(20);default:'text'"`
	IsRead    bool      `json:"is_read" gorm:"default:false"`
	CreatedAt time.Time `json:"created_at"`
}

// Request/Response models
type CreateP2POrderRequest struct {
	CurrencyID     uuid.UUID `json:"currency_id" binding:"required"`
	FiatCurrency   string    `json:"fiat_currency" binding:"required"`
	OrderType      string    `json:"order_type" binding:"required"`
	Quantity       float64   `json:"quantity" binding:"required,gt=0"`
	Price          float64   `json:"price" binding:"required,gt=0"`
	MinAmount      float64   `json:"min_amount" binding:"required,gt=0"`
	MaxAmount      float64   `json:"max_amount" binding:"required,gt=0"`
	PaymentMethods []string  `json:"payment_methods" binding:"required"`
	Terms          string    `json:"terms"`
	AutoReply      string    `json:"auto_reply"`
	TimeLimit      int       `json:"time_limit"`
}

type CreateP2PTradeRequest struct {
	OrderID       uuid.UUID `json:"order_id" binding:"required"`
	Quantity      float64   `json:"quantity" binding:"required,gt=0"`
	PaymentMethod string    `json:"payment_method" binding:"required"`
	Message       string    `json:"message"`
}

type P2PService struct {
	db       *gorm.DB
	redis    *redis.Client
	upgrader websocket.Upgrader
}

func NewP2PService() *P2PService {
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

	return &P2PService{
		db:    db,
		redis: rdb,
		upgrader: websocket.Upgrader{
			CheckOrigin: func(r *http.Request) bool {
				return true
			},
		},
	}
}

// P2P Order Management
func (p *P2PService) CreateP2POrder(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var req CreateP2POrderRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Validate order type
	if req.OrderType != "buy" && req.OrderType != "sell" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid order type"})
		return
	}

	// Validate amounts
	if req.MinAmount > req.MaxAmount {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Min amount cannot be greater than max amount"})
		return
	}

	// For sell orders, check if user has sufficient balance
	if req.OrderType == "sell" {
		if !p.checkUserBalance(userID, req.CurrencyID, req.Quantity) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Insufficient balance"})
			return
		}
	}

	// Convert payment methods to JSON
	paymentMethodsJSON, _ := json.Marshal(req.PaymentMethods)

	order := P2POrder{
		ID:                uuid.New(),
		UserID:            uuid.MustParse(userID),
		CurrencyID:        req.CurrencyID,
		FiatCurrency:      req.FiatCurrency,
		OrderType:         req.OrderType,
		Status:            "active",
		Quantity:          req.Quantity,
		RemainingQuantity: req.Quantity,
		Price:             req.Price,
		MinAmount:         req.MinAmount,
		MaxAmount:         req.MaxAmount,
		PaymentMethods:    string(paymentMethodsJSON),
		Terms:             req.Terms,
		AutoReply:         req.AutoReply,
		TimeLimit:         req.TimeLimit,
		CreatedAt:         time.Now(),
		UpdatedAt:         time.Now(),
	}

	if err := p.db.Create(&order).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create order"})
		return
	}

	// Lock funds for sell orders
	if req.OrderType == "sell" {
		p.lockUserFunds(userID, req.CurrencyID, req.Quantity)
	}

	// Broadcast new order to WebSocket clients
	p.broadcastOrderUpdate(order, "created")

	c.JSON(http.StatusOK, gin.H{
		"order_id": order.ID,
		"message":  "P2P order created successfully",
	})
}

func (p *P2PService) GetP2POrders(c *gin.Context) {
	orderType := c.Query("type")
	fiatCurrency := c.Query("fiat_currency")
	currencyID := c.Query("currency_id")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))
	offset := (page - 1) * limit

	query := p.db.Model(&P2POrder{}).Where("status = ?", "active")

	if orderType != "" {
		query = query.Where("order_type = ?", orderType)
	}
	if fiatCurrency != "" {
		query = query.Where("fiat_currency = ?", fiatCurrency)
	}
	if currencyID != "" {
		query = query.Where("currency_id = ?", currencyID)
	}

	var orders []P2POrder
	var total int64

	query.Count(&total)
	query.Preload("User").Preload("Currency").
		Order("created_at DESC").
		Limit(limit).Offset(offset).
		Find(&orders)

	c.JSON(http.StatusOK, gin.H{
		"orders": orders,
		"pagination": gin.H{
			"page":        page,
			"limit":       limit,
			"total":       total,
			"total_pages": (total + int64(limit) - 1) / int64(limit),
		},
	})
}

func (p *P2PService) GetUserP2POrders(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	status := c.DefaultQuery("status", "all")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))
	offset := (page - 1) * limit

	query := p.db.Model(&P2POrder{}).Where("user_id = ?", userID)

	if status != "all" {
		query = query.Where("status = ?", status)
	}

	var orders []P2POrder
	var total int64

	query.Count(&total)
	query.Preload("Currency").
		Order("created_at DESC").
		Limit(limit).Offset(offset).
		Find(&orders)

	c.JSON(http.StatusOK, gin.H{
		"orders": orders,
		"pagination": gin.H{
			"page":        page,
			"limit":       limit,
			"total":       total,
			"total_pages": (total + int64(limit) - 1) / int64(limit),
		},
	})
}

// P2P Trade Management
func (p *P2PService) CreateP2PTrade(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var req CreateP2PTradeRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get the order
	var order P2POrder
	if err := p.db.First(&order, "id = ? AND status = ?", req.OrderID, "active").Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Order not found or inactive"})
		return
	}

	// Check if user is trying to trade with their own order
	if order.UserID.String() == userID {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Cannot trade with your own order"})
		return
	}

	// Check if quantity is available
	if req.Quantity > order.RemainingQuantity {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Insufficient quantity available"})
		return
	}

	// Calculate total amount
	totalAmount := req.Quantity * order.Price

	// Check min/max limits
	if totalAmount < order.MinAmount || totalAmount > order.MaxAmount {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": fmt.Sprintf("Amount must be between %.2f and %.2f %s", 
				order.MinAmount, order.MaxAmount, order.FiatCurrency),
		})
		return
	}

	// Determine buyer and seller
	var buyerID, sellerID uuid.UUID
	if order.OrderType == "sell" {
		buyerID = uuid.MustParse(userID)
		sellerID = order.UserID
	} else {
		buyerID = order.UserID
		sellerID = uuid.MustParse(userID)
	}

	// Check buyer's balance for buy orders
	if order.OrderType == "buy" && !p.checkUserBalance(userID, order.CurrencyID, req.Quantity) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Insufficient balance"})
		return
	}

	// Create trade
	trade := P2PTrade{
		ID:              uuid.New(),
		OrderID:         req.OrderID,
		BuyerID:         buyerID,
		SellerID:        sellerID,
		Quantity:        req.Quantity,
		Price:           order.Price,
		TotalAmount:     totalAmount,
		FiatCurrency:    order.FiatCurrency,
		PaymentMethod:   req.PaymentMethod,
		Status:          "pending",
		PaymentDeadline: time.Now().Add(time.Duration(order.TimeLimit) * time.Minute),
		CreatedAt:       time.Now(),
		UpdatedAt:       time.Now(),
	}

	tx := p.db.Begin()

	// Create trade
	if err := tx.Create(&trade).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create trade"})
		return
	}

	// Update order remaining quantity
	order.RemainingQuantity -= req.Quantity
	if order.RemainingQuantity <= 0 {
		order.Status = "completed"
	}
	if err := tx.Save(&order).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update order"})
		return
	}

	// Lock funds
	if order.OrderType == "buy" {
		p.lockUserFunds(userID, order.CurrencyID, req.Quantity)
	}

	tx.Commit()

	// Send initial message if provided
	if req.Message != "" {
		p.sendChatMessage(trade.ID, uuid.MustParse(userID), req.Message, "text")
	}

	// Send auto-reply from order creator
	if order.AutoReply != "" {
		p.sendChatMessage(trade.ID, order.UserID, order.AutoReply, "auto_reply")
	}

	// Broadcast trade update
	p.broadcastTradeUpdate(trade, "created")

	c.JSON(http.StatusOK, gin.H{
		"trade_id": trade.ID,
		"message":  "P2P trade created successfully",
	})
}

func (p *P2PService) GetUserP2PTrades(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	status := c.DefaultQuery("status", "all")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))
	offset := (page - 1) * limit

	query := p.db.Model(&P2PTrade{}).Where("buyer_id = ? OR seller_id = ?", userID, userID)

	if status != "all" {
		query = query.Where("status = ?", status)
	}

	var trades []P2PTrade
	var total int64

	query.Count(&total)
	query.Preload("Order").Preload("Order.Currency").
		Preload("Buyer").Preload("Seller").
		Order("created_at DESC").
		Limit(limit).Offset(offset).
		Find(&trades)

	c.JSON(http.StatusOK, gin.H{
		"trades": trades,
		"pagination": gin.H{
			"page":        page,
			"limit":       limit,
			"total":       total,
			"total_pages": (total + int64(limit) - 1) / int64(limit),
		},
	})
}

// Trade Actions
func (p *P2PService) MarkPaymentSent(c *gin.Context) {
	userID := c.GetString("user_id")
	tradeID := c.Param("trade_id")

	var trade P2PTrade
	if err := p.db.First(&trade, "id = ?", tradeID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Trade not found"})
		return
	}

	// Only buyer can mark payment as sent
	if trade.BuyerID.String() != userID {
		c.JSON(http.StatusForbidden, gin.H{"error": "Only buyer can mark payment as sent"})
		return
	}

	if trade.Status != "pending" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid trade status"})
		return
	}

	trade.Status = "payment_sent"
	trade.UpdatedAt = time.Now()

	if err := p.db.Save(&trade).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update trade"})
		return
	}

	// Send notification to seller
	p.sendTradeNotification(trade.SellerID, trade.ID, "payment_sent")

	// Broadcast update
	p.broadcastTradeUpdate(trade, "payment_sent")

	c.JSON(http.StatusOK, gin.H{"message": "Payment marked as sent"})
}

func (p *P2PService) ConfirmPaymentReceived(c *gin.Context) {
	userID := c.GetString("user_id")
	tradeID := c.Param("trade_id")

	var trade P2PTrade
	if err := p.db.First(&trade, "id = ?", tradeID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Trade not found"})
		return
	}

	// Only seller can confirm payment received
	if trade.SellerID.String() != userID {
		c.JSON(http.StatusForbidden, gin.H{"error": "Only seller can confirm payment received"})
		return
	}

	if trade.Status != "payment_sent" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid trade status"})
		return
	}

	// Complete the trade
	now := time.Now()
	trade.Status = "completed"
	trade.UpdatedAt = now
	trade.CompletedAt = &now

	tx := p.db.Begin()

	if err := tx.Save(&trade).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update trade"})
		return
	}

	// Transfer funds
	if err := p.transferFunds(trade); err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to transfer funds"})
		return
	}

	tx.Commit()

	// Send notifications
	p.sendTradeNotification(trade.BuyerID, trade.ID, "completed")
	p.sendTradeNotification(trade.SellerID, trade.ID, "completed")

	// Broadcast update
	p.broadcastTradeUpdate(trade, "completed")

	c.JSON(http.StatusOK, gin.H{"message": "Trade completed successfully"})
}

func (p *P2PService) CreateDispute(c *gin.Context) {
	userID := c.GetString("user_id")
	tradeID := c.Param("trade_id")

	var req struct {
		Reason   string                 `json:"reason" binding:"required"`
		Evidence map[string]interface{} `json:"evidence"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var trade P2PTrade
	if err := p.db.First(&trade, "id = ?", tradeID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Trade not found"})
		return
	}

	// Check if user is part of the trade
	if trade.BuyerID.String() != userID && trade.SellerID.String() != userID {
		c.JSON(http.StatusForbidden, gin.H{"error": "Access denied"})
		return
	}

	// Check if trade can be disputed
	if trade.Status == "completed" || trade.Status == "cancelled" || trade.Status == "disputed" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Trade cannot be disputed"})
		return
	}

	evidenceJSON, _ := json.Marshal(req.Evidence)

	dispute := P2PDispute{
		ID:          uuid.New(),
		TradeID:     trade.ID,
		InitiatorID: uuid.MustParse(userID),
		Reason:      req.Reason,
		Evidence:    string(evidenceJSON),
		Status:      "open",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	tx := p.db.Begin()

	// Create dispute
	if err := tx.Create(&dispute).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create dispute"})
		return
	}

	// Update trade status
	trade.Status = "disputed"
	trade.DisputeReason = req.Reason
	trade.UpdatedAt = time.Now()

	if err := tx.Save(&trade).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update trade"})
		return
	}

	tx.Commit()

	// Notify admin and other party
	otherPartyID := trade.BuyerID
	if trade.BuyerID.String() == userID {
		otherPartyID = trade.SellerID
	}

	p.sendDisputeNotification(otherPartyID, dispute.ID, "created")
	p.notifyAdminDispute(dispute.ID)

	c.JSON(http.StatusOK, gin.H{
		"dispute_id": dispute.ID,
		"message":    "Dispute created successfully",
	})
}

// Chat System
func (p *P2PService) SendChatMessage(c *gin.Context) {
	userID := c.GetString("user_id")
	tradeID := c.Param("trade_id")

	var req struct {
		Message string `json:"message" binding:"required"`
		Type    string `json:"type"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Verify user is part of the trade
	var trade P2PTrade
	if err := p.db.First(&trade, "id = ?", tradeID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Trade not found"})
		return
	}

	if trade.BuyerID.String() != userID && trade.SellerID.String() != userID {
		c.JSON(http.StatusForbidden, gin.H{"error": "Access denied"})
		return
	}

	messageType := req.Type
	if messageType == "" {
		messageType = "text"
	}

	messageID := p.sendChatMessage(trade.ID, uuid.MustParse(userID), req.Message, messageType)

	c.JSON(http.StatusOK, gin.H{
		"message_id": messageID,
		"message":    "Message sent successfully",
	})
}

func (p *P2PService) GetChatMessages(c *gin.Context) {
	userID := c.GetString("user_id")
	tradeID := c.Param("trade_id")

	// Verify user is part of the trade
	var trade P2PTrade
	if err := p.db.First(&trade, "id = ?", tradeID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Trade not found"})
		return
	}

	if trade.BuyerID.String() != userID && trade.SellerID.String() != userID {
		c.JSON(http.StatusForbidden, gin.H{"error": "Access denied"})
		return
	}

	var messages []ChatMessage
	p.db.Where("trade_id = ?", tradeID).
		Order("created_at ASC").
		Find(&messages)

	// Mark messages as read
	p.db.Model(&ChatMessage{}).
		Where("trade_id = ? AND sender_id != ? AND is_read = false", tradeID, userID).
		Update("is_read", true)

	c.JSON(http.StatusOK, gin.H{"messages": messages})
}

// Payment Methods
func (p *P2PService) GetPaymentMethods(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var paymentMethods []P2PPaymentMethod
	p.db.Where("user_id = ? AND is_active = true", userID).
		Order("created_at DESC").
		Find(&paymentMethods)

	c.JSON(http.StatusOK, gin.H{"payment_methods": paymentMethods})
}

func (p *P2PService) AddPaymentMethod(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var req struct {
		Name    string                 `json:"name" binding:"required"`
		Type    string                 `json:"type" binding:"required"`
		Details map[string]interface{} `json:"details" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	detailsJSON, _ := json.Marshal(req.Details)

	paymentMethod := P2PPaymentMethod{
		ID:        uuid.New(),
		UserID:    uuid.MustParse(userID),
		Name:      req.Name,
		Type:      req.Type,
		Details:   string(detailsJSON),
		IsActive:  true,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	if err := p.db.Create(&paymentMethod).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to add payment method"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"payment_method_id": paymentMethod.ID,
		"message":           "Payment method added successfully",
	})
}

// WebSocket for real-time updates
func (p *P2PService) HandleWebSocket(c *gin.Context) {
	conn, err := p.upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		return
	}
	defer conn.Close()

	userID := c.GetString("user_id")
	
	// Subscribe to user's P2P updates
	pubsub := p.redis.Subscribe(context.Background(), 
		fmt.Sprintf("p2p_orders:%s", userID),
		fmt.Sprintf("p2p_trades:%s", userID),
		fmt.Sprintf("p2p_chat:%s", userID),
	)
	defer pubsub.Close()

	ch := pubsub.Channel()
	
	for msg := range ch {
		if err := conn.WriteMessage(websocket.TextMessage, []byte(msg.Payload)); err != nil {
			log.Printf("WebSocket write error: %v", err)
			break
		}
	}
}

// Helper functions
func (p *P2PService) checkUserBalance(userID string, currencyID uuid.UUID, amount float64) bool {
	var wallet struct {
		Balance       float64
		LockedBalance float64
	}
	
	err := p.db.Raw(`
		SELECT balance, locked_balance 
		FROM wallets 
		WHERE user_id = ? AND currency_id = ?
	`, userID, currencyID).Scan(&wallet).Error
	
	if err != nil {
		return false
	}
	
	availableBalance := wallet.Balance - wallet.LockedBalance
	return availableBalance >= amount
}

func (p *P2PService) lockUserFunds(userID string, currencyID uuid.UUID, amount float64) error {
	return p.db.Exec(`
		UPDATE wallets 
		SET locked_balance = locked_balance + ? 
		WHERE user_id = ? AND currency_id = ?
	`, amount, userID, currencyID).Error
}

func (p *P2PService) transferFunds(trade P2PTrade) error {
	// Transfer crypto from seller to buyer
	err := p.db.Exec(`
		UPDATE wallets 
		SET balance = balance - ?, locked_balance = locked_balance - ?
		WHERE user_id = ? AND currency_id = ?
	`, trade.Quantity, trade.Quantity, trade.SellerID, trade.OrderID).Error
	
	if err != nil {
		return err
	}
	
	return p.db.Exec(`
		UPDATE wallets 
		SET balance = balance + ?
		WHERE user_id = ? AND currency_id = ?
	`, trade.Quantity, trade.BuyerID, trade.OrderID).Error
}

func (p *P2PService) sendChatMessage(tradeID, senderID uuid.UUID, message, messageType string) uuid.UUID {
	chatMessage := ChatMessage{
		ID:          uuid.New(),
		TradeID:     tradeID,
		SenderID:    senderID,
		Message:     message,
		MessageType: messageType,
		CreatedAt:   time.Now(),
	}
	
	p.db.Create(&chatMessage)
	
	// Broadcast to WebSocket
	messageData, _ := json.Marshal(chatMessage)
	p.redis.Publish(context.Background(), fmt.Sprintf("p2p_chat:%s", tradeID), messageData)
	
	return chatMessage.ID
}

func (p *P2PService) broadcastOrderUpdate(order P2POrder, action string) {
	update := map[string]interface{}{
		"type":   "order_update",
		"action": action,
		"order":  order,
	}
	
	updateData, _ := json.Marshal(update)
	p.redis.Publish(context.Background(), "p2p_orders_global", updateData)
}

func (p *P2PService) broadcastTradeUpdate(trade P2PTrade, action string) {
	update := map[string]interface{}{
		"type":   "trade_update",
		"action": action,
		"trade":  trade,
	}
	
	updateData, _ := json.Marshal(update)
	p.redis.Publish(context.Background(), fmt.Sprintf("p2p_trades:%s", trade.BuyerID), updateData)
	p.redis.Publish(context.Background(), fmt.Sprintf("p2p_trades:%s", trade.SellerID), updateData)
}

func (p *P2PService) sendTradeNotification(userID, tradeID uuid.UUID, notificationType string) {
	// Implementation for sending notifications
}

func (p *P2PService) sendDisputeNotification(userID, disputeID uuid.UUID, notificationType string) {
	// Implementation for sending dispute notifications
}

func (p *P2PService) notifyAdminDispute(disputeID uuid.UUID) {
	// Implementation for notifying admin about disputes
}

func main() {
	p2pService := NewP2PService()

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
		c.JSON(http.StatusOK, gin.H{"status": "healthy", "service": "p2p-service"})
	})

	// API routes
	api := r.Group("/api/v1/p2p")
	{
		// Orders
		api.POST("/orders", p2pService.CreateP2POrder)
		api.GET("/orders", p2pService.GetP2POrders)
		api.GET("/orders/my", p2pService.GetUserP2POrders)
		
		// Trades
		api.POST("/trades", p2pService.CreateP2PTrade)
		api.GET("/trades/my", p2pService.GetUserP2PTrades)
		api.POST("/trades/:trade_id/payment-sent", p2pService.MarkPaymentSent)
		api.POST("/trades/:trade_id/payment-received", p2pService.ConfirmPaymentReceived)
		api.POST("/trades/:trade_id/dispute", p2pService.CreateDispute)
		
		// Chat
		api.POST("/trades/:trade_id/chat", p2pService.SendChatMessage)
		api.GET("/trades/:trade_id/chat", p2pService.GetChatMessages)
		
		// Payment Methods
		api.GET("/payment-methods", p2pService.GetPaymentMethods)
		api.POST("/payment-methods", p2pService.AddPaymentMethod)
		
		// WebSocket
		api.GET("/ws", p2pService.HandleWebSocket)
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "3009"
	}

	log.Printf("P2P Service starting on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, r))
}