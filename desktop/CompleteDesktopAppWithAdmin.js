/**
 * TigerEx Complete Desktop Application with Full Admin Control
 * Comprehensive desktop trading platform with all features and admin functionality
 * Electron - Windows, macOS, Linux Support
 */

const { app, BrowserWindow, Menu, ipcMain, dialog, shell, globalShortcut, Tray, nativeImage } = require('electron');
const path = require('path');
const fs = require('fs').promises;
const crypto = require('crypto');
const os = require('os');
const { autoUpdater } = require('electron-updater');
const { exec } = require('child_process');
const { networkInterfaces } = require('os');
const https = require('https');
const http = require('http');
const WebSocket = require('ws');
const sqlite3 = require('sqlite3').verbose();
const keytar = require('keytar');
const { app: expressApp, server } = require('express');
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
const compression = require('compression');
const { createProxyMiddleware } = require('http-proxy-middleware');

// Configuration Constants
const APP_CONFIG = {
  name: 'TigerEx Desktop',
  version: '4.0.0',
  description: 'Complete Cryptocurrency Exchange Desktop Application',
  author: 'TigerEx Team',
  homepage: 'https://tigerex.com',
  repository: 'https://github.com/meghlabd275-byte/TigerEx-',
  
  // Window Configuration
  window: {
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    show: false,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
      webSecurity: true,
      allowRunningInsecureContent: false,
      experimentalFeatures: true,
      spellcheck: true,
    },
  },
  
  // Security Configuration
  security: {
    allowEvaluatingJavaScript: true,
    allowRunningInsecureContent: false,
    experimentalFeatures: true,
    webSecurity: true,
    nodeIntegration: true,
    contextIsolation: false,
    enableRemoteModule: true,
  },
  
  // Update Configuration
  update: {
    autoDownload: true,
    autoInstallOnAppQuit: true,
    updateCheckInterval: 1000 * 60 * 60, // 1 hour
    notifyUser: true,
  },
  
  // API Configuration
  api: {
    baseUrl: 'https://api.tigerex.com',
    wsUrl: 'wss://ws.tigerex.com',
    timeout: 30000,
    retries: 3,
  },
  
  // Database Configuration
  database: {
    name: 'tigerex-desktop.db',
    path: path.join(app.getPath('userData'), 'databases'),
  },
  
  // Storage Configuration
  storage: {
    config: path.join(app.getPath('userData'), 'config'),
    cache: path.join(app.getPath('userData'), 'cache'),
    logs: path.join(app.getPath('userData'), 'logs'),
    temp: path.join(app.getPath('userData'), 'temp'),
  },
  
  // Performance Configuration
  performance: {
    maxCacheSize: 100 * 1024 * 1024, // 100MB
    maxLogSize: 10 * 1024 * 1024, // 10MB
    cleanupInterval: 1000 * 60 * 60, // 1 hour
  },
};

// Global Variables
let mainWindow = null;
let adminWindow = null;
let settingsWindow = null;
let tray = null;
let isQuitting = false;
let isOnline = false;
let userData = null;
let tradingData = [];
let notifications = [];
let systemMetrics = {};
let database = null;
let wsConnection = null;
let securityManager = null;
let performanceMonitor = null;
let updateManager = null;
let apiClient = null;
let cacheManager = null;
let logManager = null;
let themeManager = null;
let notificationManager = null;
let shortcutManager = null;
let encryptionManager = null;
let backupManager = null;
let pluginManager = null;
let analyticsManager = null;

// Security Manager Class
class SecurityManager {
  constructor() {
    this.encryptionKey = null;
    this.sessionToken = null;
    this.userPermissions = [];
    this.auditLog = [];
  }

  async initialize() {
    // Generate or load encryption key
    await this.loadEncryptionKey();
    
    // Initialize secure storage
    await this.initializeSecureStorage();
    
    // Setup security policies
    this.setupSecurityPolicies();
  }

  async loadEncryptionKey() {
    try {
      const key = await keytar.getPassword('tigerex-desktop', 'encryption-key');
      if (!key) {
        this.encryptionKey = crypto.randomBytes(32).toString('hex');
        await keytar.setPassword('tigerex-desktop', 'encryption-key', this.encryptionKey);
      } else {
        this.encryptionKey = key;
      }
    } catch (error) {
      console.error('Error loading encryption key:', error);
      this.encryptionKey = crypto.randomBytes(32).toString('hex');
    }
  }

  async initializeSecureStorage() {
    // Initialize secure storage for sensitive data
    this.secureStorage = {
      apiKey: await keytar.getPassword('tigerex-desktop', 'api-key'),
      apiSecret: await keytar.getPassword('tigerex-desktop', 'api-secret'),
      sessionToken: await keytar.getPassword('tigerex-desktop', 'session-token'),
    };
  }

  setupSecurityPolicies() {
    // Setup content security policy
    this.csp = {
      'default-src': ["'self'"],
      'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
      'style-src': ["'self'", "'unsafe-inline'"],
      'img-src': ["'self'", 'data:', 'https:'],
      'connect-src': ["'self'", 'https://api.tigerex.com', 'wss://ws.tigerex.com'],
      'font-src': ["'self'", 'data:'],
      'object-src': ["'none'"],
      'media-src': ["'self'"],
      'frame-src': ["'none'"],
    };
  }

  encrypt(data) {
    const algorithm = 'aes-256-gcm';
    const key = Buffer.from(this.encryptionKey, 'hex');
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher(algorithm, key, iv);
    
    let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
      encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex'),
    };
  }

  decrypt(encryptedData) {
    const algorithm = 'aes-256-gcm';
    const key = Buffer.from(this.encryptionKey, 'hex');
    const iv = Buffer.from(encryptedData.iv, 'hex');
    const authTag = Buffer.from(encryptedData.authTag, 'hex');
    
    const decipher = crypto.createDecipher(algorithm, key, iv);
    decipher.setAuthTag(authTag);
    
    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return JSON.parse(decrypted);
  }

  async logSecurityEvent(event) {
    const auditEntry = {
      timestamp: new Date().toISOString(),
      event: event.type,
      details: event.details,
      userId: userData?.id,
      sessionId: this.sessionToken,
    };
    
    this.auditLog.push(auditEntry);
    
    // Save to database
    try {
      await database.run('INSERT INTO audit_log (timestamp, event, details, user_id, session_id) VALUES (?, ?, ?, ?, ?)', [
        auditEntry.timestamp,
        auditEntry.event,
        JSON.stringify(auditEntry.details),
        auditEntry.userId,
        auditEntry.sessionId,
      ]);
    } catch (error) {
      console.error('Error logging security event:', error);
    }
  }
}

// Performance Monitor Class
class PerformanceMonitor {
  constructor() {
    this.metrics = {
      cpu: 0,
      memory: 0,
      disk: 0,
      network: 0,
      appStartup: 0,
      appRuntime: 0,
      renderTime: 0,
      apiResponseTime: 0,
    };
    this.startTime = Date.now();
    this.monitoringInterval = null;
  }

  start() {
    this.startTime = Date.now();
    this.monitoringInterval = setInterval(() => {
      this.collectMetrics();
    }, 5000); // Collect every 5 seconds
  }

  stop() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }

  collectMetrics() {
    // CPU Usage
    this.metrics.cpu = process.cpuUsage().user / 1000000;
    
    // Memory Usage
    const memoryUsage = process.memoryUsage();
    this.metrics.memory = memoryUsage.heapUsed / 1024 / 1024; // MB
    
    // App Runtime
    this.metrics.appRuntime = (Date.now() - this.startTime) / 1000; // seconds
    
    // System metrics
    this.collectSystemMetrics();
  }

  collectSystemMetrics() {
    // Get system CPU usage
    exec('wmic cpu get loadpercentage /value', (error, stdout) => {
      if (!error) {
        const match = stdout.match(/LoadPercentage=(\d+)/);
        if (match) {
          this.metrics.cpu = parseInt(match[1]);
        }
      }
    });

    // Get system memory usage
    exec('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value', (error, stdout) => {
      if (!error) {
        const totalMatch = stdout.match(/TotalVisibleMemorySize=(\d+)/);
        const freeMatch = stdout.match(/FreePhysicalMemory=(\d+)/);
        if (totalMatch && freeMatch) {
          const total = parseInt(totalMatch[1]);
          const free = parseInt(freeMatch[1]);
          this.metrics.memory = ((total - free) / total) * 100;
        }
      }
    });
  }

  getMetrics() {
    return {
      ...this.metrics,
      timestamp: new Date().toISOString(),
    };
  }
}

// API Client Class
class APIClient {
  constructor() {
    this.baseUrl = APP_CONFIG.api.baseUrl;
    this.wsUrl = APP_CONFIG.api.wsUrl;
    this.timeout = APP_CONFIG.api.timeout;
    this.retries = APP_CONFIG.api.retries;
    this.sessionToken = null;
  }

  async request(method, endpoint, data = null, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'User-Agent': `TigerEx-Desktop/${APP_CONFIG.version}`,
      ...(this.sessionToken && { 'Authorization': `Bearer ${this.sessionToken}` }),
      ...options.headers,
    };

    try {
      const response = await this.makeRequest(method, url, headers, data, options);
      return response;
    } catch (error) {
      console.error(`API request failed: ${method} ${endpoint}`, error);
      throw error;
    }
  }

  async makeRequest(method, url, headers, data, options) {
    const requestOptions = {
      method,
      headers,
      timeout: this.timeout,
      ...options,
    };

    if (data && method !== 'GET') {
      requestOptions.body = JSON.stringify(data);
    }

    const protocol = url.startsWith('https') ? https : http;
    
    return new Promise((resolve, reject) => {
      const req = protocol.request(url, requestOptions, (res) => {
        let body = '';
        
        res.on('data', (chunk) => {
          body += chunk;
        });
        
        res.on('end', () => {
          try {
            const response = JSON.parse(body);
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(response);
            } else {
              reject(new Error(`HTTP ${res.statusCode}: ${response.message || 'Unknown error'}`));
            }
          } catch (error) {
            reject(new Error(`Invalid response: ${error.message}`));
          }
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });

      req.end();
    });
  }

  async get(endpoint, params = null) {
    const url = params ? `${endpoint}?${new URLSearchParams(params)}` : endpoint;
    return this.request('GET', url);
  }

  async post(endpoint, data = null) {
    return this.request('POST', endpoint, data);
  }

  async put(endpoint, data = null) {
    return this.request('PUT', endpoint, data);
  }

  async delete(endpoint, data = null) {
    return this.request('DELETE', endpoint, data);
  }

  connectWebSocket() {
    if (this.wsConnection) {
      this.wsConnection.close();
    }

    this.wsConnection = new WebSocket(`${this.wsUrl}?token=${this.sessionToken}`);
    
    this.wsConnection.onopen = () => {
      console.log('WebSocket connected');
      this.onWebSocketConnected();
    };
    
    this.wsConnection.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.onWebSocketMessage(data);
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };
    
    this.wsConnection.onclose = () => {
      console.log('WebSocket disconnected');
      this.onWebSocketDisconnected();
    };
    
    this.wsConnection.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.onWebSocketError(error);
    };
  }

  onWebSocketConnected() {
    // Send initial subscription requests
    this.wsConnection.send(JSON.stringify({
      type: 'subscribe',
      channels: ['prices', 'orders', 'notifications'],
    }));
  }

  onWebSocketMessage(data) {
    // Handle WebSocket messages
    switch (data.type) {
      case 'price_update':
        this.handlePriceUpdate(data);
        break;
      case 'order_update':
        this.handleOrderUpdate(data);
        break;
      case 'notification':
        this.handleNotification(data);
        break;
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }

  handlePriceUpdate(data) {
    // Update trading data
    tradingData = tradingData.map(item => 
      item.symbol === data.symbol ? { ...item, ...data } : item
    );
    
    // Send to renderer process
    if (mainWindow) {
      mainWindow.webContents.send('price-update', data);
    }
  }

  handleOrderUpdate(data) {
    // Update orders
    // Send to renderer process
    if (mainWindow) {
      mainWindow.webContents.send('order-update', data);
    }
  }

  handleNotification(data) {
    // Add to notifications
    notifications.unshift(data);
    
    // Send to renderer process
    if (mainWindow) {
      mainWindow.webContents.send('notification', data);
    }
    
    // Show system notification
    this.showSystemNotification(data);
  }

  showSystemNotification(data) {
    const notification = new Notification(data.title, {
      body: data.message,
      icon: path.join(__dirname, 'assets', 'icon.png'),
    });
    
    notification.onclick = () => {
      // Focus main window
      if (mainWindow) {
        mainWindow.focus();
      }
    };
  }

  onWebSocketDisconnected() {
    // Attempt to reconnect after 5 seconds
    setTimeout(() => {
      this.connectWebSocket();
    }, 5000);
  }

  onWebSocketError(error) {
    console.error('WebSocket error:', error);
  }

  setSessionToken(token) {
    this.sessionToken = token;
    this.connectWebSocket();
  }
}

// Cache Manager Class
class CacheManager {
  constructor() {
    this.cache = new Map();
    this.maxSize = APP_CONFIG.performance.maxCacheSize;
    this.currentSize = 0;
  }

  async get(key) {
    const item = this.cache.get(key);
    if (item && !this.isExpired(item)) {
      return item.value;
    }
    return null;
  }

  async set(key, value, ttl = 3600000) { // 1 hour default
    const size = this.calculateSize(value);
    
    // Check if cache is full
    if (this.currentSize + size > this.maxSize) {
      await this.evictOldest();
    }
    
    const item = {
      key,
      value,
      timestamp: Date.now(),
      ttl,
      size,
    };
    
    this.cache.set(key, item);
    this.currentSize += size;
  }

  async delete(key) {
    const item = this.cache.get(key);
    if (item) {
      this.cache.delete(key);
      this.currentSize -= item.size;
    }
  }

  async clear() {
    this.cache.clear();
    this.currentSize = 0;
  }

  isExpired(item) {
    return Date.now() - item.timestamp > item.ttl;
  }

  calculateSize(value) {
    return JSON.stringify(value).length * 2; // Rough estimate
  }

  async evictOldest() {
    let oldestKey = null;
    let oldestTimestamp = Date.now();
    
    for (const [key, item] of this.cache) {
      if (item.timestamp < oldestTimestamp) {
        oldestTimestamp = item.timestamp;
        oldestKey = key;
      }
    }
    
    if (oldestKey) {
      await this.delete(oldestKey);
    }
  }

  async cleanup() {
    for (const [key, item] of this.cache) {
      if (this.isExpired(item)) {
        await this.delete(key);
      }
    }
  }

  getStats() {
    return {
      size: this.cache.size,
      currentSize: this.currentSize,
      maxSize: this.maxSize,
      usage: (this.currentSize / this.maxSize) * 100,
    };
  }
}

// Plugin Manager Class
class PluginManager {
  constructor() {
    this.plugins = new Map();
    this.pluginDir = path.join(app.getPath('userData'), 'plugins');
  }

  async initialize() {
    await this.ensurePluginDirectory();
    await this.loadPlugins();
  }

  async ensurePluginDirectory() {
    try {
      await fs.mkdir(this.pluginDir, { recursive: true });
    } catch (error) {
      console.error('Error creating plugin directory:', error);
    }
  }

  async loadPlugins() {
    try {
      const files = await fs.readdir(this.pluginDir);
      const pluginFiles = files.filter(file => file.endsWith('.js'));
      
      for (const file of pluginFiles) {
        await this.loadPlugin(path.join(this.pluginDir, file));
      }
    } catch (error) {
      console.error('Error loading plugins:', error);
    }
  }

  async loadPlugin(filePath) {
    try {
      delete require.cache[require.resolve(filePath)];
      const plugin = require(filePath);
      
      if (this.validatePlugin(plugin)) {
        plugin.initialize();
        this.plugins.set(plugin.name, plugin);
        console.log(`Plugin loaded: ${plugin.name}`);
      } else {
        console.error(`Invalid plugin: ${filePath}`);
      }
    } catch (error) {
      console.error(`Error loading plugin ${filePath}:`, error);
    }
  }

  validatePlugin(plugin) {
    return plugin && 
           typeof plugin.name === 'string' &&
           typeof plugin.version === 'string' &&
           typeof plugin.initialize === 'function';
  }

  async unloadPlugin(pluginName) {
    const plugin = this.plugins.get(pluginName);
    if (plugin && typeof plugin.destroy === 'function') {
      await plugin.destroy();
    }
    this.plugins.delete(pluginName);
  }

  async installPlugin(pluginPath) {
    try {
      const pluginFiles = await fs.readdir(pluginPath);
      const mainFile = pluginFiles.find(file => file === 'index.js' || file === 'main.js');
      
      if (mainFile) {
        const targetPath = path.join(this.pluginDir, path.basename(pluginPath));
        await this.copyDirectory(pluginPath, targetPath);
        await this.loadPlugin(path.join(targetPath, mainFile));
        return true;
      }
    } catch (error) {
      console.error('Error installing plugin:', error);
    }
    return false;
  }

  async copyDirectory(src, dest) {
    await fs.mkdir(dest, { recursive: true });
    const entries = await fs.readdir(src, { withFileTypes: true });
    
    for (const entry of entries) {
      const srcPath = path.join(src, entry.name);
      const destPath = path.join(dest, entry.name);
      
      if (entry.isDirectory()) {
        await this.copyDirectory(srcPath, destPath);
      } else {
        await fs.copyFile(srcPath, destPath);
      }
    }
  }

  getPlugins() {
    return Array.from(this.plugins.values());
  }

  getPlugin(name) {
    return this.plugins.get(name);
  }
}

// Application Initialization
async function initializeApp() {
  try {
    console.log('Initializing TigerEx Desktop Application...');
    
    // Initialize security manager
    securityManager = new SecurityManager();
    await securityManager.initialize();
    
    // Initialize performance monitor
    performanceMonitor = new PerformanceMonitor();
    performanceMonitor.start();
    
    // Initialize API client
    apiClient = new APIClient();
    
    // Initialize cache manager
    cacheManager = new CacheManager();
    
    // Initialize database
    await initializeDatabase();
    
    // Initialize plugin manager
    pluginManager = new PluginManager();
    await pluginManager.initialize();
    
    // Setup auto updater
    setupAutoUpdater();
    
    // Setup IPC handlers
    setupIPCHandlers();
    
    // Setup global shortcuts
    setupGlobalShortcuts();
    
    // Setup system tray
    setupSystemTray();
    
    // Setup menu
    setupMenu();
    
    // Create main window
    await createMainWindow();
    
    // Setup update checker
    setupUpdateChecker();
    
    console.log('Application initialized successfully');
  } catch (error) {
    console.error('Error initializing application:', error);
    app.quit();
  }
}

// Database Initialization
async function initializeDatabase() {
  try {
    await fs.mkdir(APP_CONFIG.database.path, { recursive: true });
    
    const dbPath = path.join(APP_CONFIG.database.path, APP_CONFIG.database.name);
    database = new sqlite3.Database(dbPath);
    
    // Create tables
    await createDatabaseTables();
    
    console.log('Database initialized successfully');
  } catch (error) {
    console.error('Error initializing database:', error);
    throw error;
  }
}

// Create Database Tables
function createDatabaseTables() {
  return new Promise((resolve, reject) => {
    database.serialize(() => {
      // Users table
      database.run(`
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT UNIQUE NOT NULL,
          username TEXT UNIQUE NOT NULL,
          password TEXT NOT NULL,
          role TEXT DEFAULT 'user',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);
      
      // Trading orders table
      database.run(`
        CREATE TABLE IF NOT EXISTS trading_orders (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          symbol TEXT NOT NULL,
          type TEXT NOT NULL,
          side TEXT NOT NULL,
          quantity REAL NOT NULL,
          price REAL,
          status TEXT DEFAULT 'pending',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users (id)
        )
      `);
      
      // Portfolio table
      database.run(`
        CREATE TABLE IF NOT EXISTS portfolio (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          asset TEXT NOT NULL,
          balance REAL DEFAULT 0,
          value REAL DEFAULT 0,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users (id)
        )
      `);
      
      // Settings table
      database.run(`
        CREATE TABLE IF NOT EXISTS settings (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          key TEXT NOT NULL,
          value TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users (id)
        )
      `);
      
      // Audit log table
      database.run(`
        CREATE TABLE IF NOT EXISTS audit_log (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
          event TEXT NOT NULL,
          details TEXT,
          user_id INTEGER,
          session_id TEXT,
          FOREIGN KEY (user_id) REFERENCES users (id)
        )
      `);
      
      // Performance metrics table
      database.run(`
        CREATE TABLE IF NOT EXISTS performance_metrics (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
          cpu_usage REAL,
          memory_usage REAL,
          disk_usage REAL,
          network_usage REAL,
          app_runtime REAL,
          render_time REAL
        )
      `, (error) => {
        if (error) {
          reject(error);
        } else {
          resolve();
        }
      });
    });
  });
}

// Create Main Window
async function createMainWindow() {
  mainWindow = new BrowserWindow({
    ...APP_CONFIG.window,
    icon: path.join(__dirname, 'assets', 'icon.png'),
    title: APP_CONFIG.name,
  });

  // Load the app
  const isDev = process.env.NODE_ENV === 'development';
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'build', 'index.html'));
  }

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle window focus
  mainWindow.on('focus', () => {
    // Update performance metrics
    if (performanceMonitor) {
      const metrics = performanceMonitor.getMetrics();
      mainWindow.webContents.send('performance-metrics', metrics);
    }
  });

  // Handle navigation
  mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);
    
    // Allow internal navigation only
    if (parsedUrl.origin !== 'http://localhost:3000' && !isDev) {
      event.preventDefault();
      shell.openExternal(navigationUrl);
    }
  });

  // Handle new window
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Focus window
    if (process.platform === 'darwin') {
      app.focus();
    }
  });

  console.log('Main window created successfully');
}

// Create Admin Window
function createAdminWindow() {
  if (adminWindow) {
    adminWindow.focus();
    return;
  }

  adminWindow = new BrowserWindow({
    ...APP_CONFIG.window,
    width: 1600,
    height: 1000,
    title: `${APP_CONFIG.name} - Admin Panel`,
    parent: mainWindow,
    modal: false,
  });

  // Load admin panel
  const isDev = process.env.NODE_ENV === 'development';
  if (isDev) {
    adminWindow.loadURL('http://localhost:3001/admin');
    adminWindow.webContents.openDevTools();
  } else {
    adminWindow.loadFile(path.join(__dirname, 'build', 'admin.html'));
  }

  // Handle window closed
  adminWindow.on('closed', () => {
    adminWindow = null;
  });

  console.log('Admin window created successfully');
}

// Setup Auto Updater
function setupAutoUpdater() {
  autoUpdater.checkForUpdatesAndNotify();
  
  autoUpdater.on('update-available', (info) => {
    console.log('Update available:', info);
    if (mainWindow) {
      mainWindow.webContents.send('update-available', info);
    }
  });
  
  autoUpdater.on('update-downloaded', (info) => {
    console.log('Update downloaded:', info);
    if (mainWindow) {
      mainWindow.webContents.send('update-downloaded', info);
    }
  });
  
  autoUpdater.on('error', (error) => {
    console.error('Update error:', error);
  });
}

// Setup IPC Handlers
function setupIPCHandlers() {
  // App info
  ipcMain.handle('app-info', () => {
    return {
      name: APP_CONFIG.name,
      version: APP_CONFIG.version,
      platform: process.platform,
      arch: process.arch,
    };
  });

  // User authentication
  ipcMain.handle('login', async (event, credentials) => {
    try {
      const response = await apiClient.post('/auth/login', credentials);
      if (response.success) {
        userData = response.user;
        apiClient.setSessionToken(response.token);
        await securityManager.logSecurityEvent({
          type: 'login',
          details: { userId: userData.id },
        });
        return response;
      }
      throw new Error(response.message);
    } catch (error) {
      await securityManager.logSecurityEvent({
        type: 'login_failed',
        details: { error: error.message },
      });
      throw error;
    }
  });

  // User logout
  ipcMain.handle('logout', async () => {
    try {
      await securityManager.logSecurityEvent({
        type: 'logout',
        details: { userId: userData?.id },
      });
      userData = null;
      apiClient.setSessionToken(null);
      return { success: true };
    } catch (error) {
      throw error;
    }
  });

  // Trading data
  ipcMain.handle('get-trading-data', async () => {
    try {
      const cached = await cacheManager.get('trading-data');
      if (cached) {
        return cached;
      }
      
      const response = await apiClient.get('/trading/data');
      await cacheManager.set('trading-data', response.data, 30000); // 30 seconds
      return response.data;
    } catch (error) {
      throw error;
    }
  });

  // Place order
  ipcMain.handle('place-order', async (event, orderData) => {
    try {
      const response = await apiClient.post('/trading/orders', orderData);
      await securityManager.logSecurityEvent({
        type: 'order_placed',
        details: orderData,
      });
      return response;
    } catch (error) {
      await securityManager.logSecurityEvent({
        type: 'order_failed',
        details: { error: error.message, orderData },
      });
      throw error;
    }
  });

  // Get portfolio
  ipcMain.handle('get-portfolio', async () => {
    try {
      const response = await apiClient.get('/portfolio');
      return response.data;
    } catch (error) {
      throw error;
    }
  });

  // System metrics
  ipcMain.handle('get-system-metrics', async () => {
    return performanceMonitor ? performanceMonitor.getMetrics() : {};
  });

  // Cache operations
  ipcMain.handle('cache-get', async (event, key) => {
    return await cacheManager.get(key);
  });

  ipcMain.handle('cache-set', async (event, key, value, ttl) => {
    return await cacheManager.set(key, value, ttl);
  });

  ipcMain.handle('cache-delete', async (event, key) => {
    return await cacheManager.delete(key);
  });

  ipcMain.handle('cache-clear', async () => {
    return await cacheManager.clear();
  });

  // Plugin operations
  ipcMain.handle('get-plugins', () => {
    return pluginManager.getPlugins();
  });

  ipcMain.handle('install-plugin', async (event, pluginPath) => {
    return await pluginManager.installPlugin(pluginPath);
  });

  ipcMain.handle('uninstall-plugin', async (event, pluginName) => {
    await pluginManager.unloadPlugin(pluginName);
    return { success: true };
  });

  // Admin operations
  ipcMain.handle('open-admin-panel', () => {
    createAdminWindow();
  });

  ipcMain.handle('get-users', async () => {
    try {
      const response = await apiClient.get('/admin/users');
      return response.data;
    } catch (error) {
      throw error;
    }
  });

  ipcMain.handle('get-orders', async () => {
    try {
      const response = await apiClient.get('/admin/orders');
      return response.data;
    } catch (error) {
      throw error;
    }
  });

  ipcMain.handle('get-system-health', async () => {
    try {
      const response = await apiClient.get('/admin/system/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  });

  // Settings
  ipcMain.handle('get-settings', async () => {
    try {
      const response = await apiClient.get('/settings');
      return response.data;
    } catch (error) {
      throw error;
    }
  });

  ipcMain.handle('update-settings', async (event, settings) => {
    try {
      const response = await apiClient.put('/settings', settings);
      return response;
    } catch (error) {
      throw error;
    }
  });

  // Security
  ipcMain.handle('encrypt-data', async (event, data) => {
    return securityManager.encrypt(data);
  });

  ipcMain.handle('decrypt-data', async (event, encryptedData) => {
    return securityManager.decrypt(encryptedData);
  });
}

// Setup Global Shortcuts
function setupGlobalShortcuts() {
  // Quick trade window
  globalShortcut.register('CommandOrControl+Shift+T', () => {
    createQuickTradeWindow();
  });

  // Admin panel
  globalShortcut.register('CommandOrControl+Shift+A', () => {
    createAdminWindow();
  });

  // Settings
  globalShortcut.register('CommandOrControl+Shift+S', () => {
    createSettingsWindow();
  });

  // Lock app
  globalShortcut.register('CommandOrControl+Shift+L', () => {
    lockApp();
  });

  console.log('Global shortcuts registered');
}

// Setup System Tray
function setupSystemTray() {
  const iconPath = path.join(__dirname, 'assets', 'tray-icon.png');
  const trayIcon = nativeImage.createFromPath(iconPath);
  
  tray = new Tray(trayIcon);
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show TigerEx',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        } else {
          createMainWindow();
        }
      },
    },
    {
      label: 'Quick Trade',
      click: () => {
        createQuickTradeWindow();
      },
    },
    {
      label: 'Admin Panel',
      click: () => {
        createAdminWindow();
      },
    },
    { type: 'separator' },
    {
      label: 'Settings',
      click: () => {
        createSettingsWindow();
      },
    },
    {
      label: 'About',
      click: () => {
        dialog.showMessageBox({
          type: 'info',
          title: 'About TigerEx',
          message: APP_CONFIG.name,
          detail: `Version: ${APP_CONFIG.version}\n${APP_CONFIG.description}`,
        });
      },
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.quit();
      },
    },
  ]);
  
  tray.setToolTip(APP_CONFIG.name);
  tray.setContextMenu(contextMenu);
  
  // Double click to show main window
  tray.on('double-click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    } else {
      createMainWindow();
    }
  });

  console.log('System tray setup completed');
}

// Setup Menu
function setupMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Trade',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            createQuickTradeWindow();
          },
        },
        {
          label: 'Import Data',
          click: async () => {
            const result = await dialog.showOpenDialog({
              properties: ['openFile'],
              filters: [
                { name: 'CSV Files', extensions: ['csv'] },
                { name: 'JSON Files', extensions: ['json'] },
              ],
            });
            
            if (!result.canceled) {
              importData(result.filePaths[0]);
            }
          },
        },
        {
          label: 'Export Data',
          click: async () => {
            const result = await dialog.showSaveDialog({
              filters: [
                { name: 'CSV Files', extensions: ['csv'] },
                { name: 'JSON Files', extensions: ['json'] },
              ],
            });
            
            if (!result.canceled) {
              exportData(result.filePath);
            }
          },
        },
        { type: 'separator' },
        {
          label: 'Quit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          },
        },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        { label: 'Undo', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
        { label: 'Redo', accelerator: 'Shift+CmdOrCtrl+Z', role: 'redo' },
        { type: 'separator' },
        { label: 'Cut', accelerator: 'CmdOrCtrl+X', role: 'cut' },
        { label: 'Copy', accelerator: 'CmdOrCtrl+C', role: 'copy' },
        { label: 'Paste', accelerator: 'CmdOrCtrl+V', role: 'paste' },
        { label: 'Select All', accelerator: 'CmdOrCtrl+A', role: 'selectAll' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { label: 'Reload', accelerator: 'CmdOrCtrl+R', role: 'reload' },
        { label: 'Force Reload', accelerator: 'CmdOrCtrl+Shift+R', role: 'forceReload' },
        { label: 'Toggle Developer Tools', accelerator: process.platform === 'darwin' ? 'Alt+Cmd+I' : 'Ctrl+Shift+I', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: 'Actual Size', accelerator: 'CmdOrCtrl+0', role: 'resetZoom' },
        { label: 'Zoom In', accelerator: 'CmdOrCtrl+Plus', role: 'zoomIn' },
        { label: 'Zoom Out', accelerator: 'CmdOrCtrl+-', role: 'zoomOut' },
        { type: 'separator' },
        { label: 'Toggle Fullscreen', accelerator: process.platform === 'darwin' ? 'Ctrl+Cmd+F' : 'F11', role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Trading',
      submenu: [
        {
          label: 'Quick Trade',
          accelerator: 'CmdOrCtrl+Shift+T',
          click: () => {
            createQuickTradeWindow();
          },
        },
        {
          label: 'Advanced Trading',
          click: () => {
            createAdvancedTradingWindow();
          },
        },
        {
          label: 'Portfolio Analysis',
          click: () => {
            createPortfolioWindow();
          },
        },
      ],
    },
    {
      label: 'Admin',
      submenu: [
        {
          label: 'Admin Panel',
          accelerator: 'CmdOrCtrl+Shift+A',
          click: () => {
            createAdminWindow();
          },
        },
        {
          label: 'User Management',
          click: () => {
            createUserManagementWindow();
          },
        },
        {
          label: 'System Monitor',
          click: () => {
            createSystemMonitorWindow();
          },
        },
        {
          label: 'Security Settings',
          click: () => {
            createSecurityWindow();
          },
        },
      ],
    },
    {
      label: 'Window',
      submenu: [
        { label: 'Minimize', accelerator: 'CmdOrCtrl+M', role: 'minimize' },
        { label: 'Close', accelerator: 'CmdOrCtrl+W', role: 'close' },
      ],
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: () => {
            shell.openExternal('https://docs.tigerex.com');
          },
        },
        {
          label: 'Support',
          click: () => {
            shell.openExternal('https://support.tigerex.com');
          },
        },
        {
          label: 'Check for Updates',
          click: () => {
            autoUpdater.checkForUpdatesAndNotify();
          },
        },
        { type: 'separator' },
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox({
              type: 'info',
              title: 'About TigerEx',
              message: APP_CONFIG.name,
              detail: `Version: ${APP_CONFIG.version}\n${APP_CONFIG.description}`,
            });
          },
        },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
  
  console.log('Application menu setup completed');
}

// Setup Update Checker
function setupUpdateChecker() {
  setInterval(() => {
    autoUpdater.checkForUpdatesAndNotify();
  }, APP_CONFIG.update.updateCheckInterval);
}

// Utility Functions
function createQuickTradeWindow() {
  const quickTradeWindow = new BrowserWindow({
    width: 400,
    height: 600,
    parent: mainWindow,
    modal: false,
    alwaysOnTop: true,
    frame: false,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  quickTradeWindow.loadFile(path.join(__dirname, 'quick-trade.html'));
  
  quickTradeWindow.on('blur', () => {
    quickTradeWindow.close();
  });
}

function createAdvancedTradingWindow() {
  const advancedWindow = new BrowserWindow({
    width: 1800,
    height: 1000,
    title: 'Advanced Trading',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  advancedWindow.loadFile(path.join(__dirname, 'advanced-trading.html'));
}

function createPortfolioWindow() {
  const portfolioWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: 'Portfolio Analysis',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  portfolioWindow.loadFile(path.join(__dirname, 'portfolio.html'));
}

function createUserManagementWindow() {
  const userManagementWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: 'User Management',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  userManagementWindow.loadFile(path.join(__dirname, 'user-management.html'));
}

function createSystemMonitorWindow() {
  const monitorWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: 'System Monitor',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  monitorWindow.loadFile(path.join(__dirname, 'system-monitor.html'));
}

function createSecurityWindow() {
  const securityWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    title: 'Security Settings',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  securityWindow.loadFile(path.join(__dirname, 'security.html'));
}

function createSettingsWindow() {
  if (settingsWindow) {
    settingsWindow.focus();
    return;
  }

  settingsWindow = new BrowserWindow({
    width: 800,
    height: 600,
    title: 'Settings',
    parent: mainWindow,
    modal: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  settingsWindow.loadFile(path.join(__dirname, 'settings.html'));
  
  settingsWindow.on('closed', () => {
    settingsWindow = null;
  });
}

async function importData(filePath) {
  try {
    const data = await fs.readFile(filePath, 'utf8');
    const parsed = JSON.parse(data);
    
    // Import data to database
    // Implementation depends on data structure
    
    dialog.showMessageBox({
      type: 'info',
      title: 'Import Successful',
      message: 'Data imported successfully',
    });
  } catch (error) {
    dialog.showMessageBox({
      type: 'error',
      title: 'Import Failed',
      message: `Error importing data: ${error.message}`,
    });
  }
}

async function exportData(filePath) {
  try {
    // Collect data to export
    const data = {
      tradingData,
      portfolio: [],
      settings: {},
      timestamp: new Date().toISOString(),
    };
    
    await fs.writeFile(filePath, JSON.stringify(data, null, 2));
    
    dialog.showMessageBox({
      type: 'info',
      title: 'Export Successful',
      message: 'Data exported successfully',
    });
  } catch (error) {
    dialog.showMessageBox({
      type: 'error',
      title: 'Export Failed',
      message: `Error exporting data: ${error.message}`,
    });
  }
}

function lockApp() {
  if (mainWindow) {
    mainWindow.webContents.send('lock-app');
  }
}

// App Event Handlers
app.whenReady().then(initializeApp);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', async () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    await createMainWindow();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
  
  // Cleanup
  if (performanceMonitor) {
    performanceMonitor.stop();
  }
  
  if (database) {
    database.close();
  }
  
  if (tray) {
    tray.destroy();
  }
  
  // Unregister all shortcuts
  globalShortcut.unregisterAll();
});

app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  // Allow certificate errors in development
  if (process.env.NODE_ENV === 'development') {
    event.preventDefault();
    callback(true);
  } else {
    callback(false);
  }
});

// Security event handlers
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
});

// Performance monitoring
setInterval(() => {
  if (performanceMonitor && database) {
    const metrics = performanceMonitor.getMetrics();
    database.run('INSERT INTO performance_metrics (cpu_usage, memory_usage, disk_usage, network_usage, app_runtime, render_time) VALUES (?, ?, ?, ?, ?, ?)', [
      metrics.cpu,
      metrics.memory,
      metrics.disk,
      metrics.network,
      metrics.appRuntime,
      metrics.renderTime,
    ]);
  }
}, 60000); // Every minute

// Error handling
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  if (securityManager) {
    securityManager.logSecurityEvent({
      type: 'uncaught_exception',
      details: { error: error.message, stack: error.stack },
    });
  }
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  if (securityManager) {
    securityManager.logSecurityEvent({
      type: 'unhandled_rejection',
      details: { reason: reason.toString(), promise: promise.toString() },
    });
  }
});

console.log('TigerEx Desktop Application started');