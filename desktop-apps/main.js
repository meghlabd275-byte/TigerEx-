/**
 * TigerEx Desktop Application - Main Process
 * Cross-platform desktop application for Windows, macOS, and Linux
 */

const { app, BrowserWindow, ipcMain, Menu, Tray, dialog, shell } = require('electron');
const path = require('path');
const Store = require('electron-store');
const axios = require('axios');

// Initialize electron-store for persistent data
const store = new Store();

// Global variables
let mainWindow;
let tray;
const API_BASE_URL = process.env.API_URL || 'https://api.tigerex.com';

// App configuration
const APP_CONFIG = {
  name: 'TigerEx',
  version: '1.0.0',
  minWidth: 1200,
  minHeight: 800,
  defaultWidth: 1400,
  defaultHeight: 900
};

/**
 * Create the main application window
 */
function createMainWindow() {
  // Get saved window bounds or use defaults
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
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    backgroundColor: '#1a1a2e',
    show: false // Don't show until ready
  });

  // Load the application
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Save window bounds on resize/move
  mainWindow.on('resize', () => {
    store.set('windowBounds', mainWindow.getBounds());
  });

  mainWindow.on('move', () => {
    store.set('windowBounds', mainWindow.getBounds());
  });

  // Handle window close
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create application menu
  createMenu();
}

/**
 * Create system tray icon
 */
function createTray() {
  tray = new Tray(path.join(__dirname, 'assets', 'tray-icon.png'));
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show TigerEx',
      click: () => {
        mainWindow.show();
      }
    },
    {
      label: 'Markets',
      click: () => {
        mainWindow.show();
        mainWindow.webContents.send('navigate', '/markets');
      }
    },
    {
      label: 'Portfolio',
      click: () => {
        mainWindow.show();
        mainWindow.webContents.send('navigate', '/portfolio');
      }
    },
    { type: 'separator' },
    {
      label: 'Settings',
      click: () => {
        mainWindow.show();
        mainWindow.webContents.send('navigate', '/settings');
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('TigerEx - Cryptocurrency Exchange');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
  });
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
            mainWindow.webContents.send('open-order-dialog');
          }
        },
        { type: 'separator' },
        {
          label: 'Settings',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            mainWindow.webContents.send('navigate', '/settings');
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.isQuitting = true;
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Markets',
          accelerator: 'CmdOrCtrl+1',
          click: () => {
            mainWindow.webContents.send('navigate', '/markets');
          }
        },
        {
          label: 'Trading',
          accelerator: 'CmdOrCtrl+2',
          click: () => {
            mainWindow.webContents.send('navigate', '/trading');
          }
        },
        {
          label: 'Portfolio',
          accelerator: 'CmdOrCtrl+3',
          click: () => {
            mainWindow.webContents.send('navigate', '/portfolio');
          }
        },
        {
          label: 'Wallet',
          accelerator: 'CmdOrCtrl+4',
          click: () => {
            mainWindow.webContents.send('navigate', '/wallet');
          }
        },
        { type: 'separator' },
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
      label: 'Trading',
      submenu: [
        {
          label: 'Spot Trading',
          click: () => {
            mainWindow.webContents.send('navigate', '/trading/spot');
          }
        },
        {
          label: 'Futures Trading',
          click: () => {
            mainWindow.webContents.send('navigate', '/trading/futures');
          }
        },
        {
          label: 'Options Trading',
          click: () => {
            mainWindow.webContents.send('navigate', '/trading/options');
          }
        },
        { type: 'separator' },
        {
          label: 'Order History',
          click: () => {
            mainWindow.webContents.send('navigate', '/orders');
          }
        },
        {
          label: 'Trade History',
          click: () => {
            mainWindow.webContents.send('navigate', '/trades');
          }
        }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: async () => {
            await shell.openExternal('https://docs.tigerex.com');
          }
        },
        {
          label: 'API Documentation',
          click: async () => {
            await shell.openExternal('https://docs.tigerex.com/api');
          }
        },
        { type: 'separator' },
        {
          label: 'Support',
          click: async () => {
            await shell.openExternal('https://support.tigerex.com');
          }
        },
        {
          label: 'Report Issue',
          click: async () => {
            await shell.openExternal('https://github.com/tigerex/issues');
          }
        },
        { type: 'separator' },
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About TigerEx',
              message: `TigerEx Desktop v${APP_CONFIG.version}`,
              detail: 'Professional Cryptocurrency Exchange Platform\n\n© 2025 TigerEx. All rights reserved.',
              buttons: ['OK']
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
 * IPC Handlers
 */

// Get stored data
ipcMain.handle('store-get', (event, key) => {
  return store.get(key);
});

// Set stored data
ipcMain.handle('store-set', (event, key, value) => {
  store.set(key, value);
  return true;
});

// Delete stored data
ipcMain.handle('store-delete', (event, key) => {
  store.delete(key);
  return true;
});

// API request handler
ipcMain.handle('api-request', async (event, { method, endpoint, data, headers }) => {
  try {
    const response = await axios({
      method,
      url: `${API_BASE_URL}${endpoint}`,
      data,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      }
    });
    return { success: true, data: response.data };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data || error.message
    };
  }
});

// Open external link
ipcMain.handle('open-external', async (event, url) => {
  await shell.openExternal(url);
});

// Show notification
ipcMain.handle('show-notification', (event, { title, body }) => {
  const notification = new Notification({
    title,
    body,
    icon: path.join(__dirname, 'assets', 'icon.png')
  });
  notification.show();
});

// Get app version
ipcMain.handle('get-app-version', () => {
  return APP_CONFIG.version;
});

/**
 * App lifecycle events
 */

app.whenReady().then(() => {
  createMainWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    } else {
      mainWindow.show();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  dialog.showErrorBox('Error', `An unexpected error occurred: ${error.message}`);
});

// Auto-updater (for production)
if (process.env.NODE_ENV === 'production') {
  // Implement auto-updater logic here
  // Example: electron-updater
}