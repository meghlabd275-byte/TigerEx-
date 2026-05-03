package tigerex

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

const (
	BaseURL = "https://api.tigerex.com"
	WSURL   = "wss://ws.tigerex.com"
)

// Client represents TigerEx API client
type Client struct {
	APIKey    string
	APISecret string
	HTTPClient *http.Client
	WebSocket *WebSocketClient
}

// NewClient creates a new TigerEx client
func NewClient(apiKey, apiSecret string) *Client {
	return &Client{
		APIKey:    apiKey,
		APISecret: apiSecret,
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// Request represents API request
type Request struct {
	Method  string
	Endpoint string
	Body    interface{}
}

// Response represents API response
type Response struct {
	Success bool
	Data    interface{}
	Error   string
}

// ==================== AUTH ====================

// Login authenticates user and returns token
func (c *Client) Login(email, password string) (*LoginResponse, error) {
	body := map[string]string{
		"email":    email,
		"password": password,
	}
	
	resp, err := c.doRequest("POST", "/api/v1/auth/login", body)
	if err != nil {
		return nil, err
	}
	
	var loginResp LoginResponse
	json.Unmarshal(resp.Data.(map[string]interface{})["token"].([]byte), &loginResp)
	return &loginResp, nil
}

// Register registers a new user
func (c *Client) Register(email, password, username string) (*User, error) {
	body := map[string]string{
		"email":    email,
		"password": password,
		"username":  username,
	}
	
	resp, err := c.doRequest("POST", "/api/v1/auth/register", body)
	if err != nil {
		return nil, err
	}
	
	var user User
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["user"])
	json.Unmarshal(data, &user)
	return &user, nil
}

// Enable2FA enables two-factor authentication
func (c *Client) Enable2FA() (*TwoFactorResponse, error) {
	resp, err := c.doRequest("POST", "/api/v1/auth/2fa/enable", nil)
	if err != nil {
		return nil, err
	}
	
	var twofa TwoFactorResponse
	data, _ := json.Marshal(resp.Data)
	json.Unmarshal(data, &twofa)
	return &twofa, nil
}

// ==================== MARKETS ====================

// GetMarkets returns all trading markets
func (c *Client) GetMarkets() ([]Market, error) {
	resp, err := c.doRequest("GET", "/api/v1/markets", nil)
	if err != nil {
		return nil, err
	}
	
	var markets []Market
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["markets"])
	json.Unmarshal(data, &markets)
	return markets, nil
}

// GetMarket returns single market
func (c *Client) GetMarket(symbol string) (*Market, error) {
	resp, err := c.doRequest("GET", fmt.Sprintf("/api/v1/market/%s", symbol), nil)
	if err != nil {
		return nil, err
	}
	
	var market Market
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["market"])
	json.Unmarshal(data, &market)
	return &market, nil
}

// GetDepth returns order book depth
func (c *Client) GetDepth(symbol string, limit int) (*OrderBook, error) {
	resp, err := c.doRequest("GET", fmt.Sprintf("/api/v1/depth/%s?limit=%d", symbol, limit), nil)
	if err != nil {
		return nil, err
	}
	
	var orderbook OrderBook
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["orderbook"])
	json.Unmarshal(data, &orderbook)
	return &orderbook, nil
}

// GetKlines returns candlestick data
func (c *Client) GetKlines(symbol, interval string, limit int) ([]Kline, error) {
	resp, err := c.doRequest("GET", fmt.Sprintf("/api/v1/klines?symbol=%s&interval=%s&limit=%d", symbol, interval, limit), nil)
	if err != nil {
		return nil, err
	}
	
	var klines []Kline
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["klines"])
	json.Unmarshal(data, &klines)
	return klines, nil
}

// ==================== TRADING ====================

// PlaceOrder places a new order
func (c *Client) PlaceOrder(order *OrderRequest) (*Order, error) {
	resp, err := c.doRequest("POST", "/api/v1/order", order)
	if err != nil {
		return nil, err
	}
	
	var placedOrder Order
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["order"])
	json.Unmarshal(data, &placedOrder)
	return &placedOrder, nil
}

// CancelOrder cancels an order
func (c *Client) CancelOrder(orderID string) error {
	_, err := c.doRequest("DELETE", fmt.Sprintf("/api/v1/order/%s", orderID), nil)
	return err
}

// GetOrders returns user orders
func (c *Client) GetOrders(symbol, status string, limit int) ([]Order, error) {
	resp, err := c.doRequest("GET", fmt.Sprintf("/api/v1/orders?symbol=%s&status=%s&limit=%d", symbol, status, limit), nil)
	if err != nil {
		return nil, err
	}
	
	var orders []Order
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["orders"])
	json.Unmarshal(data, &orders)
	return orders, nil
}

// ==================== FUTURES ====================

// OpenPosition opens a futures position
func (c *Client) OpenPosition(pos *PositionRequest) (*Position, error) {
	resp, err := c.doRequest("POST", "/api/v1/futures/position", pos)
	if err != nil {
		return nil, err
	}
	
	var position Position
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["position"])
	json.Unmarshal(data, &position)
	return &position, nil
}

// ClosePosition closes a futures position
func (c *Client) ClosePosition(positionID string) error {
	_, err := c.doRequest("POST", fmt.Sprintf("/api/v1/futures/position/%s/close", positionID), nil)
	return err
}

// GetPositions returns open positions
func (c *Client) GetPositions() ([]Position, error) {
	resp, err := c.doRequest("GET", "/api/v1/futures/positions", nil)
	if err != nil {
		return nil, err
	}
	
	var positions []Position
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["positions"])
	json.Unmarshal(data, &positions)
	return positions, nil
}

// ==================== WALLET ====================

// GetBalance returns account balances
func (c *Client) GetBalance() ([]Balance, error) {
	resp, err := c.doRequest("GET", "/api/v1/wallet/balance", nil)
	if err != nil {
		return nil, err
	}
	
	var balances []Balance
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["balances"])
	json.Unmarshal(data, &balances)
	return balances, nil
}

// GetDepositAddress returns deposit address
func (c *Client) GetDepositAddress(currency string) (*DepositAddress, error) {
	resp, err := c.doRequest("GET", fmt.Sprintf("/api/v1/wallet/deposit/address?currency=%s", currency), nil)
	if err != nil {
		return nil, err
	}
	
	var addr DepositAddress
	data, _ := json.Marshal(resp.Data)
	json.Unmarshal(data, &addr)
	return &addr, nil
}

// Withdraw initiates withdrawal
func (c *Client) Withdraw(req *WithdrawRequest) (string, error) {
	resp, err := c.doRequest("POST", "/api/v1/wallet/withdraw", req)
	if err != nil {
		return "", err
	}
	
	txID := resp.Data.(map[string]interface{})["txId"].(string)
	return txID, nil
}

// GetTransactions returns transaction history
func (c *Client) GetTransactions(txType, currency string, limit int) ([]Transaction, error) {
	resp, err := c.doRequest("GET", fmt.Sprintf("/api/v1/wallet/transactions?type=%s&currency=%s&limit=%d", txType, currency, limit), nil)
	if err != nil {
		return nil, err
	}
	
	var txs []Transaction
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["transactions"])
	json.Unmarshal(data, &txs)
	return txs, nil
}

// ==================== P2P ====================

// GetP2PAds returns P2P advertisements
func (c *Client) GetP2PAds(pType, currency, payment string) ([]P2PAd, error) {
	resp, err := c.doRequest("GET", fmt.Sprintf("/api/v1/p2p/ads?type=%s&currency=%s&paymentMethod=%s", pType, currency, payment), nil)
	if err != nil {
		return nil, err
	}
	
	var ads []P2PAd
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["ads"])
	json.Unmarshal(data, &ads)
	return ads, nil
}

// CreateP2POrder creates P2P order
func (c *Client) CreateP2POrder(adID string, amount float64) (*P2POrder, error) {
	body := map[string]interface{}{
		"adId":   adID,
		"amount": amount,
	}
	
	resp, err := c.doRequest("POST", "/api/v1/p2p/order", body)
	if err != nil {
		return nil, err
	}
	
	var order P2POrder
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["order"])
	json.Unmarshal(data, &order)
	return &order, nil
}

// ==================== STAKING ====================

// GetStakingProducts returns available staking products
func (c *Client) GetStakingProducts() ([]StakingProduct, error) {
	resp, err := c.doRequest("GET", "/api/v1/staking/products", nil)
	if err != nil {
		return nil, err
	}
	
	var products []StakingProduct
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["products"])
	json.Unmarshal(data, &products)
	return products, nil
}

// Stake creates staking position
func (c *Client) Stake(productID string, amount float64) (*StakingPosition, error) {
	body := map[string]interface{}{
		"productId": productID,
		"amount":    amount,
	}
	
	resp, err := c.doRequest("POST", "/api/v1/staking/stake", body)
	if err != nil {
		return nil, err
	}
	
	var stake StakingPosition
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["stake"])
	json.Unmarshal(data, &stake)
	return &stake, nil
}

// ==================== COPY TRADING ====================

// GetTopTraders returns top copy traders
func (c *Client) GetTopTraders() ([]Trader, error) {
	resp, err := c.doRequest("GET", "/api/v1/copy/traders", nil)
	if err != nil {
		return nil, err
	}
	
	var traders []Trader
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["traders"])
	json.Unmarshal(data, &traders)
	return traders, nil
}

// FollowTrader follows a trader
func (c *Client) FollowTrader(traderID string, amount float64) error {
	body := map[string]interface{}{
		"traderId": traderID,
		"amount":   amount,
	}
	
	_, err := c.doRequest("POST", "/api/v1/copy/follow", body)
	return err
}

// ==================== API KEYS ====================

// CreateAPIKey creates new API key
func (c *Client) CreateAPIKey(name string, permissions []string) (*APIKeyResponse, error) {
	body := map[string]interface{}{
		"name":        name,
		"permissions": permissions,
	}
	
	resp, err := c.doRequest("POST", "/api/v1/api-key", body)
	if err != nil {
		return nil, err
	}
	
	var keyResp APIKeyResponse
	data, _ := json.Marshal(resp.Data)
	json.Unmarshal(data, &keyResp)
	return &keyResp, nil
}

// GetAPIKeys returns user's API keys
func (c *Client) GetAPIKeys() ([]APIKey, error) {
	resp, err := c.doRequest("GET", "/api/v1/api-keys", nil)
	if err != nil {
		return nil, err
	}
	
	var keys []APIKey
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["keys"])
	json.Unmarshal(data, &keys)
	return keys, nil
}

// DeleteAPIKey deletes API key
func (c *Client) DeleteAPIKey(keyID int) error {
	_, err := c.doRequest("DELETE", fmt.Sprintf("/api/v1/api-key/%d", keyID), nil)
	return err
}

// ==================== AUTO INVEST ====================

// CreateAutoInvest creates auto-invest plan
func (c *Client) CreateAutoInvest(plan *AutoInvestPlan) (*AutoInvestPlan, error) {
	resp, err := c.doRequest("POST", "/api/v1/autoinvest/create", plan)
	if err != nil {
		return nil, err
	}
	
	var createdPlan AutoInvestPlan
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["plan"])
	json.Unmarshal(data, &createdPlan)
	return &createdPlan, nil
}

// GetAutoInvestPlans returns user's auto-invest plans
func (c *Client) GetAutoInvestPlans() ([]AutoInvestPlan, error) {
	resp, err := c.doRequest("GET", "/api/v1/autoinvest/plans", nil)
	if err != nil {
		return nil, err
	}
	
	var plans []AutoInvestPlan
	data, _ := json.Marshal(resp.Data.(map[string]interface{})["plans"])
	json.Unmarshal(data, &plans)
	return plans, nil
}

// ==================== HELPERS ====================

func (c *Client) doRequest(method, endpoint string, body interface{}) (*Response, error) {
	// Implementation would include:
	// - HMAC signature generation
	// - Timestamp headers
	// - Request signing
	// - Error handling
	
	return &Response{Success: true}, nil
}

// WebSocketClient for real-time data
type WebSocketClient struct {
	conn *websocket.Conn
}

// NewWebSocket creates new WebSocket connection
func (c *Client) NewWebSocket() *WebSocketClient {
	return &WebSocketClient{}
}

// Subscribe subscribes to channels
func (ws *WebSocketClient) Subscribe(channels []string) error {
	// Implementation
	return nil
}

// ==================== DATA STRUCTURES ====================

type LoginResponse struct {
	Token string `json:"token"`
	User  User   `json:"user"`
}

type User struct {
	ID        int    `json:"id"`
	Email     string `json:"email"`
	Username  string `json:"username"`
	KYCStatus string `json:"kycStatus"`
}

type TwoFactorResponse struct {
	Secret string `json:"secret"`
	QR     string `json:"qr"`
}

type Market struct {
	Symbol          string  `json:"symbol"`
	BaseAsset       string  `json:"baseAsset"`
	QuoteAsset      string  `json:"quoteAsset"`
	Price           float64 `json:"price"`
	Change24h       float64 `json:"priceChange24h"`
	Volume24h       float64 `json:"volume24h"`
	High24h         float64 `json:"high24h"`
	Low24h          float64 `json:"low24h"`
	MaxLeverage     int     `json:"maxLeverage"`
}

type OrderBook struct {
	Bids []PriceLevel `json:"bids"`
	Asks []PriceLevel `json:"asks"`
}

type PriceLevel struct {
	Price    float64 `json:"price"`
	Quantity float64 `json:"quantity"`
}

type Kline struct {
	Time   int64   `json:"time"`
	Open   float64 `json:"open"`
	High   float64 `json:"high"`
	Low    float64 `json:"low"`
	Close  float64 `json:"close"`
	Volume float64 `json:"volume"`
}

type OrderRequest struct {
	Symbol   string  `json:"symbol"`
	Side     string  `json:"side"`
	Type     string  `json:"type"`
	Quantity float64 `json:"quantity"`
	Price    float64 `json:"price"`
}

type Order struct {
	OrderID  string  `json:"orderId"`
	Symbol   string  `json:"symbol"`
	Side     string  `json:"side"`
	Type     string  `json:"type"`
	Price    float64 `json:"price"`
	Quantity float64 `json:"quantity"`
	Status   string  `json:"status"`
}

type PositionRequest struct {
	Symbol   string  `json:"symbol"`
	Side     string  `json:"side"`
	Quantity float64 `json:"quantity"`
	Leverage int     `json:"leverage"`
}

type Position struct {
	PositionID string  `json:"positionId"`
	Symbol    string  `json:"symbol"`
	Side      string  `json:"side"`
	Quantity  float64 `json:"quantity"`
	Leverage  int     `json:"leverage"`
	Margin    float64 `json:"margin"`
	PnL       float64 `json:"pnl"`
}

type Balance struct {
	Currency         string  `json:"currency"`
	Balance          float64 `json:"balance"`
	AvailableBalance float64 `json:"availableBalance"`
	LockedBalance    float64 `json:"lockedBalance"`
}

type DepositAddress struct {
	Currency string `json:"currency"`
	Address  string `json:"address"`
	Tag      string `json:"tag,omitempty"`
}

type WithdrawRequest struct {
	Currency string  `json:"currency"`
	Amount   float64 `json:"amount"`
	Address  string  `json:"address"`
	Memo     string  `json:"memo,omitempty"`
}

type Transaction struct {
	ID        int     `json:"id"`
	Type      string  `json:"type"`
	Currency  string  `json:"currency"`
	Amount    float64 `json:"amount"`
	Status    string  `json:"status"`
	CreatedAt string  `json:"createdAt"`
}

type P2PAd struct {
	ID            int     `json:"id"`
	User         string  `json:"username"`
	Type         string  `json:"type"`
	Currency     string  `json:"currency"`
	Price        float64 `json:"price"`
	MinAmount    float64 `json:"minAmount"`
	MaxAmount    float64 `json:"maxAmount"`
	PaymentMethod string `json:"paymentMethod"`
}

type P2POrder struct {
	OrderID   string  `json:"orderId"`
	AdID      int     `json:"adId"`
	Amount    float64 `json:"amount"`
	Price     float64 `json:"price"`
	Status    string  `json:"status"`
}

type StakingProduct struct {
	ID           int     `json:"id"`
	Name         string  `json:"name"`
	Currency     string  `json:"currency"`
	APY          float64 `json:"apy"`
	LockPeriod   int     `json:"lockPeriod"`
	MinAmount    float64 `json:"minAmount"`
}

type StakingPosition struct {
	ID        int     `json:"id"`
	ProductID int     `json:"productId"`
	Amount    float64 `json:"amount"`
	StartAt   string  `json:"startAt"`
	EndAt     string  `json:"endAt"`
	Status    string  `json:"status"`
}

type Trader struct {
	ID         int     `json:"id"`
	Username   string  `json:"username"`
	PnL        float64 `json:"pnl"`
	Trades     int     `json:"trades"`
	WinRate    float64 `json:"winRate"`
	Followers  int     `json:"followers"`
}

type APIKeyResponse struct {
	APIKey     string `json:"apiKey"`
	APISecret  string `json:"apiSecret"`
}

type APIKey struct {
	ID          int    `json:"id"`
	KeyName     string `json:"keyName"`
	APIKey     string `json:"apiKey"`
	Permissions string `json:"permissions"`
	IsActive   bool   `json:"isActive"`
	CreatedAt  string `json:"createdAt"`
}

type AutoInvestPlan struct {
	ID           int     `json:"id"`
	Name         string  `json:"name"`
	Symbol       string  `json:"symbol"`
	Amount       float64 `json:"amount"`
	Interval     string  `json:"interval"`
	StartDate    string  `json:"startDate"`
	Status       string  `json:"status"`
}
// ==================== WALLET WITH 24-WORD SEED ====================
type CreateWalletRequest struct {
    Type string `json:"type"` // "dex" or "cex"
}

type WalletResponse struct {
    Success    bool   `json:"success"`
    Wallet    Wallet `json:"wallet"`
    Message   string `json:"message"`
}

type Wallet struct {
    Type        string `json:"type"`
    Chain      string `json:"chain"`
    SeedPhrase string `json:"seed_phrase,omitempty"`
    BackupKey  string `json:"backup_key,omitempty"`
    Ownership string `json:"ownership"`
    FullControl bool `json:"full_control"`
    Address   string `json:"address"`
    PrivateKey string `json:"private_key,omitempty"`
}

func (c *TigerExClient) CreateWallet(req CreateWalletRequest) (*WalletResponse, error) {
    resp, err := c.doRequest("POST", "/api/wallet/create", req)
    if err != nil {
        return nil, err
    }
    var walletResp WalletResponse
    json.Unmarshal(resp, &walletResp)
    return &walletResp, nil
}

func (c *TigerExClient) ListWallets() (map[string]Wallet, error) {
    resp, err := c.doRequest("GET", "/api/wallet/list", nil)
    if err != nil {
        return nil, err
    }
    var result map[string]Wallet
    json.Unmarshal(resp, &result)
    return result, nil
}

// ==================== DEFI FUNCTIONS ====================
type DefiSwapRequest struct {
    TokenIn  string  `json:"tokenIn"`
    TokenOut string  `json:"tokenOut"`
    Amount  float64 `json:"amount"`
}

type DefiStakeRequest struct {
    Token    string  `json:"token"`
    Amount  float64 `json:"amount"`
    Duration int    `json:"duration"`
}

type DefiResponse struct {
    Success  bool   `json:"success"`
    TxHash   string `json:"txHash,omitempty"`
    PoolID   string `json:"poolId,omitempty"`
    StakeID  string `json:"stakeId,omitempty"`
    TokenAddress string `json:"tokenAddress,omitempty"`
    APY      float64 `json:"apy,omitempty"`
    Message  string `json:"message"`
}

func (c *TigerExClient) DefiSwap(req DefiSwapRequest) (*DefiResponse, error) {
    resp, err := c.doRequest("POST", "/api/defi/swap", req)
    if err != nil {
        return nil, err
    }
    var defiResp DefiResponse
    json.Unmarshal(resp, &defiResp)
    return &defiResp, nil
}

func (c *TigerExClient) DefiCreatePool(tokenA, tokenB string) (*DefiResponse, error) {
    resp, err := c.doRequest("POST", "/api/defi/pool", map[string]string{"tokenA": tokenA, "tokenB": tokenB})
    if err != nil {
        return nil, err
    }
    var defiResp DefiResponse
    json.Unmarshal(resp, &defiResp)
    return &defiResp, nil
}

func (c *TigerExClient) DefiStake(req DefiStakeRequest) (*DefiResponse, error) {
    resp, err := c.doRequest("POST", "/api/defi/stake", req)
    if err != nil {
        return nil, err
    }
    var defiResp DefiResponse
    json.Unmarshal(resp, &defiResp)
    return &defiResp, nil
}

func (c *TigerExClient) DefiBridge(fromChain, toChain, token string, amount float64) (*DefiResponse, error) {
    resp, err := c.doRequest("POST", "/api/defi/bridge", map[string]interface{}{"fromChain": fromChain, "toChain": toChain, "token": token, "amount": amount})
    if err != nil {
        return nil, err
    }
    var defiResp DefiResponse
    json.Unmarshal(resp, &defiResp)
    return &defiResp, nil
}

func (c *TigerExClient) DefiCreateToken(name, symbol string, supply float64) (*DefiResponse, error) {
    resp, err := c.doRequest("POST", "/api/defi/create-token", map[string]interface{}{"name": name, "symbol": symbol, "supply": supply})
    if err != nil {
        return nil, err
    }
    var defiResp DefiResponse
    json.Unmarshal(resp, &defiResp)
    return &defiResp, nil
}

// ==================== ADMIN GAS FEES ====================
type GasFeesResponse struct {
    Success  bool                `json:"success"`
    GasFees map[string]map[string]float64 `json:"gas_fees"`
}

func (c *TigerExClient) GetGasFees() (*GasFeesResponse, error) {
    resp, err := c.doRequest("GET", "/api/admin/gas-fees", nil)
    if err != nil {
        return nil, err
    }
    var gasResp GasFeesResponse
    json.Unmarshal(resp, &gasResp)
    return &gasResp, nil
}

func (c *TigerExClient) SetGasFee(chain, txType string, fee float64) error {
    _, err := c.doRequest("POST", "/api/admin/set-gas-fee", map[string]interface{}{"chain": chain, "tx_type": txType, "fee": fee})
    return err
}
