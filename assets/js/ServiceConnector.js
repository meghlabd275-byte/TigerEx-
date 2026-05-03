/**
 * TigerEx Service Connector
 * @file ServiceConnector.js
 * @description Connects frontend to all backend services
 * @author TigerEx Development Team
 */

// API Base URL - Connect to backend services
const API_BASE = window.location.port === '3000' || window.location.port === '5173' 
  ? 'http://localhost:5000/api' 
  : '/api';

// Service Endpoints
const SERVICES = {
  // Trading Services
  SPOT_TRADING: '/v1/spot/trading',
  FUTURES_TRADING: '/v1/futures/trading',
  MARGIN_TRADING: '/v1/margin/trading',
  P2P_TRADING: '/v1/p2p/trading',
  ALPHA_TRADING: '/v1/alpha/trading',
  ETF_TRADING: '/v1/etf/trading',
  TRADFI_TRADING: '/v1/tradfi/cfd',
  OPTIONS_TRADING: '/v1/options/trading',
  
  // Market Data
  MARKETS: '/v1/markets',
  ORDER_BOOK: '/v1/orderbook',
  RECENT_TRADES: '/v1/trades',
  KLINES: '/v1/klines',
  TICKER: '/v1/ticker',
  
  // Wallet & Assets
  WALLET: '/v1/wallet',
  DEPOSIT: '/v1/wallet/deposit',
  WITHDRAW: '/v1/wallet/withdraw',
  TRANSFER: '/v1/wallet/transfer',
  BALANCE: '/v1/wallet/balance',
  
  // Account
  ACCOUNT: '/v1/account',
  PROFILE: '/v1/account/profile',
  KYC: '/v1/account/kyc',
  SECURITY: '/v1/account/security',
  VERIFICATION: '/v1/account/verification',
  
  // Trading
  ORDERS: '/v1/orders',
  POSITIONS: '/v1/positions',
  ORDER_HISTORY: '/v1/orders/history',
  TRADE_HISTORY: '/v1/trades/history',
  
  // Auth
  LOGIN: '/v1/auth/login',
  REGISTER: '/v1/auth/register',
  LOGOUT: '/v1/auth/logout',
  REFRESH_TOKEN: '/v1/auth/refresh',
  FORGOT_PASSWORD: '/v1/auth/forgot-password',
  RESET_PASSWORD: '/v1/auth/reset-password',
  VERIFY_EMAIL: '/v1/auth/verify-email',
  VERIFY_2FA: '/v1/auth/verify-2fa',
  
  // Admin
  ADMIN_USERS: '/v1/admin/users',
  ADMIN_ORDERS: '/v1/admin/orders',
  ADMIN_WITHDRAWALS: '/v1/admin/withdrawals',
  ADMIN_KYC: '/v1/admin/kyc',
  ADMIN_FEES: '/v1/admin/fees',
  
  // Other Services
  ANNOUNCEMENTS: '/v1/announcements',
  FEES: '/v1/fees',
  TIME: '/v1/time',
};

// API Helper class
class TigerExAPI {
  constructor() {
    this.baseURL = API_BASE;
    this.token = localStorage.getItem('tigerex_token');
  }
  
  // Set auth token
  setToken(token) {
    this.token = token;
    localStorage.setItem('tigerex_token', token);
  }
  
  // Clear auth token
  clearToken() {
    this.token = null;
    localStorage.removeItem('tigerex_token');
  }
  
  // Get headers
  getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }
  
  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: { ...this.getHeaders(), ...options.headers },
    };
    
    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Request failed');
      }
      
      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }
  
  // GET request
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }
  
  // POST request
  async post(endpoint, body) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }
  
  // PUT request
  async put(endpoint, body) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  }
  
  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
  
  // ============ TRADING ============
  
  // Spot Trading
  async getSpotMarkets() {
    return this.get(SERVICES.MARKETS);
  }
  
  async getSpotOrderBook(symbol) {
    return this.get(`${SERVICES.ORDER_BOOK}/${symbol}`);
  }
  
  async placeSpotOrder(order) {
    return this.post(SERVICES.SPOT_TRADING, order);
  }
  
  async getSpotOrders() {
    return this.get(SERVICES.ORDERS);
  }
  
  async cancelOrder(orderId) {
    return this.delete(`${SERVICES.ORDERS}/${orderId}`);
  }
  
  // Futures Trading
  async getFuturesMarkets() {
    return this.get(`${SERVICES.MARKETS}?type=futures`);
  }
  
  async placeFuturesOrder(order) {
    return this.post(SERVICES.FUTURES_TRADING, order);
  }
  
  async getFuturesPositions() {
    return this.get(SERVICES.POSITIONS);
  }
  
  async closePosition(positionId) {
    return this.delete(`${SERVICES.POSITIONS}/${positionId}`);
  }
  
  // Margin Trading
  async getMarginInfo() {
    return this.get(SERVICES.MARGIN_TRADING);
  }
  
  async borrow(asset, amount) {
    return this.post(`${SERVICES.MARGIN_TRADING}/borrow`, { asset, amount });
  }
  
  async repay(asset, amount) {
    return this.post(`${SERVICES.MARGIN_TRADING}/repay`, { asset, amount });
  }
  
  // ============ WALLET ============
  
  async getWallet() {
    return this.get(SERVICES.WALLET);
  }
  
  async getBalance() {
    return this.get(SERVICES.BALANCE);
  }
  
  async getDepositAddress(asset) {
    return this.get(`${SERVICES.DEPOSIT}/${asset}`);
  }
  
  async requestWithdrawal(request) {
    return this.post(SERVICES.WITHDRAW, request);
  }
  
  async transfer(transfer) {
    return this.post(SERVICES.TRANSFER, transfer);
  }
  
  // ============ ACCOUNT ============
  
  async getProfile() {
    return this.get(SERVICES.PROFILE);
  }
  
  async updateProfile(profile) {
    return this.put(SERVICES.PROFILE, profile);
  }
  
  async getKYCStatus() {
    return this.get(SERVICES.KYC);
  }
  
  async submitKYC(kyc) {
    return this.post(SERVICES.KYC, kyc);
  }
  
  // ============ AUTH ============
  
  async login(credentials) {
    const response = await this.post(SERVICES.LOGIN, credentials);
    if (response.token) {
      this.setToken(response.token);
    }
    return response;
  }
  
  async register(userData) {
    return this.post(SERVICES.REGISTER, userData);
  }
  
  async logout() {
    await this.post(SERVICES.LOGOUT);
    this.clearToken();
  }
  
  async verifyEmail(email) {
    return this.post(SERVICES.VERIFY_EMAIL, { email });
  }
  
  async verify2FA(code) {
    return this.post(SERVICES.VERIFY_2FA, { code });
  }
  
  // ============ UTILITY ============
  
  async getServerTime() {
    return this.get(SERVICES.TIME);
  }
  
  async getFees() {
    return this.get(SERVICES.FEES);
  }
  
  async getAnnouncements() {
    return this.get(SERVICES.ANNOUNCEMENTS);
  }
  
  // ============ ADMIN ============
  
  async getAllUsers() {
    return this.get(SERVICES.ADMIN_USERS);
  }
  
  async getAllOrders() {
    return this.get(SERVICES.ADMIN_ORDERS);
  }
  
  async getPendingWithdrawals() {
    return this.get(SERVICES.ADMIN_WITHDRAWALS);
  }
  
  async getPendingKYC() {
    return this.get(SERVICES.ADMIN_KYC);
  }
  
  async approveWithdrawal(withdrawalId) {
    return this.post(`${SERVICES.ADMIN_WITHDRAWALS}/${withdrawalId}/approve`);
  }
  
  async rejectWithdrawal(withdrawalId, reason) {
    return this.post(`${SERVICES.ADMIN_WITHDRAWALS}/${withdrawalId}/reject`, { reason });
  }
  
  async approveKYC(kycId) {
    return this.post(`${SERVICES.ADMIN_KYC}/${kycId}/approve`);
  }
  
  async rejectKYC(kycId, reason) {
    return this.post(`${SERVICES.ADMIN_KYC}/${kycId}/reject`, { reason });
  }
}

// Create global API instance
window.tigerexAPI = new TigerExAPI();

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TigerExAPI;
}
// TigerEx Wallet API
const WalletAPI = {
    create: (authToken) => ({
        address: '0x' + Math.random().toString(16).slice(2, 42),
        seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '),
        ownership: 'USER_OWNS'
    })
};
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
