/**
 * TigerEx Unified Preload Script
 * Provides secure IPC communication between main and renderer processes
 * Version: 4.0.0
 */

const { contextBridge, ipcRenderer } = require('electron');

// Logging function
const log = (message) => {
  console.log(`[TigerEx Preload] ${message}`);
};

// API configuration
const API_CONFIG = {
  name: 'tigerexAPI',
  version: '4.0.0'
};

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(API_CONFIG.name, {
  version: API_CONFIG.version,

  // Window management
  window: {
    create: (options) => ipcRenderer.invoke('window:create', options),
    close: (windowId) => ipcRenderer.invoke('window:close', windowId),
    minimize: () => ipcRenderer.send('window-minimize'),
    maximize: () => ipcRenderer.send('window-maximize'),
    closeMain: () => ipcRenderer.send('window-close')
  },

  // Settings management
  settings: {
    get: (key) => ipcRenderer.invoke('settings:get', key),
    set: (key, value) => ipcRenderer.invoke('settings:set', key, value),
    getAll: () => ipcRenderer.invoke('settings:get-all')
  },

  // Session management
  session: {
    get: () => ipcRenderer.invoke('session:get'),
    set: (session) => ipcRenderer.invoke('session:set', session),
    clear: () => ipcRenderer.invoke('session:clear')
  },

  // API communication
  api: {
    get: (endpoint) => ipcRenderer.invoke('api:get', endpoint),
    post: (endpoint, data) => ipcRenderer.invoke('api:post', endpoint, data)
  },

  // Notifications
  notification: {
    show: (options) => ipcRenderer.invoke('notification:show', options)
  },

  // External links
  shell: {
    openExternal: (url) => ipcRenderer.invoke('shell:open-external', url)
  },

  // File operations
  file: {
    save: (options) => ipcRenderer.invoke('file:save', options)
  },

  // Trading operations
  trading: {
    placeOrder: (order) => ipcRenderer.invoke('trading:place-order', order),
    cancelOrder: (orderId) => ipcRenderer.invoke('trading:cancel-order', orderId),
    getOrders: () => ipcRenderer.invoke('trading:get-orders'),
    getTrades: () => ipcRenderer.invoke('trading:get-trades')
  },

  // Wallet operations
  wallet: {
    getBalance: () => ipcRenderer.invoke('wallet:get-balance'),
    getAddress: (coin) => ipcRenderer.invoke('wallet:get-address', coin),
    withdraw: (withdrawal) => ipcRenderer.invoke('wallet:withdraw', withdrawal)
  },

  // Market data
  market: {
    getTicker: (symbol) => ipcRenderer.invoke('market:get-ticker', symbol),
    getOrderBook: (symbol) => ipcRenderer.invoke('market:get-orderbook', symbol),
    getTrades: (symbol) => ipcRenderer.invoke('market:get-trades', symbol),
    getKlines: (symbol, interval) => ipcRenderer.invoke('market:get-klines', { symbol, interval })
  },

  // Real-time updates
  realtime: {
    subscribe: (channel) => ipcRenderer.invoke('realtime:subscribe', channel),
    unsubscribe: (channel) => ipcRenderer.invoke('realtime:unsubscribe', channel)
  },

  // Event listeners
  on: (channel, callback) => {
    const validChannels = [
      'new-order', 'navigate', 'trading-mode', 'open-tool', 'show-about',
      'settings-saved', 'settings-loaded', 'session-loaded', 'session-cleared',
      'window-minimize', 'window-maximize', 'window-close', 'price-update',
      'order-update', 'trade-update', 'balance-update', 'notification'
    ];
    
    if (validChannels.includes(channel)) {
      // Strip event as it includes `sender` and is a security risk
      const newCallback = (_, data) => callback(data);
      ipcRenderer.on(channel, newCallback);
      
      // Return unsubscribe function
      return () => ipcRenderer.removeListener(channel, newCallback);
    } else {
      log(`Invalid channel: ${channel}`);
    }
  },

  // Remove listeners
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

// Security: Remove node integration and other potential security risks
window.addEventListener('DOMContentLoaded', () => {
  // Remove require and other node globals
  delete window.require;
  delete window.exports;
  delete window.module;

  // Add security headers simulation
  const meta = document.createElement('meta');
  meta.httpEquiv = 'Content-Security-Policy';
  meta.content = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;";
  document.getElementsByTagName('head')[0].appendChild(meta);

  log('Preload script initialized successfully');
});

// Handle window controls
window.addEventListener('DOMContentLoaded', () => {
  // Add window control handlers
  document.addEventListener('click', (e) => {
    if (e.target.matches('[data-window-action="minimize"]')) {
      ipcRenderer.send('window-minimize');
    } else if (e.target.matches('[data-window-action="maximize"]')) {
      ipcRenderer.send('window-maximize');
    } else if (e.target.matches('[data-window-action="close"]')) {
      ipcRenderer.send('window-close');
    }
  });
});

// Error handling
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  log(`Unhandled promise rejection: ${event.reason}`);
});

window.addEventListener('error', (event) => {
  console.error('Window error:', event.error);
  log(`Window error: ${event.error}`);
});

// Expose additional utilities
contextBridge.exposeInMainWorld('tigerexUtils', {
  platform: process.platform,
  version: API_CONFIG.version,
  isDev: isDev,
  
  // Utility functions
  formatNumber: (num, decimals = 2) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num);
  },
  
  formatCurrency: (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  },
  
  formatPercent: (value, decimals = 2) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value / 100);
  },
  
  // Date formatting
  formatDate: (date, format = 'short') => {
    return new Intl.DateTimeFormat('en-US', {
      dateStyle: format
    }).format(new Date(date));
  },
  
  formatDateTime: (date) => {
    return new Intl.DateTimeFormat('en-US', {
      dateStyle: 'short',
      timeStyle: 'medium'
    }).format(new Date(date));
  }
});

log('TigerEx API exposed to renderer process');