/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getVersion: () => ipcRenderer.invoke('app-version'),
  
  // Dialog methods
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  
  // Menu event listeners
  onMenuNewOrder: (callback) => ipcRenderer.on('menu-new-order', callback),
  onMenuExportData: (callback) => ipcRenderer.on('menu-export-data', callback),
  onMenuSwitchCEX: (callback) => ipcRenderer.on('menu-switch-cex', callback),
  onMenuSwitchDEX: (callback) => ipcRenderer.on('menu-switch-dex', callback),
  onMenuMarketData: (callback) => ipcRenderer.on('menu-market-data', callback),
  onMenuOrderBook: (callback) => ipcRenderer.on('menu-order-book', callback),
  onMenuViewBalances: (callback) => ipcRenderer.on('menu-view-balances', callback),
  onMenuTransferFunds: (callback) => ipcRenderer.on('menu-transfer-funds', callback),
  onMenuTransactionHistory: (callback) => ipcRenderer.on('menu-transaction-history', callback),
  onMenuShowShortcuts: (callback) => ipcRenderer.on('menu-show-shortcuts', callback),
  
  // Remove listeners
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),
  
  // Platform info
  platform: process.platform,
  
  // Window controls
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close'),
  
  // Notifications
  showNotification: (title, body) => {
    if (Notification.permission === 'granted') {
      new Notification(title, { body });
    }
  },
  
  // File system (limited)
  selectFile: () => ipcRenderer.invoke('select-file'),
  saveFile: (data, filename) => ipcRenderer.invoke('save-file', data, filename),
  
  // Clipboard
  writeText: (text) => {
    navigator.clipboard.writeText(text);
  },
  
  // System info
  getSystemInfo: () => ({
    platform: process.platform,
    arch: process.arch,
    version: process.version
  })
});

// Security: Remove Node.js globals
delete window.require;
delete window.exports;
delete window.module;

// Add desktop-specific styles
window.addEventListener('DOMContentLoaded', () => {
  // Add desktop class to body
  document.body.classList.add('desktop-app');
  
  // Add platform-specific class
  document.body.classList.add(`platform-${process.platform}`);
  
  // Handle window controls for frameless windows
  if (process.platform === 'win32') {
    // Windows-specific styling
    document.body.classList.add('windows-controls');
  } else if (process.platform === 'darwin') {
    // macOS-specific styling
    document.body.classList.add('macos-controls');
  }
  
  // Add keyboard shortcuts info
  const shortcuts = {
    'Ctrl+N': 'New Order',
    'Ctrl+E': 'Export Data',
    'Ctrl+1': 'Switch to CEX',
    'Ctrl+2': 'Switch to DEX',
    'Ctrl+M': 'Market Data',
    'Ctrl+O': 'Order Book',
    'Ctrl+B': 'View Balances',
    'Ctrl+T': 'Transfer Funds',
    'Ctrl+H': 'Transaction History',
    'F11': 'Toggle Fullscreen',
    'Ctrl+R': 'Reload',
    'Ctrl+Shift+I': 'Developer Tools'
  };
  
  // Store shortcuts for later use
  window.keyboardShortcuts = shortcuts;
});

// Handle keyboard shortcuts
window.addEventListener('keydown', (event) => {
  // Handle custom shortcuts
  const key = event.key.toLowerCase();
  const ctrl = event.ctrlKey || event.metaKey;
  const shift = event.shiftKey;
  
  if (ctrl && key === 'n') {
    event.preventDefault();
    // Trigger new order
    window.dispatchEvent(new CustomEvent('desktop-new-order'));
  }
  
  if (ctrl && key === 'e') {
    event.preventDefault();
    // Trigger export
    window.dispatchEvent(new CustomEvent('desktop-export-data'));
  }
  
  if (ctrl && key === '1') {
    event.preventDefault();
    // Switch to CEX
    window.dispatchEvent(new CustomEvent('desktop-switch-cex'));
  }
  
  if (ctrl && key === '2') {
    event.preventDefault();
    // Switch to DEX
    window.dispatchEvent(new CustomEvent('desktop-switch-dex'));
  }
});

// Add desktop-specific utilities
window.desktopUtils = {
  // Show native notification
  showNotification: (title, message, options = {}) => {
    if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        return new Notification(title, {
          body: message,
          icon: '/assets/icon.png',
          ...options
        });
      } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            return new Notification(title, {
              body: message,
              icon: '/assets/icon.png',
              ...options
            });
          }
        });
      }
    }
  },
  
  // Copy to clipboard
  copyToClipboard: async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      return false;
    }
  },
  
  // Get system theme
  getSystemTheme: () => {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  },
  
  // Listen for theme changes
  onThemeChange: (callback) => {
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addListener(callback);
      return () => mediaQuery.removeListener(callback);
    }
    return () => {};
  },
  
  // Check if online
  isOnline: () => navigator.onLine,
  
  // Listen for online/offline events
  onConnectionChange: (callback) => {
    window.addEventListener('online', () => callback(true));
    window.addEventListener('offline', () => callback(false));
    
    return () => {
      window.removeEventListener('online', callback);
      window.removeEventListener('offline', callback);
    };
  }
};

// Performance monitoring
window.performance.mark('preload-end');

console.log('TigerEx Desktop preload script loaded successfully');