/**
 * TigerEx Unified Desktop Application
 * Consolidated from desktop/, desktop-app/, and desktop-apps/
 * Features: Multi-window support, security, auto-updater, hardware wallet integration
 * Version: 4.0.0
 */

const { app, BrowserWindow, ipcMain, Menu, Tray, dialog, shell, Notification } = require('electron');
const path = require('path');
const fs = require('fs');
const Store = require('electron-store');
const axios = require('axios');
const { autoUpdater } = require('electron-updater');
const log = require('electron-log');
const isDev = require('electron-is-dev');

// Configure logging
log.transports.file.level = 'info';
log.info('TigerEx Unified Desktop starting...');

// Constants
const APP_CONFIG = {
  name: 'TigerEx',
  version: '4.0.0',
  minWidth: 1200,
  minHeight: 700,
  defaultWidth: 1400,
  defaultHeight: 900,
  apiUrl: process.env.API_URL || 'https://api.tigerex.com',
  websocketUrl: process.env.WS_URL || 'wss://ws.tigerex.com'
};

// Global variables
let mainWindow;
let windows = new Map();
let tray;
let store;
let isQuitting = false;

// Initialize electron-store
try {
  store = new Store({
    name: 'tigerex-desktop',
    defaults: {
      windowBounds: { width: APP_CONFIG.defaultWidth, height: APP_CONFIG.defaultHeight },
      settings: {
        theme: 'dark',
        language: 'en',
        notifications: true,
        autoUpdate: true,
        hardwareAcceleration: true
      },
      session: null,
      favorites: [],
      alerts: []
    }
  });
} catch (error) {
  log.error('Failed to initialize store:', error);
}

/**
 * Create main application window
 */
function createMainWindow() {
  try {
    const windowBounds = store.get('windowBounds', { 
      width: APP_CONFIG.defaultWidth, 
      height: APP_CONFIG.defaultHeight 
    });

    mainWindow = new BrowserWindow({
      width: windowBounds.width,
      height: windowBounds.height,
      minWidth: APP_CONFIG.minWidth,
      minHeight: APP_CONFIG.minHeight,
      title: APP_CONFIG.name,
      icon: getIconPath(),
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js'),
        webSecurity: true,
        allowRunningInsecureContent: false,
        experimentalFeatures: false
      },
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      show: false,
      autoHideMenuBar: false
    });

    // Load the application
    const startUrl = getStartUrl();
    mainWindow.loadURL(startUrl);

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
      
      if (isDev) {
        mainWindow.webContents.openDevTools();
      }
    });

    // Handle external links
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });

    // Handle window close
    mainWindow.on('close', (event) => {
      if (process.platform === 'darwin' && !isQuitting) {
        event.preventDefault();
        mainWindow.hide();
      } else {
        saveWindowBounds();
      }
    });

    // Handle window resize/move
    mainWindow.on('resize', saveWindowBounds);
    mainWindow.on('move', saveWindowBounds);

    // Add to windows map
    windows.set('main', mainWindow);

    log.info('Main window created successfully');
    return mainWindow;

  } catch (error) {
    log.error('Failed to create main window:', error);
    throw error;
  }
}

/**
 * Create additional windows (trading, charts, etc.)
 */
function createWindow(windowId, options = {}) {
  try {
    const window = new BrowserWindow({
      width: options.width || 1200,
      height: options.height || 800,
      minWidth: 800,
      minHeight: 600,
      title: options.title || 'TigerEx',
      icon: getIconPath(),
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js'),
        webSecurity: true
      },
      show: false,
      parent: options.modal ? mainWindow : null,
      modal: options.modal || false
    });

    // Load URL
    if (options.url) {
      window.loadURL(options.url);
    } else if (options.route) {
      const startUrl = getStartUrl() + '#' + options.route;
      window.loadURL(startUrl);
    } else {
      window.loadURL(getStartUrl());
    }

    window.once('ready-to-show', () => {
      window.show();
      if (isDev) {
        window.webContents.openDevTools();
      }
    });

    windows.set(windowId, window);
    log.info(`Window ${windowId} created successfully`);
    return window;

  } catch (error) {
    log.error(`Failed to create window ${windowId}:`, error);
    throw error;
  }
}

/**
 * Get application start URL
 */
function getStartUrl() {
  if (isDev) {
    return 'http://localhost:3000';
  }
  
  const buildPath = path.join(__dirname, 'build', 'index.html');
  const rendererPath = path.join(__dirname, 'renderer', 'index.html');
  
  if (fs.existsSync(buildPath)) {
    return `file://${buildPath}`;
  } else if (fs.existsSync(rendererPath)) {
    return `file://${rendererPath}`;
  } else {
    // Fallback to simple HTML
    return `data:text/html;charset=utf-8,${encodeURIComponent(getFallbackHTML())}`;
  }
}

/**
 * Get fallback HTML for development
 */
function getFallbackHTML() {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>TigerEx Desktop</title>
      <style>
        body { 
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100vh;
          margin: 0;
        }
        .container {
          text-align: center;
          padding: 40px;
        }
        h1 { font-size: 48px; margin-bottom: 20px; }
        p { font-size: 18px; opacity: 0.9; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🐅 TigerEx Desktop</h1>
        <p>Professional Crypto Trading Platform</p>
        <p>Version ${APP_CONFIG.version}</p>
        <p>Status: Running in development mode</p>
      </div>
    </body>
    </html>
  `;
}

/**
 * Get icon path for current platform
 */
function getIconPath() {
  const iconDir = path.join(__dirname, 'assets');
  const icons = {
    darwin: 'icon.icns',
    win32: 'icon.ico',
    linux: 'icon.png'
  };
  
  const iconFile = icons[process.platform] || icons.linux;
  const iconPath = path.join(iconDir, iconFile);
  
  if (fs.existsSync(iconPath)) {
    return iconPath;
  }
  
  // Fallback to any available icon
  const fallbackIcons = ['icon.png', 'icon.ico', 'icon.icns'];
  for (const icon of fallbackIcons) {
    const fallbackPath = path.join(iconDir, icon);
    if (fs.existsSync(fallbackPath)) {
      return fallbackPath;
    }
  }
  
  return null;
}

/**
 * Save window bounds to store
 */
function saveWindowBounds() {
  if (mainWindow && !mainWindow.isDestroyed()) {
    const bounds = mainWindow.getBounds();
    store.set('windowBounds', bounds);
  }
}

/**
 * Create application menu
 */
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Order',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            createWindow('order', { title: 'New Order', width: 800, height: 600 });
          }
        },
        {
          label: 'New Chart',
          accelerator: 'CmdOrCtrl+T',
          click: () => {
            createWindow('chart', { title: 'Chart', width: 1000, height: 700 });
          }
        },
        { type: 'separator' },
        {
          label: 'Settings',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            createWindow('settings', { title: 'Settings', width: 600, height: 500 });
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            isQuitting = true;
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Trading',
      submenu: [
        {
          label: 'Spot Trading',
          accelerator: 'CmdOrCtrl+1',
          click: () => {
            mainWindow?.webContents.send('navigate', 'spot');
          }
        },
        {
          label: 'Futures Trading',
          accelerator: 'CmdOrCtrl+2',
          click: () => {
            mainWindow?.webContents.send('navigate', 'futures');
          }
        },
        {
          label: 'Options Trading',
          accelerator: 'CmdOrCtrl+3',
          click: () => {
            mainWindow?.webContents.send('navigate', 'options');
          }
        },
        {
          label: 'Margin Trading',
          accelerator: 'CmdOrCtrl+4',
          click: () => {
            mainWindow?.webContents.send('navigate', 'margin');
          }
        },
        { type: 'separator' },
        {
          label: 'Trading Bots',
          accelerator: 'CmdOrCtrl+B',
          click: () => {
            createWindow('bots', { title: 'Trading Bots', width: 1200, height: 800 });
          }
        },
        {
          label: 'Copy Trading',
          accelerator: 'CmdOrCtrl+C',
          click: () => {
            createWindow('copy-trading', { title: 'Copy Trading', width: 1200, height: 800 });
          }
        }
      ]
    },
    {
      label: 'Tools',
      submenu: [
        {
          label: 'Price Alerts',
          click: () => {
            createWindow('alerts', { title: 'Price Alerts', width: 800, height: 600 });
          }
        },
        {
          label: 'Portfolio Tracker',
          click: () => {
            createWindow('portfolio', { title: 'Portfolio', width: 1000, height: 700 });
          }
        },
        {
          label: 'Market Scanner',
          click: () => {
            createWindow('scanner', { title: 'Market Scanner', width: 1200, height: 800 });
          }
        },
        {
          label: 'Technical Analysis',
          click: () => {
            createWindow('analysis', { title: 'Technical Analysis', width: 1200, height: 800 });
          }
        },
        { type: 'separator' },
        {
          label: 'API Keys',
          click: () => {
            createWindow('api-keys', { title: 'API Keys', width: 800, height: 600 });
          }
        },
        {
          label: 'Hardware Wallet',
          click: () => {
            createWindow('hardware-wallet', { title: 'Hardware Wallet', width: 800, height: 600 });
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: () => {
            shell.openExternal('https://docs.tigerex.com');
          }
        },
        {
          label: 'API Documentation',
          click: () => {
            shell.openExternal('https://api.tigerex.com/docs');
          }
        },
        { type: 'separator' },
        {
          label: 'Support',
          click: () => {
            shell.openExternal('https://support.tigerex.com');
          }
        },
        {
          label: 'About TigerEx',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About TigerEx',
              message: `TigerEx Desktop v${APP_CONFIG.version}`,
              detail: 'Professional Cryptocurrency Exchange Platform\n\n© 2025 TigerEx Team\n\nFeatures:\n• Multi-platform trading\n• Advanced charting\n• Hardware wallet support\n• Copy trading\n• Trading bots\n• Portfolio management'
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

/**
 * Create system tray
 */
function createTray() {
  if (tray) return;

  const iconPath = getIconPath();
  if (!iconPath) {
    log.warn('No tray icon found');
    return;
  }

  tray = new Tray(iconPath);
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show TigerEx',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      }
    },
    {
      label: 'New Order',
      click: () => {
        createWindow('order', { title: 'New Order', width: 800, height: 600 });
      }
    },
    { type: 'separator' },
    {
      label: 'Settings',
      click: () => {
        createWindow('settings', { title: 'Settings', width: 600, height: 500 });
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('TigerEx Desktop');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

/**
 * IPC Handlers
 */
function setupIPCHandlers() {
  // Window management
  ipcMain.handle('window:create', (event, options) => {
    const windowId = options.id || `window_${Date.now()}`;
    return createWindow(windowId, options);
  });

  ipcMain.handle('window:close', (event, windowId) => {
    const window = windows.get(windowId);
    if (window && !window.isDestroyed()) {
      window.close();
      windows.delete(windowId);
    }
  });

  // Settings management
  ipcMain.handle('settings:get', (event, key) => {
    return store.get(key);
  });

  ipcMain.handle('settings:set', (event, key, value) => {
    store.set(key, value);
    return true;
  });

  ipcMain.handle('settings:get-all', () => {
    return store.store;
  });

  // Session management
  ipcMain.handle('session:get', () => {
    return store.get('session');
  });

  ipcMain.handle('session:set', (event, session) => {
    store.set('session', session);
    return true;
  });

  ipcMain.handle('session:clear', () => {
    store.delete('session');
    return true;
  });

  // API communication
  ipcMain.handle('api:get', async (event, endpoint) => {
    try {
      const response = await axios.get(`${APP_CONFIG.apiUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': `TigerEx-Desktop/${APP_CONFIG.version}`
        }
      });
      return { success: true, data: response.data };
    } catch (error) {
      log.error(`API GET ${endpoint} failed:`, error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('api:post', async (event, endpoint, data) => {
    try {
      const response = await axios.post(`${APP_CONFIG.apiUrl}${endpoint}`, data, {
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': `TigerEx-Desktop/${APP_CONFIG.version}`
        }
      });
      return { success: true, data: response.data };
    } catch (error) {
      log.error(`API POST ${endpoint} failed:`, error);
      return { success: false, error: error.message };
    }
  });

  // Notifications
  ipcMain.handle('notification:show', (event, { title, body, icon }) => {
    try {
      new Notification({
        title,
        body,
        icon: icon || getIconPath()
      }).show();
      return true;
    } catch (error) {
      log.error('Notification failed:', error);
      return false;
    }
  });

  // External links
  ipcMain.handle('shell:open-external', (event, url) => {
    shell.openExternal(url);
  });

  // File operations
  ipcMain.handle('file:save', async (event, { filename, data }) => {
    try {
      const result = await dialog.showSaveDialog(mainWindow, {
        defaultPath: filename,
        filters: [
          { name: 'JSON', extensions: ['json'] },
          { name: 'CSV', extensions: ['csv'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (!result.canceled && result.filePath) {
        fs.writeFileSync(result.filePath, data);
        return { success: true, filePath: result.filePath };
      }
      return { success: false, canceled: true };
    } catch (error) {
      log.error('File save failed:', error);
      return { success: false, error: error.message };
    }
  });
}

/**
 * Auto-updater setup
 */
function initializeAutoUpdater() {
  if (!store.get('settings.autoUpdate', true)) return;

  autoUpdater.logger = log;
  autoUpdater.checkForUpdatesAndNotify();

  autoUpdater.on('update-available', () => {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: 'A new version of TigerEx Desktop is available. It will be downloaded in the background.',
      buttons: ['OK']
    });
  });

  autoUpdater.on('update-downloaded', () => {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Ready',
      message: 'Update downloaded. The application will restart to apply the update.',
      buttons: ['Restart Now', 'Later']
    }).then((result) => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  });
}

/**
 * Security initialization
 */
function initializeSecurity() {
  // Prevent new window creation
  app.on('web-contents-created', (event, contents) => {
    contents.on('new-window', (event, navigationUrl) => {
      event.preventDefault();
      shell.openExternal(navigationUrl);
    });
  });

  // Prevent navigation to external URLs
  app.on('web-contents-created', (event, contents) => {
    contents.on('will-navigate', (event, navigationUrl) => {
      const parsedUrl = new URL(navigationUrl);
      if (parsedUrl.origin !== getStartUrl()) {
        event.preventDefault();
      }
    });
  });
}

/**
 * App initialization
 */
function initializeApp() {
  try {
    log.info('Initializing TigerEx Desktop...');

    // Security setup
    initializeSecurity();

    // App event handlers
    app.whenReady().then(() => {
      log.info('App ready, creating main window...');
      createMainWindow();
      createMenu();
      createTray();
      setupIPCHandlers();
      initializeAutoUpdater();
    });

    app.on('window-all-closed', () => {
      log.info('All windows closed');
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createMainWindow();
      }
    });

    app.on('before-quit', () => {
      isQuitting = true;
      saveWindowBounds();
    });

    // Handle uncaught exceptions
    process.on('uncaughtException', (error) => {
      log.error('Uncaught exception:', error);
      dialog.showErrorBox('Unexpected Error', error.message);
    });

    process.on('unhandledRejection', (reason, promise) => {
      log.error('Unhandled rejection at:', promise, 'reason:', reason);
    });

    log.info('TigerEx Desktop initialization complete');

  } catch (error) {
    log.error('App initialization failed:', error);
    dialog.showErrorBox('Initialization Error', error.message);
  }
}

// Start the application
initializeApp();