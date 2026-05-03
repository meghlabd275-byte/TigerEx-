// TigerEx Go Trading Engine
// High-performance trading engine written in Go
// Part of TigerEx Multi-Language Microservices Architecture

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"sync"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/redis/go-redis/v9"
	"github.com/shopspring/decimal"
	"go.uber.org/zap"
)

// Order represents a trading order
type Order struct {
	ID            string          `json:"id"`
	UserID        string          `json:"user_id"`
	Symbol        string          `json:"symbol"`
	Side          OrderSide       `json:"side"`
	Type          OrderType       `json:"type"`
	Price         decimal.Decimal `json:"price"`
	Quantity      decimal.Decimal `json:"quantity"`
	FilledQty     decimal.Decimal `json:"filled_qty"`
	Status        OrderStatus     `json:"status"`
	Fee           decimal.Decimal `json:"fee"`
	FeeCurrency   string          `json:"fee_currency"`
	CreatedAt     time.Time       `json:"created_at"`
	UpdatedAt     time.Time       `json:"updated_at"`
	ExchangeID    string          `json:"exchange_id"`
	TierFeeDiscount decimal.Decimal `json:"tier_fee_discount"`
}

type OrderSide string
type OrderType string
type OrderStatus string

const (
	OrderSideBuy  OrderSide = "buy"
	OrderSideSell OrderSide = "sell"

	OrderTypeLimit       OrderType = "limit"
	OrderTypeMarket      OrderType = "market"
	OrderTypeStopLimit   OrderType = "stop_limit"
	OrderTypeStopMarket  OrderType = "stop_market"
	OrderTypeIOC         OrderType = "ioc"  // Immediate or Cancel
	OrderTypeFOK         OrderType = "fok"  // Fill or Kill
	OrderTypePostOnly    OrderType = "post_only"

	OrderStatusNew             OrderStatus = "new"
	OrderStatusPartiallyFilled OrderStatus = "partially_filled"
	OrderStatusFilled          OrderStatus = "filled"
	OrderStatusCancelled       OrderStatus = "cancelled"
	OrderStatusRejected        OrderStatus = "rejected"
	OrderStatusExpired         OrderStatus = "expired"
)

// Trade represents an executed trade
type Trade struct {
	ID          string          `json:"id"`
	Symbol      string          `json:"symbol"`
	TakerOrderID string         `json:"taker_order_id"`
	MakerOrderID string         `json:"maker_order_id"`
	TakerUserID string          `json:"taker_user_id"`
	MakerUserID string          `json:"maker_user_id"`
	Side        OrderSide       `json:"side"`
	Price       decimal.Decimal `json:"price"`
	Quantity    decimal.Decimal `json:"quantity"`
	TakerFee    decimal.Decimal `json:"taker_fee"`
	MakerFee    decimal.Decimal `json:"maker_fee"`
	Timestamp   time.Time       `json:"timestamp"`
}

// OrderBook represents the order book for a trading pair
type OrderBook struct {
	Symbol    string
	Bids      *OrderBookLevel // Sorted descending by price
	Asks      *OrderBookLevel // Sorted ascending by price
	mu        sync.RWMutex
	orderMap  map[string]*Order // Quick lookup by order ID
}

type OrderBookLevel struct {
	Price    decimal.Decimal
	Orders   []*Order
	Next     *OrderBookLevel
	Prev     *OrderBookLevel
}

// TradingEngine represents the main trading engine
type TradingEngine struct {
	orderBooks    map[string]*OrderBook
	orderBooksMu  sync.RWMutex
	db            *pgxpool.Pool
	redis         *redis.Client
	logger        *zap.Logger
	feeService    *FeeService
	wsHub         *WebSocketHub
	exchangeID    string
	exchangeStatus ExchangeStatus
}

type ExchangeStatus string

const (
	ExchangeStatusActive    ExchangeStatus = "active"
	ExchangeStatusPaused    ExchangeStatus = "paused"
	ExchangeStatusHalted    ExchangeStatus = "halted"
	ExchangeStatusMaintenance ExchangeStatus = "maintenance"
)

// FeeService handles fee calculations
type FeeService struct {
	redis    *redis.Client
	db       *pgxpool.Pool
	logger   *zap.Logger
}

// FeeTier represents user fee tier
type FeeTier struct {
	ID             string
	Name           string
	MakerFee       decimal.Decimal
	TakerFee       decimal.Decimal
	WithdrawalFee  decimal.Decimal
	MinVolume      decimal.Decimal
	Description    string
}

func NewTradingEngine(db *pgxpool.Pool, redis *redis.Client, logger *zap.Logger) *TradingEngine {
	return &TradingEngine{
		orderBooks: make(map[string]*OrderBook),
		db:         db,
		redis:      redis,
		logger:     logger,
		feeService: &FeeService{redis: redis, db: db, logger: logger},
		wsHub:      NewWebSocketHub(),
	}
}

// PlaceOrder places a new order
func (e *TradingEngine) PlaceOrder(ctx context.Context, order *Order) (*Order, []Trade, error) {
	e.orderBooksMu.Lock()
	defer e.orderBooksMu.Unlock()

	// Check exchange status
	if e.exchangeStatus != ExchangeStatusActive {
		return nil, nil, fmt.Errorf("exchange is %s", e.exchangeStatus)
	}

	// Get or create order book
	ob, exists := e.orderBooks[order.Symbol]
	if !exists {
		ob = &OrderBook{
			Symbol:   order.Symbol,
			Bids:     nil,
			Asks:     nil,
			orderMap: make(map[string]*Order),
		}
		e.orderBooks[order.Symbol] = ob
	}

	ob.mu.Lock()
	defer ob.mu.Unlock()

	// Set order defaults
	order.ID = generateOrderID()
	order.Status = OrderStatusNew
	order.CreatedAt = time.Now()
	order.UpdatedAt = time.Now()
	order.ExchangeID = e.exchangeID

	var trades []Trade
	var err error

	// Process order based on type
	switch order.Type {
	case OrderTypeMarket:
		trades, err = e.processMarketOrder(ob, order)
	case OrderTypeLimit:
		trades, err = e.processLimitOrder(ob, order)
	case OrderTypeIOC:
		trades, err = e.processIOCOrder(ob, order)
	case OrderTypeFOK:
		trades, err = e.processFOKOrder(ob, order)
	default:
		return nil, nil, fmt.Errorf("unsupported order type: %s", order.Type)
	}

	if err != nil {
		order.Status = OrderStatusRejected
		return order, nil, err
	}

	// Update order status
	if order.FilledQty.GreaterThan(decimal.Zero) {
		if order.FilledQty.Equal(order.Quantity) {
			order.Status = OrderStatusFilled
		} else {
			order.Status = OrderStatusPartiallyFilled
		}
	}

	// Store order
	ob.orderMap[order.ID] = order

	// Publish order update
	e.publishOrderUpdate(ctx, order, trades)

	return order, trades, nil
}

// processMarketOrder processes a market order
func (e *TradingEngine) processMarketOrder(ob *OrderBook, order *Order) ([]Trade, error) {
	var trades []Trade
	remainingQty := order.Quantity

	// Match against opposite side
	if order.Side == OrderSideBuy {
		// Match against asks (sells)
		for ob.Asks != nil && remainingQty.GreaterThan(decimal.Zero) {
			level := ob.Asks
			for len(level.Orders) > 0 && remainingQty.GreaterThan(decimal.Zero) {
				makerOrder := level.Orders[0]
				matchQty := decimal.Min(remainingQty, makerOrder.Quantity.Sub(makerOrder.FilledQty))
				
				trade := e.executeTrade(order, makerOrder, matchQty, level.Price)
				trades = append(trades, trade)
				
				remainingQty = remainingQty.Sub(matchQty)
				order.FilledQty = order.FilledQty.Add(matchQty)
				makerOrder.FilledQty = makerOrder.FilledQty.Add(matchQty)
				
				if makerOrder.FilledQty.Equal(makerOrder.Quantity) {
					makerOrder.Status = OrderStatusFilled
					level.Orders = level.Orders[1:]
					delete(ob.orderMap, makerOrder.ID)
				}
			}
			if len(level.Orders) == 0 {
				ob.Asks = level.Next
			}
		}
	} else {
		// Match against bids (buys)
		for ob.Bids != nil && remainingQty.GreaterThan(decimal.Zero) {
			level := ob.Bids
			for len(level.Orders) > 0 && remainingQty.GreaterThan(decimal.Zero) {
				makerOrder := level.Orders[0]
				matchQty := decimal.Min(remainingQty, makerOrder.Quantity.Sub(makerOrder.FilledQty))
				
				trade := e.executeTrade(order, makerOrder, matchQty, level.Price)
				trades = append(trades, trade)
				
				remainingQty = remainingQty.Sub(matchQty)
				order.FilledQty = order.FilledQty.Add(matchQty)
				makerOrder.FilledQty = makerOrder.FilledQty.Add(matchQty)
				
				if makerOrder.FilledQty.Equal(makerOrder.Quantity) {
					makerOrder.Status = OrderStatusFilled
					level.Orders = level.Orders[1:]
					delete(ob.orderMap, makerOrder.ID)
				}
			}
			if len(level.Orders) == 0 {
				ob.Bids = level.Next
			}
		}
	}

	return trades, nil
}

// processLimitOrder processes a limit order
func (e *TradingEngine) processLimitOrder(ob *OrderBook, order *Order) ([]Trade, error) {
	var trades []Trade
	remainingQty := order.Quantity

	// Try to match first
	if order.Side == OrderSideBuy {
		// Match against asks
		for ob.Asks != nil && remainingQty.GreaterThan(decimal.Zero) && order.Price.GreaterThanOrEqual(ob.Asks.Price) {
			level := ob.Asks
			for len(level.Orders) > 0 && remainingQty.GreaterThan(decimal.Zero) {
				makerOrder := level.Orders[0]
				matchQty := decimal.Min(remainingQty, makerOrder.Quantity.Sub(makerOrder.FilledQty))
				
				trade := e.executeTrade(order, makerOrder, matchQty, level.Price)
				trades = append(trades, trade)
				
				remainingQty = remainingQty.Sub(matchQty)
				order.FilledQty = order.FilledQty.Add(matchQty)
				makerOrder.FilledQty = makerOrder.FilledQty.Add(matchQty)
				
				if makerOrder.FilledQty.Equal(makerOrder.Quantity) {
					makerOrder.Status = OrderStatusFilled
					level.Orders = level.Orders[1:]
					delete(ob.orderMap, makerOrder.ID)
				}
			}
			if len(level.Orders) == 0 {
				ob.Asks = level.Next
			}
		}
	} else {
		// Match against bids
		for ob.Bids != nil && remainingQty.GreaterThan(decimal.Zero) && order.Price.LessThanOrEqual(ob.Bids.Price) {
			level := ob.Bids
			for len(level.Orders) > 0 && remainingQty.GreaterThan(decimal.Zero) {
				makerOrder := level.Orders[0]
				matchQty := decimal.Min(remainingQty, makerOrder.Quantity.Sub(makerOrder.FilledQty))
				
				trade := e.executeTrade(order, makerOrder, matchQty, level.Price)
				trades = append(trades, trade)
				
				remainingQty = remainingQty.Sub(matchQty)
				order.FilledQty = order.FilledQty.Add(matchQty)
				makerOrder.FilledQty = makerOrder.FilledQty.Add(matchQty)
				
				if makerOrder.FilledQty.Equal(makerOrder.Quantity) {
					makerOrder.Status = OrderStatusFilled
					level.Orders = level.Orders[1:]
					delete(ob.orderMap, makerOrder.ID)
				}
			}
			if len(level.Orders) == 0 {
				ob.Bids = level.Next
			}
		}
	}

	// If remaining quantity, add to book
	if remainingQty.GreaterThan(decimal.Zero) && order.Type != OrderTypeIOC {
		e.addOrderToBook(ob, order)
	}

	return trades, nil
}

// processIOCOrder processes an Immediate or Cancel order
func (e *TradingEngine) processIOCOrder(ob *OrderBook, order *Order) ([]Trade, error) {
	trades, err := e.processLimitOrder(ob, order)
	if err != nil {
		return nil, err
	}
	// Any unfilled portion is cancelled
	return trades, nil
}

// processFOKOrder processes a Fill or Kill order
func (e *TradingEngine) processFOKOrder(ob *OrderBook, order *Order) ([]Trade, error) {
	// Check if entire order can be filled
	availableQty := decimal.Zero
	if order.Side == OrderSideBuy {
		level := ob.Asks
		for level != nil && availableQty.LessThan(order.Quantity) {
			if level.Price.LessThanOrEqual(order.Price) {
				for _, o := range level.Orders {
					availableQty = availableQty.Add(o.Quantity.Sub(o.FilledQty))
				}
			}
			level = level.Next
		}
	} else {
		level := ob.Bids
		for level != nil && availableQty.LessThan(order.Quantity) {
			if level.Price.GreaterThanOrEqual(order.Price) {
				for _, o := range level.Orders {
					availableQty = availableQty.Add(o.Quantity.Sub(o.FilledQty))
				}
			}
			level = level.Next
		}
	}

	if availableQty.LessThan(order.Quantity) {
		return nil, fmt.Errorf("insufficient liquidity for FOK order")
	}

	return e.processLimitOrder(ob, order)
}

// executeTrade executes a trade between taker and maker
func (e *TradingEngine) executeTrade(takerOrder, makerOrder *Order, qty, price decimal.Decimal) Trade {
	// Calculate fees
	takerFeeRate := e.feeService.GetFeeRate(takerOrder.UserID, takerOrder.Side == OrderSideBuy)
	makerFeeRate := e.feeService.GetFeeRate(makerOrder.UserID, makerOrder.Side == OrderSideBuy)

	takerFee := qty.Mul(price).Mul(takerFeeRate)
	makerFee := qty.Mul(price).Mul(makerFeeRate)

	trade := Trade{
		ID:           generateTradeID(),
		Symbol:       takerOrder.Symbol,
		TakerOrderID: takerOrder.ID,
		MakerOrderID: makerOrder.ID,
		TakerUserID:  takerOrder.UserID,
		MakerUserID:  makerOrder.UserID,
		Side:         takerOrder.Side,
		Price:        price,
		Quantity:     qty,
		TakerFee:     takerFee,
		MakerFee:     makerFee,
		Timestamp:    time.Now(),
	}

	// Store trade in database
	go e.storeTrade(&trade)

	return trade
}

// addOrderToBook adds an order to the order book
func (e *TradingEngine) addOrderToBook(ob *OrderBook, order *Order) {
	var level **OrderBookLevel
	var compareFunc func(decimal.Decimal, decimal.Decimal) bool

	if order.Side == OrderSideBuy {
		level = &ob.Bids
		compareFunc = func(a, b decimal.Decimal) bool { return a.GreaterThan(b) }
	} else {
		level = &ob.Asks
		compareFunc = func(a, b decimal.Decimal) bool { return a.LessThan(b) }
	}

	// Find or create level
	current := *level
	var prev *OrderBookLevel

	for current != nil && compareFunc(current.Price, order.Price) {
		prev = current
		current = current.Next
	}

	if current != nil && current.Price.Equal(order.Price) {
		// Add to existing level
		current.Orders = append(current.Orders, order)
	} else {
		// Create new level
		newLevel := &OrderBookLevel{
			Price:  order.Price,
			Orders: []*Order{order},
		}
		if prev == nil {
			newLevel.Next = *level
			*level = newLevel
		} else {
			newLevel.Next = current
			newLevel.Prev = prev
			prev.Next = newLevel
		}
	}
}

// CancelOrder cancels an order
func (e *TradingEngine) CancelOrder(ctx context.Context, symbol, orderID string) error {
	e.orderBooksMu.RLock()
	ob, exists := e.orderBooks[symbol]
	e.orderBooksMu.RUnlock()

	if !exists {
		return fmt.Errorf("order book not found for symbol: %s", symbol)
	}

	ob.mu.Lock()
	defer ob.mu.Unlock()

	order, exists := ob.orderMap[orderID]
	if !exists {
		return fmt.Errorf("order not found: %s", orderID)
	}

	order.Status = OrderStatusCancelled
	order.UpdatedAt = time.Now()
	delete(ob.orderMap, orderID)

	// Remove from price level
	// (implementation would traverse and remove from linked list)

	e.publishOrderUpdate(ctx, order, nil)
	return nil
}

// GetOrderBook returns the current order book state
func (e *TradingEngine) GetOrderBook(symbol string, depth int) (bids, asks []OrderBookEntry) {
	e.orderBooksMu.RLock()
	ob, exists := e.orderBooks[symbol]
	e.orderBooksMu.RUnlock()

	if !exists {
		return nil, nil
	}

	ob.mu.RLock()
	defer ob.mu.RUnlock()

	// Collect bids
	level := ob.Bids
	for level != nil && len(bids) < depth {
		totalQty := decimal.Zero
		for _, o := range level.Orders {
			totalQty = totalQty.Add(o.Quantity.Sub(o.FilledQty))
		}
		bids = append(bids, OrderBookEntry{
			Price:    level.Price,
			Quantity: totalQty,
		})
		level = level.Next
	}

	// Collect asks
	level = ob.Asks
	for level != nil && len(asks) < depth {
		totalQty := decimal.Zero
		for _, o := range level.Orders {
			totalQty = totalQty.Add(o.Quantity.Sub(o.FilledQty))
		}
		asks = append(asks, OrderBookEntry{
			Price:    level.Price,
			Quantity: totalQty,
		})
		level = level.Next
	}

	return bids, asks
}

type OrderBookEntry struct {
	Price    decimal.Decimal `json:"price"`
	Quantity decimal.Decimal `json:"quantity"`
}

// FeeService methods
func (f *FeeService) GetFeeRate(userID string, isTaker bool) decimal.Decimal {
	ctx := context.Background()
	
	// Get user tier from cache
	tierKey := fmt.Sprintf("user:tier:%s", userID)
	tier, err := f.redis.Get(ctx, tierKey).Result()
	if err != nil {
		// Default tier
		tier = "regular"
	}

	// Get fee rates for tier
	feeKey := fmt.Sprintf("fee:tier:%s", tier)
	feeData, err := f.redis.HGetAll(ctx, feeKey).Result()
	if err != nil || len(feeData) == 0 {
		// Default fees
		if isTaker {
			return decimal.NewFromFloat(0.001) // 0.1%
		}
		return decimal.NewFromFloat(0.0008) // 0.08%
	}

	if isTaker {
		if takerFee, ok := feeData["taker_fee"]; ok {
			fee, _ := decimal.NewFromString(takerFee)
			return fee
		}
	} else {
		if makerFee, ok := feeData["maker_fee"]; ok {
			fee, _ := decimal.NewFromString(makerFee)
			return fee
		}
	}

	return decimal.NewFromFloat(0.001)
}

// WebSocket Hub for real-time updates
type WebSocketHub struct {
	clients    map[*WebSocketClient]bool
	broadcast  chan []byte
	register   chan *WebSocketClient
	unregister chan *WebSocketClient
	mu         sync.RWMutex
}

type WebSocketClient struct {
	hub    *WebSocketHub
	conn   *websocket.Conn
	send   chan []byte
	symbol string
}

func NewWebSocketHub() *WebSocketHub {
	return &WebSocketHub{
		clients:    make(map[*WebSocketClient]bool),
		broadcast:  make(chan []byte, 256),
		register:   make(chan *WebSocketClient),
		unregister: make(chan *WebSocketClient),
	}
}

func (h *WebSocketHub) Run() {
	for {
		select {
		case client := <-h.register:
			h.mu.Lock()
			h.clients[client] = true
			h.mu.Unlock()
		case client := <-h.unregister:
			h.mu.Lock()
			if _, ok := h.clients[client]; ok {
				delete(h.clients, client)
				close(client.send)
			}
			h.mu.Unlock()
		case message := <-h.broadcast:
			h.mu.RLock()
			for client := range h.clients {
				select {
				case client.send <- message:
				default:
					close(client.send)
					delete(h.clients, client)
				}
			}
			h.mu.RUnlock()
		}
	}
}

func (e *TradingEngine) publishOrderUpdate(ctx context.Context, order *Order, trades []Trade) {
	update := map[string]interface{}{
		"type":    "order_update",
		"order":   order,
		"trades":  trades,
	}
	data, _ := json.Marshal(update)
	e.wsHub.broadcast <- data

	// Also publish to Redis for other services
	e.redis.Publish(ctx, "order_updates", string(data))
}

func (e *TradingEngine) storeTrade(trade *Trade) {
	ctx := context.Background()
	query := `
		INSERT INTO trades (id, symbol, taker_order_id, maker_order_id, taker_user_id, maker_user_id, 
			side, price, quantity, taker_fee, maker_fee, timestamp)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
	`
	_, err := e.db.Exec(ctx, query,
		trade.ID, trade.Symbol, trade.TakerOrderID, trade.MakerOrderID,
		trade.TakerUserID, trade.MakerUserID, trade.Side, trade.Price,
		trade.Quantity, trade.TakerFee, trade.MakerFee, trade.Timestamp,
	)
	if err != nil {
		e.logger.Error("Failed to store trade", zap.Error(err))
	}
}

func generateOrderID() string {
	return fmt.Sprintf("ORD-%d-%s", time.Now().UnixNano(), randomString(8))
}

func generateTradeID() string {
	return fmt.Sprintf("TRD-%d-%s", time.Now().UnixNano(), randomString(8))
}

func randomString(n int) string {
	const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	b := make([]byte, n)
	for i := range b {
		b[i] = letters[time.Now().Nanosecond()%len(letters)]
	}
	return string(b)
}

// HTTP Handlers
func (e *TradingEngine) handlePlaceOrder(c *gin.Context) {
	var req struct {
		UserID   string          `json:"user_id"`
		Symbol   string          `json:"symbol"`
		Side     OrderSide       `json:"side"`
		Type     OrderType       `json:"type"`
		Price    decimal.Decimal `json:"price"`
		Quantity decimal.Decimal `json:"quantity"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	order := &Order{
		UserID:   req.UserID,
		Symbol:   req.Symbol,
		Side:     req.Side,
		Type:     req.Type,
		Price:    req.Price,
		Quantity: req.Quantity,
	}

	order, trades, err := e.PlaceOrder(c.Request.Context(), order)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"order":  order,
		"trades": trades,
	})
}

func (e *TradingEngine) handleCancelOrder(c *gin.Context) {
	symbol := c.Param("symbol")
	orderID := c.Param("order_id")

	err := e.CancelOrder(c.Request.Context(), symbol, orderID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Order cancelled successfully"})
}

func (e *TradingEngine) handleGetOrderBook(c *gin.Context) {
	symbol := c.Param("symbol")
	depth, _ := strconv.Atoi(c.DefaultQuery("depth", "20"))

	bids, asks := e.GetOrderBook(symbol, depth)
	c.JSON(http.StatusOK, gin.H{
		"symbol": symbol,
		"bids":   bids,
		"asks":   asks,
	})
}

func (e *TradingEngine) handleSetExchangeStatus(c *gin.Context) {
	var req struct {
		Status ExchangeStatus `json:"status"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	e.exchangeStatus = req.Status
	c.JSON(http.StatusOK, gin.H{
		"message":       "Exchange status updated",
		"exchange_id":   e.exchangeID,
		"status":        e.exchangeStatus,
	})
}

func main() {
	// Initialize logger
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	// Load environment variables
	dbURL := os.Getenv("DATABASE_URL")
	redisURL := os.Getenv("REDIS_URL")
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Connect to database
	db, err := pgxpool.New(context.Background(), dbURL)
	if err != nil {
		log.Fatalf("Unable to connect to database: %v", err)
	}
	defer db.Close()

	// Connect to Redis
	opt, _ := redis.ParseURL(redisURL)
	rdb := redis.NewClient(opt)

	// Create trading engine
	engine := NewTradingEngine(db, rdb, logger)
	engine.exchangeID = os.Getenv("EXCHANGE_ID")
	if engine.exchangeID == "" {
		engine.exchangeID = "TIGEREX-MAIN"
	}
	engine.exchangeStatus = ExchangeStatusActive

	// Start WebSocket hub
	go engine.wsHub.Run()

	// Setup HTTP server
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.Use(gin.Recovery())

	// API routes
	api := router.Group("/api/v1")
	{
		// Trading endpoints
		api.POST("/order", engine.handlePlaceOrder)
		api.DELETE("/order/:symbol/:order_id", engine.handleCancelOrder)
		api.GET("/orderbook/:symbol", engine.handleGetOrderBook)

		// Exchange management
		api.POST("/exchange/status", engine.handleSetExchangeStatus)
		api.GET("/exchange/status", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"exchange_id":   engine.exchangeID,
				"status":        engine.exchangeStatus,
			})
		})

		// Health check
		api.GET("/health", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"status":     "healthy",
				"service":    "go-trading-engine",
				"exchange_id": engine.exchangeID,
				"timestamp":  time.Now().Unix(),
			})
		})
	}

	// Graceful shutdown
	srv := &http.Server{
		Addr:    ":" + port,
		Handler: router,
	}

	go func() {
		logger.Info("Starting Go Trading Engine", zap.String("port", port))
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Fatal("Server forced to shutdown", zap.Error(err))
	}

	logger.Info("Server exited")
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
