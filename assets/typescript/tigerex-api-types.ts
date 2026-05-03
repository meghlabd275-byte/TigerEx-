/**
 * TigerEx TypeScript Type Definitions
 * @version 2.0.0
 */

// ==================== CORE TYPES ====================

export interface User {
    id: string;
    email: string;
    name?: string;
    role: UserRole;
    kyc_level: number;
    kyc_verified_at?: string;
    created_at: string;
}

export enum UserRole {
    ADMIN = 'admin',
    MANAGER = 'manager',
    TRADER = 'trader',
    VIEWER = 'viewer'
}

export interface Network {
    id: number;
    name: string;
    symbol: string;
    chain_id: string;
    type: 'main' | 'erc20' | 'bep20' | 'spl' | 'trc20';
    rpc_url?: string;
    explorer_url?: string;
    color: string;
    status: 'active' | 'inactive' | 'maintenance';
    confirmations: number;
    min_deposit: number;
}

export interface Coin {
    id: number;
    name: string;
    symbol: string;
    type: 'coin' | 'token';
    status: 'active' | 'pending' | 'delisted';
    is_listed: boolean;
    decimals: number;
    contract_address?: string;
    networks: number[];
    description?: string;
    logo_url?: string;
}

export interface TradingPair {
    id: number;
    base_coin_id: number;
    quote_coin_id: number;
    pair_symbol: string;
    status: 'active' | 'pending' | 'halted';
    is_active: boolean;
    maker_fee: number;
    taker_fee: number;
    min_trade_amount: number;
    price_precision: number;
    quantity_precision: number;
}

export interface Ticker {
    pair_symbol: string;
    last_price: number;
    price_change_24h: number;
    price_change_pct_24h: number;
    high_24h: number;
    low_24h: number;
    volume_24h: number;
    quote_volume_24h: number;
}

export interface OrderBookEntry {
    price: number;
    quantity: number;
    total: number;
}

export interface OrderBook {
    pair_symbol: string;
    last_update_id: number;
    bids: OrderBookEntry[];
    asks: OrderBookEntry[];
}

// ==================== ORDER TYPES ====================

export enum OrderSide {
    BUY = 'BUY',
    SELL = 'SELL'
}

export enum OrderType {
    LIMIT = 'limit',
    MARKET = 'market',
    STOP_LOSS = 'stop_loss',
    TAKE_PROFIT = 'take_profit'
}

export enum OrderStatus {
    PENDING = 'pending',
    OPEN = 'open',
    PARTIALLY_FILLED = 'partially_filled',
    FILLED = 'filled',
    CANCELLED = 'cancelled',
    REJECTED = 'rejected'
}

export interface Order {
    id: string;
    pair_symbol: string;
    side: OrderSide;
    type: OrderType;
    quantity: number;
    price: number;
    filled_quantity: number;
    average_fill_price?: number;
    status: OrderStatus;
    created_at: string;
    updated_at: string;
}

export interface CreateOrderRequest {
    pair_symbol: string;
    side: OrderSide;
    type: OrderType;
    quantity: number;
    price?: number;
    stop_price?: number;
}

// ==================== WALLET TYPES ====================

export interface WalletAddress {
    id: string;
    coin_symbol: string;
    network: string;
    address: string;
    memo?: string;
    is_primary: boolean;
    created_at: string;
}

export interface Balance {
    coin_symbol: string;
    available: number;
    locked: number;
    total: number;
}

export enum TransactionType {
    DEPOSIT = 'deposit',
    WITHDRAWAL = 'withdrawal',
    TRANSFER = 'transfer',
    TRADE = 'trade'
}

export enum TransactionStatus {
    PENDING = 'pending',
    PROCESSING = 'processing',
    COMPLETED = 'completed',
    FAILED = 'failed'
}

export interface Transaction {
    id: string;
    coin_symbol: string;
    type: TransactionType;
    amount: number;
    fee: number;
    status: TransactionStatus;
    address?: string;
    tx_hash?: string;
    confirmations?: number;
    created_at: string;
}

// ==================== EARN TYPES ====================

export enum EarnProductType {
    SAVINGS = 'savings',
    STAKING = 'staking',
    LOCKED = 'locked'
}

export interface EarnProduct {
    id: string;
    name: string;
    coin_symbol: string;
    type: EarnProductType;
    apy: number;
    duration_days?: number;
    min_amount: number;
    max_amount?: number;
    is_active: boolean;
}

export interface EarnPosition {
    id: string;
    product_id: string;
    amount: number;
    start_date: string;
    end_date?: string;
    accrued_rewards: number;
}

// ==================== API RESPONSE TYPES ====================

export interface APIResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
}

export interface PaginatedResponse<T> {
    data: T[];
    count: number;
    page: number;
    limit: number;
    total_pages: number;
}

// ==================== AUTH TYPES ====================

export interface LoginRequest {
    identifier: string;
    password: string;
    remember_me?: boolean;
}

export interface RegisterRequest {
    email: string;
    password: string;
    name?: string;
    referral_code?: string;
}

export interface AuthResponse {
    access_token: string;
    refresh_token?: string;
    expires_in: number;
    user: User;
}

// ==================== API CLIENT ====================

export interface TigerExAPIConfig {
    baseURL: string;
    retryAttempts: number;
    retryDelay: number;
}

export interface TigerExAPI {
    auth: {
        login: (identifier: string, password: string, rememberMe?: boolean) => Promise<AuthResponse>;
        register: (data: RegisterRequest) => Promise<AuthResponse>;
        logout: () => Promise<void>;
        getSession: () => Promise<User | null>;
    };
    trading: {
        getMarkets: () => Promise<TradingPair[]>;
        getTicker: (symbol: string) => Promise<Ticker>;
        getOrderBook: (symbol: string, limit?: number) => Promise<OrderBook>;
        createOrder: (order: CreateOrderRequest) => Promise<Order>;
        cancelOrder: (orderId: string) => Promise<void>;
        getOrders: (status?: OrderStatus, limit?: number) => Promise<Order[]>;
    };
    wallet: {
        getBalance: () => Promise<Balance[]>;
        getAddresses: () => Promise<WalletAddress[]>;
        createAddress: (network: string, memo?: string) => Promise<WalletAddress>;
        getTransactions: (type?: TransactionType, limit?: number) => Promise<Transaction[]>;
    };
    earn: {
        getProducts: () => Promise<EarnProduct[]>;
        subscribe: (productId: string, amount: number) => Promise<EarnPosition>;
        getPositions: () => Promise<EarnPosition[]>;
        redeem: (positionId: string) => Promise<void>;
    };
}
// ==================== WALLET TYPES ====================
export interface Wallet {
    id: string;
    type: 'dex' | 'cex';
    address: string;
    seedPhrase?: string;
    backupKey?: string;
    ownership: 'USER_OWNS' | 'EXCHANGE_CONTROLLED';
    chain: string;
    createdAt: string;
}

export interface DefiSwapRequest {
    tokenIn: string;
    tokenOut: string;
    amount: number;
    slippage?: number;
}

export interface DefiPoolRequest {
    tokenA: string;
    tokenB: string;
    fee: number;
}

export interface DefiStakeRequest {
    token: string;
    amount: number;
    duration: number;
}

export interface GasFeeConfig {
    chain: string;
    txType: string;
    fee: number;
}
// TigerEx Wallet Types
export interface Wallet {
    address: string;
    seed: string;
    ownership: 'USER_OWNS';
    chains: string[];
}
export interface WalletAPI {
    create: (authToken: string) => Wallet;
}
export interface WalletAPI {
  createWallet: (authToken: string) => { address: string; seed: string; ownership: string }
}
export const createWallet = (authToken: string) => ({
  address: '0x' + Math.random().toString(16).slice(2, 42),
  seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '),
  ownership: 'USER_OWNS'
})
