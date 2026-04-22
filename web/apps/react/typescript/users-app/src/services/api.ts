import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import { useAuthStore } from '../stores/authStore';
import { useAppStore } from '../stores/appStore';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.tigerex.com';

class ApiService {
  private client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  constructor() {
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      async (config) => {
        const token = useAuthStore.getState().accessToken;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        config.headers['X-Platform'] = 'web';
        config.headers['X-App-Version'] = '1.0.0';
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = useAuthStore.getState().refreshToken;
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
                refreshToken,
              });
              
              const { accessToken, refreshToken: newRefreshToken } = response.data;
              useAuthStore.getState().setTokens(accessToken, newRefreshToken);
              
              originalRequest.headers.Authorization = `Bearer ${accessToken}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            useAuthStore.getState().logout();
            window.location.href = '/login';
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  // ============ Authentication ============
  async login(email: string, password: string, twoFactorCode?: string) {
    const response = await this.client.post('/api/v1/auth/login', {
      email,
      password,
      twoFactorCode,
    });
    return response.data;
  }

  async register(data: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    referralCode?: string;
  }) {
    const response = await this.client.post('/api/v1/auth/register', data);
    return response.data;
  }

  async logout() {
    const response = await this.client.post('/api/v1/auth/logout');
    return response.data;
  }

  // ============ User Profile ============
  async getProfile() {
    const response = await this.client.get('/api/v1/user/profile');
    return response.data;
  }

  async updateProfile(data: {
    firstName?: string;
    lastName?: string;
    phone?: string;
  }) {
    const response = await this.client.put('/api/v1/user/profile', data);
    return response.data;
  }

  // ============ Trading ============
  async getTradingPairs() {
    const response = await this.client.get('/api/v1/trading/pairs');
    return response.data;
  }

  async getOrderBook(pair: string) {
    const response = await this.client.get(`/api/v1/trading/orderbook/${pair}`);
    return response.data;
  }

  async getKlines(pair: string, interval: string, limit: number = 100) {
    const response = await this.client.get(`/api/v1/trading/klines/${pair}`, {
      params: { interval, limit },
    });
    return response.data;
  }

  async createOrder(data: {
    pair: string;
    type: 'market' | 'limit' | 'stopLoss' | 'stopLimit';
    side: 'buy' | 'sell';
    price?: string;
    quantity: string;
  }) {
    const response = await this.client.post('/api/v1/trading/orders', data);
    return response.data;
  }

  async cancelOrder(orderId: string) {
    const response = await this.client.delete(`/api/v1/trading/orders/${orderId}`);
    return response.data;
  }

  async getOpenOrders(pair?: string) {
    const response = await this.client.get('/api/v1/trading/orders/open', {
      params: { pair },
    });
    return response.data;
  }

  async getOrderHistory(pair?: string, limit: number = 50) {
    const response = await this.client.get('/api/v1/trading/orders/history', {
      params: { pair, limit },
    });
    return response.data;
  }

  // ============ Wallet ============
  async getBalances() {
    const response = await this.client.get('/api/v1/wallet/balances');
    return response.data;
  }

  async getDeposits(asset?: string, limit: number = 50) {
    const response = await this.client.get('/api/v1/wallet/deposits', {
      params: { asset, limit },
    });
    return response.data;
  }

  async getWithdrawals(asset?: string, limit: number = 50) {
    const response = await this.client.get('/api/v1/wallet/withdrawals', {
      params: { asset, limit },
    });
    return response.data;
  }

  async createWithdrawal(data: {
    asset: string;
    amount: string;
    address: string;
    network?: string;
  }) {
    const response = await this.client.post('/api/v1/wallet/withdrawals', data);
    return response.data;
  }

  async convert(data: {
    fromAsset: string;
    toAsset: string;
    amount: string;
  }) {
    const response = await this.client.post('/api/v1/wallet/convert', data);
    return response.data;
  }

  // ============ P2P Trading ============
  async getP2PAds(type?: 'buy' | 'sell', asset?: string) {
    const response = await this.client.get('/api/v1/p2p/ads', {
      params: { type, asset },
    });
    return response.data;
  }

  async createP2PAd(data: {
    type: 'buy' | 'sell';
    asset: string;
    fiatCurrency: string;
    price: string;
    minAmount: string;
    maxAmount: string;
    paymentMethods: string[];
  }) {
    const response = await this.client.post('/api/v1/p2p/ads', data);
    return response.data;
  }

  async getP2PTrades() {
    const response = await this.client.get('/api/v1/p2p/trades');
    return response.data;
  }

  // ============ Earn Products ============
  async getStakingProducts() {
    const response = await this.client.get('/api/v1/earn/staking/products');
    return response.data;
  }

  async subscribeStaking(productId: string, amount: string) {
    const response = await this.client.post('/api/v1/earn/staking/subscribe', {
      productId,
      amount,
    });
    return response.data;
  }

  async getStakingPositions() {
    const response = await this.client.get('/api/v1/earn/staking/positions');
    return response.data;
  }

  async getLaunchpoolProjects() {
    const response = await this.client.get('/api/v1/earn/launchpool/projects');
    return response.data;
  }

  async subscribeLaunchpool(projectId: string, amount: string) {
    const response = await this.client.post('/api/v1/earn/launchpool/subscribe', {
      projectId,
      amount,
    });
    return response.data;
  }

  // ============ Security ============
  async enable2FA(method: 'totp' | 'sms') {
    const response = await this.client.post('/api/v1/security/2fa/enable', { method });
    return response.data;
  }

  async verify2FA(code: string) {
    const response = await this.client.post('/api/v1/security/2fa/verify', { code });
    return response.data;
  }

  async disable2FA(code: string) {
    const response = await this.client.post('/api/v1/security/2fa/disable', { code });
    return response.data;
  }

  async getApiKeys() {
    const response = await this.client.get('/api/v1/security/api-keys');
    return response.data;
  }

  async createApiKey(label: string, permissions: string[]) {
    const response = await this.client.post('/api/v1/security/api-keys', {
      label,
      permissions,
    });
    return response.data;
  }

  async deleteApiKey(keyId: string) {
    const response = await this.client.delete(`/api/v1/security/api-keys/${keyId}`);
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;