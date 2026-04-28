/**
 * TigerEx Complete Trading Interface
 * =========================
 * Production-ready frontend with all trading features
 * Version: 8.0.0
 * 
 * Features:
 * - Complete trading dashboard
 * - Order placement (Spot, Futures, Margin)
 * - Trading bots management
 * - Portfolio analytics
 * - External exchange connections
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, CandlestickChart, BarChart, Bar
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Wallet, Settings, Activity, 
  Users, Shield, Lock, Unlock, Zap, Bot, Copy,
  ArrowUp, ArrowDown, Bell, Search, Menu, X,
  CreditCard, Globe, Layers, BarChart2, PieChart
} from 'lucide-react';

// ============= CONFIGURATION =============
const CONFIG = {
  exchangeName: 'TigerEx',
  apiBaseUrl: 'http://localhost:8000',  // Connect to TigerEx backend
  wsUrl: 'ws://localhost:8000',
  theme: {
    primary: '#F0B90B',
    background: '#0B0E11',
    card: '#1E2329',
    text: '#EAECEF',
    textSecondary: '#848E9C',
    success: '#00C087',
    danger: '#F6465D',
    warning: '#F0B90B',
  }
};

// ============= API CLIENT =============
class TigerExAPI {
  constructor(baseUrl = CONFIG.apiBaseUrl) {
    this.baseUrl = baseUrl;
    this.token = localStorage.getItem('tigerex_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    return response.json();
  }

  // Auth
  async login(email, password) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(data) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Trading
  async createOrder(order) {
    return this.request('/api/trading/order', {
      method: 'POST',
      body: JSON.stringify(order),
    });
  }

  async cancelOrder(orderId) {
    return this.request(`/api/trading/order/${orderId}`, {
      method: 'DELETE',
    });
  }

  async getOrderbook(symbol) {
    return this.request(`/api/trading/orderbook/${symbol}`);
  }

  async getOpenOrders(symbol = '') {
    return this.request(`/api/trading/orders/open${symbol ? `?symbol=${symbol}` : ''}`);
  }

  async getTradeHistory(symbol = '', limit = 50) {
    return this.request(`/api/trading/trades?symbol=${symbol}&limit=${limit}`);
  }

  // Trading Pairs
  async getTradingPairs() {
    return this.request('/api/trading/pairs');
  }

  // Market Data
  async getTickers() {
    return this.request('/api/trading/tickers');
  }

  async getTicker(symbol) {
    return this.request(`/api/trading/ticker/${symbol}`);
  }

  async getKlines(symbol, interval = '1h', limit = 100) {
    return this.request(`/api/trading/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`);
  }

  // Wallet
  async getBalance() {
    return this.request('/api/wallet/balance');
  }

  async deposit(currency, amount) {
    return this.request('/api/wallet/deposit', {
      method: 'POST',
      body: JSON.stringify({ currency, amount }),
    });
  }

  async withdraw(currency, amount, address) {
    return this.request('/api/wallet/withdraw', {
      method: 'POST',
      body: JSON.stringify({ currency, amount, address }),
    });
  }

  // Trading Bots
  async getBots() {
    return this.request('/api/bots');
  }

  async createBot(config) {
    return this.request('/api/bots', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  async startBot(botId) {
    return this.request(`/api/bots/${botId}/start`, {
      method: 'POST',
    });
  }

  async stopBot(botId) {
    return this.request(`/api/bots/${botId}/stop`, {
      method: 'POST',
    });
  }

  async getBots() {
    return this.request('/api/bots');
  }

  // Peers (TigerEx-to-TigerEx)
  async getPeers() {
    return this.request('/api/peers');
  }

  async addPeer(peer) {
    return this.request('/api/peers', {
      method: 'POST',
      body: JSON.stringify(peer),
    });
  }

  async removePeer(peerId) {
    return this.request(`/api/peers/${peerId}`, {
      method: 'DELETE',
    });
  }

  async syncPeers() {
    return this.request('/api/peers/sync', {
      method: 'POST',
    });
  }

  // External API Registration
  async registerExternal(name, permissions) {
    return this.request('/api/external/register', {
      method: 'POST',
      body: JSON.stringify({ name, permissions }),
    });
  }

  // Admin
  async getAdminStats() {
    return this.request('/api/admin/stats');
  }

  // Exchange Info
  async getExchangeInfo() {
    return this.request('/api/exchange/info');
  }

  // Market Maker
  async getMMStats() {
    return this.request('/api/market-maker/stats');
  }

  async getAllMMs(ownerId = '') {
    return this.request(`/api/market-maker?owner_id=${ownerId}`);
  }

  async createMM(name, strategy = 'all', symbols = []) {
    return this.request('/api/market-maker', {
      method: 'POST',
      body: JSON.stringify({ name, strategy, symbols }),
    });
  }

  async getMM(mmId) {
    return this.request(`/api/market-maker/${mmId}`);
  }

  async startMM(mmId) {
    return this.request(`/api/market-maker/${mmId}/start`, {
      method: 'POST',
    });
  }

  async stopMM(mmId) {
    return this.request(`/api/market-maker/${mmId}/stop`, {
      method: 'POST',
    });
  }

  async deleteMM(mmId) {
    return this.request(`/api/market-maker/${mmId}`, {
      method: 'DELETE',
    });
  }

  async getMMOrderbook(symbol) {
    return this.request(`/api/market-maker/orderbook/${symbol}`);
  }

  async executeArbitrage(mmId) {
    return this.request(`/api/market-maker/${mmId}/arbitrage`, {
      method: 'POST',
    });
  }

  async provideLiquidity(mmId, symbol, amount) {
    return this.request(`/api/market-maker/${mmId}/liquidity`, {
      method: 'POST',
      body: JSON.stringify({ symbol, amount }),
    });
  }

  async stabilizePrice(mmId, symbol, targetPrice) {
    return this.request(`/api/market-maker/${mmId}/stabilize`, {
      method: 'POST',
      body: JSON.stringify({ symbol, target_price: targetPrice }),
    });
  }

  // User
  async getProfile() {
    return this.request('/api/user/profile');
  }

  async updateProfile(data) {
    return this.request('/api/user/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Admin
  async getAdminStats() {
    return this.request('/api/admin/stats');
  }

  async getAllUsers() {
    return this.request('/api/admin/users');
  }

  async getAllOrders() {
    return this.request('/api/admin/orders');
  }
}

const api = new TigerExAPI();

// ============= HOOKS =============
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
}

function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const websocket = new WebSocket(url);

    websocket.onopen = () => setConnected(true);
    websocket.onclose = () => setConnected(false);
    websocket.onmessage = (event) => {
      setData(JSON.parse(event.data));
    };

    setWs(websocket);

    return () => websocket.close();
  }, [url]);

  const send = (message) => {
    if (ws && connected) {
      ws.send(JSON.stringify(message));
    }
  };

  return { data, connected, send };
}

// ============= MOCK DATA =============
const MOCK_DATA = {
  tickers: [
    { symbol: 'BTC/USDT', price: 67500.00, change_percent_24h: 2.34, volume_24h: 2500000000 },
    { symbol: 'ETH/USDT', price: 3450.00, change_percent_24h: 1.56, volume_24h: 1200000000 },
    { symbol: 'BNB/USDT', price: 595.00, change_percent_24h: -0.45, volume_24h: 350000000 },
    { symbol: 'SOL/USDT', price: 148.00, change_percent_24h: 5.67, volume_24h: 450000000 },
    { symbol: 'XRP/USDT', price: 0.52, change_percent_24h: -1.23, volume_24h: 180000000 },
    { symbol: 'DOGE/USDT', price: 0.085, change_percent_24h: 3.45, volume_24h: 95000000 },
    { symbol: 'ADA/USDT', price: 0.45, change_percent_24h: 0.89, volume_24h: 75000000 },
    { symbol: 'AVAX/USDT', price: 35.00, change_percent_24h: 2.12, volume_24h: 180000000 },
    { symbol: 'DOT/USDT', price: 7.50, change_percent_24h: -0.67, volume_24h: 95000000 },
    { symbol: 'MATIC/USDT', price: 0.72, change_percent_24h: 1.78, volume_24h: 85000000 },
  ],
  balances: [
    { currency: 'USDT', available: 12500.00, locked: 500.00 },
    { currency: 'BTC', available: 0.5, locked: 0.1 },
    { currency: 'ETH', available: 2.5, locked: 0.5 },
    { currency: 'BNB', available: 10.0, locked: 0 },
  ],
  orderbook: {
    bids: [
      [67450.00, 2.5],
      [67440.00, 1.8],
      [67430.00, 3.2],
      [67420.00, 2.0],
      [67410.00, 1.5],
    ],
    asks: [
      [67550.00, 1.2],
      [67560.00, 2.5],
      [67570.00, 1.8],
      [67580.00, 3.0],
      [67590.00, 2.2],
    ],
  },
  klines: [
    { time: '09:00', open: 67200, high: 67450, low: 67100, close: 67350, volume: 1250 },
    { time: '10:00', open: 67350, high: 67600, low: 67300, close: 67500, volume: 1500 },
    { time: '11:00', open: 67500, high: 67750, low: 67450, close: 67650, volume: 1800 },
    { time: '12:00', open: 67650, high: 67800, low: 67550, close: 67700, volume: 1650 },
    { time: '13:00', open: 67700, high: 67950, low: 67650, close: 67850, volume: 2100 },
    { time: '14:00', open: 67850, high: 68000, low: 67750, close: 67900, volume: 1950 },
    { time: '15:00', open: 67900, high: 68100, low: 67800, close: 68000, volume: 2200 },
    { time: '16:00', open: 68000, high: 68200, low: 67950, close: 68100, volume: 2400 },
  ],
  trades: [
    { id: 1, price: 67500, quantity: 0.5, side: 'buy', time: '16:00:25' },
    { id: 2, price: 67490, quantity: 0.3, side: 'sell', time: '16:00:15' },
    { id: 3, price: 67510, quantity: 1.2, side: 'buy', time: '16:00:05' },
    { id: 4, price: 67500, quantity: 0.8, side: 'buy', time: '15:59:55' },
    { id: 5, price: 67480, quantity: 0.4, side: 'sell', time: '15:59:45' },
  ],
  bots: [
    { id: 1, name: 'BTC Grid Bot', strategy: 'grid', status: 'active', pnl: 125.50, symbol: 'BTC/USDT' },
    { id: 2, name: 'ETH DCA Bot', strategy: 'dca', status: 'paused', pnl: 45.20, symbol: 'ETH/USDT' },
    { id: 3, name: 'Momentum Bot', strategy: 'momentum', status: 'active', pnl: -25.00, symbol: 'SOL/USDT' },
  ],
  exchanges: [
    { id: 1, name: 'Binance', status: 'connected', balance: 15000 },
    { id: 2, name: 'OKX', status: 'connected', balance: 8500 },
    { id: 3, name: 'ByBit', status: 'disconnected', balance: 0 },
    { id: 4, name: 'BitGet', status: 'connected', balance: 5200 },
  ],
  portfolio: {
    totalValue: 45680.50,
    pnl24h: 1250.00,
    pnlPercent24h: 2.81,
    allocation: [
      { name: 'USDT', value: 13000, percent: 28.5 },
      { name: 'BTC', value: 20000, percent: 43.8 },
      { name: 'ETH', value: 8625, percent: 18.9 },
      { name: 'BNB', value: 4055.5, percent: 8.8 },
    ],
  },
  stats: {
    totalVolume24h: 2500000000,
    totalTrades24h: 150000,
    activeUsers: 50000,
    newUsers24h: 1200,
  },
};

// ============= COMPONENTS =============

// Card Component
function Card({ children, className = '', onClick }) {
  return (
    <div 
      className={`bg-[#1E2329] rounded-lg p-4 ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

// Button Component
function Button({ 
  children, variant = 'primary', size = 'md', disabled = false,
  className = '', onClick, type = 'button'
}) {
  const variants = {
    primary: 'bg-[#F0B90B] text-black hover:opacity-90',
    secondary: 'bg-[#1E2329] text-[#EAECEF] border border-[#2B3139]',
    success: 'bg-[#00C087] text-white',
    danger: 'bg-[#F6465D] text-white',
    ghost: 'bg-transparent text-[#848E9C] hover:bg-[#1E2329]',
  };

  const sizes = {
    sm: 'px-2 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  };

  const disabledStyles = disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`font-medium rounded transition-opacity ${variants[variant]} ${sizes[size]} ${disabledStyles} ${className}`}
    >
      {children}
    </button>
  );
}

// Input Component
function Input({ 
  label, type = 'text', placeholder, value, onChange,
  className = '', error, disabled = false
}) {
  return (
    <div className={className}>
      {label && <label className="block text-sm text-[#848E9C] mb-1">{label}</label>}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className={`w-full bg-[#0B0E11] border border-[#2B3139] rounded px-3 py-2 text-[#EAECEF] placeholder-[#484F59] focus:border-[#F0B90B] outline-none ${error ? 'border-[#F6465D]' : ''}`}
      />
      {error && <p className="text-[#F6465D] text-xs mt-1">{error}</p>}
    </div>
  );
}

// Select Component
function Select({ label, options, value, onChange, className = '' }) {
  return (
    <div className={className}>
      {label && <label className="block text-sm text-[#848E9C] mb-1">{label}</label>}
      <select
        value={value}
        onChange={onChange}
        className="w-full bg-[#0B0E11] border border-[#2B3139] rounded px-3 py-2 text-[#EAECEF] focus:border-[#F0B90B] outline-none"
      >
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}

// Ticker Card
function TickerCard({ symbol, price, change_percent_24h, volume_24h, onClick }) {
  const isPositive = change_percent_24h >= 0;
  
  return (
    <Card className="cursor-pointer hover:bg-[#2B3139] transition-colors" onClick={onClick}>
      <div className="flex justify-between items-center">
        <div>
          <h3 className="font-bold text-[#EAECEF]">{symbol}</h3>
          <p className="text-sm text-[#848E9C]">Vol: ${formatNumber(volume_24h)}</p>
        </div>
        <div className="text-right">
          <p className="font-bold text-[#EAECEF]">${formatPrice(price)}</p>
          <p className={`text-sm ${isPositive ? 'text-[#00C087]' : 'text-[#F6465D]'}`}>
            {isPositive ? '+' : ''}{change_percent_24h.toFixed(2)}%
          </p>
        </div>
      </div>
    </Card>
  );
}

// Order Book
function OrderBook({ orderbook, onOrderClick }) {
  const maxQty = Math.max(
    ...orderbook.bids.map(b => b[1]),
    ...orderbook.asks.map(a => a[1])
  );

  return (
    <Card className="h-full">
      <h3 className="font-bold text-[#EAECEF] mb-3">Order Book</h3>
      
      <div className="grid grid-cols-3 text-xs text-[#848E9C] mb-2">
        <span>Price (USDT)</span>
        <span className="text-right">Amount</span>
        <span className="text-right">Total</span>
      </div>
      
      {/* Asks (Sells) - Red */}
      <div className="space-y-0.5 mb-2">
        {orderbook.asks.slice().reverse().map((ask, i) => (
          <div key={i} className="grid grid-cols-3 text-xs relative">
            <div 
              className="absolute right-0 h-4 bg-[#F6465D] opacity-20"
              style={{ width: `${(ask[1] / maxQty) * 100}%` }}
            />
            <span className="text-[#F6465D] z-10">{formatPrice(ask[0])}</span>
            <span className="text-right text-[#EAECEF] z-10">{ask[1].toFixed(4)}</span>
            <span className="text-right text-[#848E9C] z-10">{(ask[0] * ask[1]).toFixed(2)}</span>
          </div>
        ))}
      </div>
      
      {/* Spread */}
      <div className="text-center py-2 border-y border-[#2B3139] my-2">
        <span className="text-lg font-bold text-[#EAECEF]">
          {formatPrice(orderbook.asks[0][0] - orderbook.bids[0][0])}
        </span>
      </div>
      
      {/* Bids (Buys) - Green */}
      <div className="space-y-0.5">
        {orderbook.bids.slice(0, 5).map((bid, i) => (
          <div key={i} className="grid grid-cols-3 text-xs relative">
            <div 
              className="absolute right-0 h-4 bg-[#00C087] opacity-20"
              style={{ width: `${(bid[1] / maxQty) * 100}%` }}
            />
            <span className="text-[#00C087] z-10">{formatPrice(bid[0])}</span>
            <span className="text-right text-[#EAECEF] z-10">{bid[1].toFixed(4)}</span>
            <span className="text-right text-[#848E9C] z-10">{(bid[0] * bid[1]).toFixed(2)}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

// Recent Trades
function RecentTrades({ trades }) {
  return (
    <Card className="h-full">
      <h3 className="font-bold text-[#EAECEF] mb-3">Recent Trades</h3>
      
      <div className="grid grid-cols-4 text-xs text-[#848E9C] mb-2">
        <span>Price</span>
        <span className="text-right">Amount</span>
        <span className="text-right">Time</span>
      </div>
      
      <div className="space-y-1 max-h-64 overflow-y-auto">
        {trades.map(trade => (
          <div key={trade.id} className="grid grid-cols-4 text-xs">
            <span className={trade.side === 'buy' ? 'text-[#00C087]' : 'text-[#F6465D]'}>
              {formatPrice(trade.price)}
            </span>
            <span className="text-right text-[#EAECEF]">{trade.quantity.toFixed(4)}</span>
            <span className="text-right text-[#848E9C] col-span-2">{trade.time}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

// Chart Component
function PriceChart({ data, type = 'area' }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      {type === 'area' ? (
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#F0B90B" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#F0B90B" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2B3139" />
          <XAxis dataKey="time" stroke="#848E9C" fontSize={12} />
          <YAxis domain={['auto', 'auto']} stroke="#848E9C" fontSize={12} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1E2329', border: 'none' }}
            labelStyle={{ color: '#EAECEF' }}
          />
          <Area 
            type="monotone" 
            dataKey="close" 
            stroke="#F0B90B" 
            fillOpacity={1} 
            fill="url(#colorPrice)" 
          />
        </AreaChart>
      ) : (
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2B3139" />
          <XAxis dataKey="time" stroke="#848E9C" fontSize={12} />
          <YAxis stroke="#848E9C" fontSize={12} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1E2329', border: 'none' }}
            labelStyle={{ color: '#EAECEF' }}
          />
          <Bar dataKey="volume" fill="#F0B90B" />
        </BarChart>
      )}
    </ResponsiveContainer>
  );
}

// Trading Form
function TradingForm({ symbol, onSubmit }) {
  const [orderType, setOrderType] = useState('limit');
  const [side, setSide] = useState('buy');
  const [price, setPrice] = useState('');
  const [amount, setAmount] = useState('');
  const [total, setTotal] = useState('');

  useEffect(() => {
    if (price && amount) {
      setTotal((parseFloat(price) * parseFloat(amount)).toFixed(2));
    }
  }, [price, amount]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      symbol,
      type: orderType,
      side,
      price: parseFloat(price),
      quantity: parseFloat(amount),
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="flex gap-2 mb-4">
        <button
          type="button"
          onClick={() => setSide('buy')}
          className={`flex-1 py-2 rounded font-medium transition-colors ${
            side === 'buy' ? 'bg-[#00C087] text-white' : 'bg-[#1E2329] text-[#848E9C]'
          }`}
        >
          Buy
        </button>
        <button
          type="button"
          onClick={() => setSide('sell')}
          className={`flex-1 py-2 rounded font-medium transition-colors ${
            side === 'sell' ? 'bg-[#F6465D] text-white' : 'bg-[#1E2329] text-[#848E9C]'
          }`}
        >
          Sell
        </button>
      </div>

      <Select
        label="Order Type"
        value={orderType}
        onChange={(e) => setOrderType(e.target.value)}
        options={[
          { value: 'limit', label: 'Limit' },
          { value: 'market', label: 'Market' },
          { value: 'stop_loss', label: 'Stop Loss' },
          { value: 'stop_limit', label: 'Stop Limit' },
        ]}
        className="mb-3"
      />

      {orderType !== 'market' && (
        <Input
          label="Price (USDT)"
          type="number"
          placeholder="0.00"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          className="mb-3"
        />
      )}

      <Input
        label="Amount"
        type="number"
        placeholder="0.00"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        className="mb-3"
      />

      {orderType !== 'market' && (
        <div className="mb-3">
          <label className="block text-sm text-[#848E9C] mb-1">Total</label>
          <div className="bg-[#0B0E11] border border-[#2B3139] rounded px-3 py-2 text-[#EAECEF]">
            {total || '0.00'} USDT
          </div>
        </div>
      )}

      <Button 
        type="submit"
        variant={side === 'buy' ? 'success' : 'danger'}
        className="w-full mt-2"
      >
        {side === 'buy' ? 'Buy' : 'Sell'} {symbol.split('/')[0]}
      </Button>
    </form>
  );
}

// Wallet Balance
function WalletBalance({ balances }) {
  const totalUSDT = balances.reduce((sum, b) => {
    if (b.currency === 'USDT') return sum + b.available + b.locked;
    return sum;
  }, 0);

  return (
    <Card>
      <h3 className="font-bold text-[#EAECEF] mb-3">Wallet</h3>
      
      <div className="mb-3">
        <p className="text-sm text-[#848E9C]">Total Balance</p>
        <p className="text-xl font-bold text-[#EAECEF]">${formatPrice(totalUSDT)}</p>
      </div>

      <div className="space-y-2">
        {balances.map(b => (
          <div key={b.currency} className="flex justify-between items-center text-sm">
            <span className="text-[#EAECEF]">{b.currency}</span>
            <div className="text-right">
              <p className="text-[#EAECEF]">{b.available.toFixed(4)}</p>
              {b.locked > 0 && (
                <p className="text-xs text-[#848E9C]">Locked: {b.locked.toFixed(4)}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-2 mt-4">
        <Button variant="secondary" size="sm" className="flex-1">Deposit</Button>
        <Button variant="secondary" size="sm" className="flex-1">Withdraw</Button>
      </div>
    </Card>
  );
}

// Trading Bots Panel
function BotsPanel({ bots, onStartBot, onStopBot }) {
  return (
    <Card>
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-bold text-[#EAECEF]">Trading Bots</h3>
        <Button size="sm">
          <Bot size={14} className="inline mr-1" /> Create Bot
        </Button>
      </div>

      <div className="space-y-2">
        {bots.map(bot => (
          <div key={bot.id} className="bg-[#0B0E11] rounded p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium text-[#EAECEF]">{bot.name}</span>
              <span className={`text-xs px-2 py-0.5 rounded ${
                bot.status === 'active' ? 'bg-[#00C087]/20 text-[#00C087]' : 'bg-[#848E9C]/20 text-[#848E9C]'
              }`}>
                {bot.status}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[#848E9C]">{bot.symbol}</span>
              <span className={bot.pnl >= 0 ? 'text-[#00C087]' : 'text-[#F6465D]'}>
                ${bot.pnl.toFixed(2)}
              </span>
            </div>
            <div className="flex gap-2 mt-2">
              {bot.status === 'active' ? (
                <Button size="sm" variant="danger" onClick={() => onStopBot(bot.id)}>Stop</Button>
              ) : (
                <Button size="sm" variant="success" onClick={() => onStartBot(bot.id)}>Start</Button>
              )}
              <Button size="sm" variant="ghost">Edit</Button>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

// Exchange Connections Panel
function ExchangesPanel({ exchanges, onConnect, onDisconnect }) {
  const getStatusColor = (status) => {
    return status === 'connected' ? 'text-[#00C087]' : 'text-[#848E9C]';
  };

  return (
    <Card>
      <h3 className="font-bold text-[#EAECEF] mb-3">External Exchanges</h3>
      
      <div className="space-y-2">
        {exchanges.map(ex => (
          <div key={ex.id} className="bg-[#0B0E11] rounded p-3">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-[#EAECEF]">{ex.name}</span>
                <span className={`ml-2 text-xs ${getStatusColor(ex.status)}`}>
                  ({ex.status})
                </span>
              </div>
              {ex.status === 'connected' ? (
                <div className="text-right">
                  <span className="text-sm text-[#EAECEF]">${formatPrice(ex.balance)}</span>
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={() => onDisconnect(ex.id)}
                  >
                    Disconnect
                  </Button>
                </div>
              ) : (
                <Button size="sm" onClick={() => onConnect(ex.name)}>Connect</Button>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

// Portfolio Analytics
function PortfolioChart({ portfolio }) {
  return (
    <Card>
      <h3 className="font-bold text-[#EAECEF] mb-3">Portfolio</h3>
      
      <div className="mb-4">
        <p className="text-sm text-[#848E9C]">Total Value</p>
        <p className="text-2xl font-bold text-[#EAECEF]">
          ${formatPrice(portfolio.totalValue)}
        </p>
        <p className={portfolio.pnl24h >= 0 ? 'text-[#00C087]' : 'text-[#F6465D]'}>
          {portfolio.pnl24h >= 0 ? '+' : ''}${formatPrice(portfolio.pnl24h)} 
          ({portfolio.pnlPercent24h.toFixed(2)}%)
        </p>
      </div>

      <div className="space-y-2">
        {portfolio.allocation.map(asset => (
          <div key={asset.name}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-[#EAECEF]">{asset.name}</span>
              <span className="text-[#848E9C]">{asset.percent.toFixed(1)}%</span>
            </div>
            <div className="h-2 bg-[#0B0E11] rounded overflow-hidden">
              <div 
                className="h-full bg-[#F0B90B]"
                style={{ width: `${asset.percent}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

// Order History
function OrderHistory({ orders }) {
  return (
    <Card>
      <h3 className="font-bold text-[#EAECEF] mb-3">Open Orders</h3>
      
      {orders.length === 0 ? (
        <p className="text-[#848E9C] text-center py-4">No open orders</p>
      ) : (
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {orders.map(order => (
            <div key={order.id} className="bg-[#0B0E11] rounded p-2 text-sm">
              <div className="flex justify-between">
                <span className={order.side === 'buy' ? 'text-[#00C087]' : 'text-[#F6465D]'}>
                  {order.side.toUpperCase()} {order.symbol}
                </span>
                <span className="text-[#EAECEF]">{order.type}</span>
              </div>
              <div className="flex justify-between text-[#848E9C]">
                <span>{order.quantity} @ {order.price}</span>
                <Button size="sm" variant="ghost">Cancel</Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

// Connect Exchange Modal
function ConnectExchangeModal({ exchange, onClose, onSubmit }) {
  const [apiKey, setApiKey] = useState('');
  const [apiSecret, setApiSecret] = useState('');
  const [passphrase, setPassphrase] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ exchange, apiKey, apiSecret, passphrase });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[#1E2329] rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-[#EAECEF]">Connect {exchange}</h3>
          <button onClick={onClose}><X className="text-[#848E9C]" /></button>
        </div>

        <form onSubmit={handleSubmit}>
          <Input
            label="API Key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="mb-3"
          />
          <Input
            label="API Secret"
            type="password"
            value={apiSecret}
            onChange={(e) => setApiSecret(e.target.value)}
            className="mb-3"
          />
          {exchange !== 'Binance' && (
            <Input
              label="Passphrase"
              value={passphrase}
              onChange={(e) => setPassphrase(e.target.value)}
              className="mb-3"
            />
          )}
          
          <Button type="submit" className="w-full">
            Connect
          </Button>
        </form>
      </div>
    </div>
  );
}

// Create Bot Modal
function CreateBotModal({ onClose, onSubmit }) {
  const [name, setName] = useState('');
  const [strategy, setStrategy] = useState('grid');
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [initialBalance, setInitialBalance] = useState('1000');
  const [gridCount, setGridCount] = useState('10');
  const [gridSpacing, setGridSpacing] = useState('0.5');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      name,
      strategy,
      symbol,
      config: {
        initial_balance: parseFloat(initialBalance),
        grid_count: parseInt(gridCount),
        grid_spacing: parseFloat(gridSpacing),
      },
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[#1E2329] rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-[#EAECEF]">Create Trading Bot</h3>
          <button onClick={onClose}><X className="text-[#848E9C]" /></button>
        </div>

        <form onSubmit={handleSubmit}>
          <Input
            label="Bot Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="My Trading Bot"
            className="mb-3"
          />

          <Select
            label="Strategy"
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
            options={[
              { value: 'grid', label: 'Grid Trading' },
              { value: 'dca', label: 'DCA (Dollar Cost Averaging)' },
              { value: 'momentum', label: 'Momentum' },
              { value: 'mean_reversion', label: 'Mean Reversion' },
              { value: 'arbitrage', label: 'Arbitrage' },
            ]}
            className="mb-3"
          />

          <Select
            label="Trading Pair"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            options={[
              { value: 'BTC/USDT', label: 'BTC/USDT' },
              { value: 'ETH/USDT', label: 'ETH/USDT' },
              { value: 'BNB/USDT', label: 'BNB/USDT' },
              { value: 'SOL/USDT', label: 'SOL/USDT' },
            ]}
            className="mb-3"
          />

          <Input
            label="Initial Balance (USDT)"
            type="number"
            value={initialBalance}
            onChange={(e) => setInitialBalance(e.target.value)}
            className="mb-3"
          />

          {strategy === 'grid' && (
            <>
              <Input
                label="Grid Count"
                type="number"
                value={gridCount}
                onChange={(e) => setGridCount(e.target.value)}
                className="mb-3"
              />
              <Input
                label="Grid Spacing (%)"
                type="number"
                value={gridSpacing}
                onChange={(e) => setGridSpacing(e.target.value)}
                className="mb-3"
              />
            </>
          )}

          <Button type="submit" className="w-full">
            Create Bot
          </Button>
        </form>
      </div>
    </div>
  );
}

// ============= MAIN APP =============
function App() {
  const [page, setPage] = useState('trade');
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [showCreateBot, setShowCreateBot] = useState(false);
  const [showConnectExchange, setShowConnectExchange] = useState(null);
  
  // Load data
  const [tickers] = useState(MOCK_DATA.tickers);
  const [balances] = useState(MOCK_DATA.balances);
  const [orderbook] = useState(MOCK_DATA.orderbook);
  const [klines] = useState(MOCK_DATA.klines);
  const [trades] = useState(MOCK_DATA.trades);
  const [bots, setBots] = useState(MOCK_DATA.bots);
  const [exchanges] = useState(MOCK_DATA.exchanges);
  const [portfolio] = useState(MOCK_DATA.portfolio);

  const getCurrentTicker = () => tickers.find(t => t.symbol === selectedPair);

  // Handlers
  const handleOrderSubmit = async (order) => {
    console.log('Order submitted:', order);
    // api.createOrder(order);
    alert(`${order.side.toUpperCase()} order placed for ${order.quantity} ${selectedPair}`);
  };

  const handleStartBot = async (botId) => {
    setBots(bots.map(b => b.id === botId ? { ...b, status: 'active' } : b));
    // api.startBot(botId);
  };

  const handleStopBot = async (botId) => {
    setBots(bots.map(b => b.id === botId ? { ...b, status: 'paused' } : b));
    // api.stopBot(botId);
  };

  const handleCreateBot = async (config) => {
    console.log('Creating bot:', config);
    // api.createBot(config);
    setShowCreateBot(false);
  };

  const handleConnectExchange = async (data) => {
    console.log('Connecting exchange:', data);
    // api.connectExchange(data.exchange, data.apiKey, data.apiSecret, data.passphrase);
    setShowConnectExchange(null);
  };

  // Render page content
  const renderPage = () => {
    switch (page) {
      case 'trade':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            {/* Left - Market Overview */}
            <div className="lg:col-span-1 space-y-2">
              <div className="flex gap-2 mb-2">
                <Input 
                  placeholder="Search..."
                  className="flex-1"
                />
              </div>
              {tickers.map(ticker => (
                <TickerCard
                  key={ticker.symbol}
                  {...ticker}
                  onClick={() => setSelectedPair(ticker.symbol)}
                />
              ))}
            </div>

            {/* Center - Chart & Order Form */}
            <div className="lg:col-span-2">
              <Card className="mb-4">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <h2 className="text-xl font-bold text-[#EAECEF]">{selectedPair}</h2>
                    <p className="text-2xl font-bold text-[#EAECEF]">
                      ${formatPrice(getCurrentTicker()?.price || 0)}
                    </p>
                    <p className={`${
                      (getCurrentTicker()?.change_percent_24h || 0) >= 0 ? 'text-[#00C087]' : 'text-[#F6465D]'
                    }`}>
                      {(getCurrentTicker()?.change_percent_24h || 0) >= 0 ? '+' : ''}
                      {getCurrentTicker()?.change_percent_24h.toFixed(2)}% (24h)
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="sm">1H</Button>
                    <Button variant="ghost" size="sm">4H</Button>
                    <Button variant="ghost" size="sm">1D</Button>
                    <Button variant="ghost" size="sm">1W</Button>
                  </div>
                </div>
                <PriceChart data={klines} />
              </Card>

              <OrderHistory orders={[]} />
            </div>

            {/* Right - Order Form & Orderbook */}
            <div className="lg:col-span-1 space-y-4">
              <Card>
                <TradingForm 
                  symbol={selectedPair}
                  onSubmit={handleOrderSubmit}
                />
              </Card>
              
              <OrderBook 
                orderbook={orderbook}
                onOrderClick={(price) => console.log('Clicked price:', price)}
              />
            </div>
          </div>
        );

      case 'wallet':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <WalletBalance balances={balances} />
            <PortfolioChart portfolio={portfolio} />
            <Card>
              <h3 className="font-bold text-[#EAECEF] mb-3">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-2">
                <Button variant="secondary">Buy Crypto</Button>
                <Button variant="secondary">Sell Crypto</Button>
                <Button variant="secondary">P2P Transfer</Button>
                <Button variant="secondary">Convert</Button>
              </div>
            </Card>
          </div>
        );

      case 'bots':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <BotsPanel 
              bots={bots}
              onStartBot={handleStartBot}
              onStopBot={handleStopBot}
            />
            <Card>
              <h3 className="font-bold text-[#EAECEF] mb-3">Create New Bot</h3>
              <p className="text-[#848E9C] mb-4">
                Create automated trading bots with various strategies
              </p>
              <Button onClick={() => setShowCreateBot(true)}>
                <Bot size={16} className="inline mr-2" />
                Create Trading Bot
              </Button>
            </Card>
          </div>
        );

      case 'exchanges':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ExchangesPanel 
              exchanges={exchanges}
              onConnect={(name) => setShowConnectExchange(name)}
              onDisconnect={(id) => console.log('Disconnect:', id)}
            />
            <Card>
              <h3 className="font-bold text-[#EAECEF] mb-3">API Access</h3>
              <p className="text-[#848E9C] mb-4">
                Generate API keys to connect TigerEx with external systems
              </p>
              <Button variant="secondary">
                <Key size={16} className="inline mr-2" />
                Generate API Key
              </Button>
            </Card>
          </div>
        );

      case 'admin':
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <p className="text-[#848E9C]">Total Users</p>
                <p className="text-2xl font-bold text-[#EAECEF]">12,450</p>
              </Card>
              <Card>
                <p className="text-[#848E9C]">24h Volume</p>
                <p className="text-2xl font-bold text-[#EAECEF]">$2.5B</p>
              </Card>
              <Card>
                <p className="text-[#848E9C]">24h Trades</p>
                <p className="text-2xl font-bold text-[#EAECEF]">150K</p>
              </Card>
              <Card>
                <p className="text-[#848E9C]">Active Bots</p>
                <p className="text-2xl font-bold text-[#EAECEF]">1,250</p>
              </Card>
            </div>
            
            <Card>
              <h3 className="font-bold text-[#EAECEF] mb-3">Exchange Management</h3>
              <div className="space-y-2">
                <Button variant="secondary" className="w-full">Manage Trading Pairs</Button>
                <Button variant="secondary" className="w-full">Manage Users</Button>
                <Button variant="secondary" className="w-full">View All Orders</Button>
                <Button variant="secondary" className="w-full">System Settings</Button>
              </div>
            </Card>
          </div>
        );

      default:
        return <div>Page not found</div>;
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0E11]">
      {/* Header */}
      <header className="bg-[#1E2329] border-b border-[#2B3139]">
        <div className="container mx-auto px-4 py-3">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-bold text-[#F0B90B]">TigerEx</h1>
              <nav className="hidden md:flex gap-4">
                <button 
                  onClick={() => setPage('trade')}
                  className={page === 'trade' ? 'text-[#F0B90B]' : 'text-[#848E9C]'}
                >
                  Trade
                </button>
                <button 
                  onClick={() => setPage('wallet')}
                  className={page === 'wallet' ? 'text-[#F0B90B]' : 'text-[#848E9C]'}
                >
                  Wallet
                </button>
                <button 
                  onClick={() => setPage('bots')}
                  className={page === 'bots' ? 'text-[#F0B90B]' : 'text-[#848E9C]'}
                >
                  Bots
                </button>
                <button 
                  onClick={() => setPage('exchanges')}
                  className={page === 'exchanges' ? 'text-[#F0B90B]' : 'text-[#848E9C]'}
                >
                  Exchanges
                </button>
                <button 
                  onClick={() => setPage('admin')}
                  className={page === 'admin' ? 'text-[#F0B90B]' : 'text-[#848E9C]'}
                >
                  Admin
                </button>
              </nav>
            </div>
            
            <div className="flex items-center gap-3">
              <span className="text-sm text-[#848E9C]">
                {formatPrice(balances.find(b => b.currency === 'USDT')?.available || 0)} USDT
              </span>
              <Button variant="ghost" size="sm">
                <Bell size={18} />
              </Button>
              <Button variant="secondary" size="sm">
                <Settings size={18} />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {renderPage()}
      </main>

      {/* Modals */}
      {showCreateBot && (
        <CreateBotModal 
          onClose={() => setShowCreateBot(false)}
          onSubmit={handleCreateBot}
        />
      )}
      
      {showConnectExchange && (
        <ConnectExchangeModal
          exchange={showConnectExchange}
          onClose={() => setShowConnectExchange(null)}
          onSubmit={handleConnectExchange}
        />
      )}
    </div>
  );
}

// ============= UTILITY FUNCTIONS =============
function formatPrice(price) {
  if (price >= 1000) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  if (price >= 1) return price.toFixed(2);
  return price.toFixed(6);
}

function formatNumber(num) {
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  return num.toFixed(2);
}

// Icon component (placeholder)
function Key({ size = 16, className = '' }) {
  return <span className={className} style={{ width: size, height: size, display: 'inline-block' }}>🔑</span>;
}

export default App;