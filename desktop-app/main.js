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

const { app, BrowserWindow, Menu, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const Store = require('electron-store');
const notifier = require('node-notifier');

// Initialize electron store
const store = new Store();

let mainWindow;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    icon: path.join(__dirname, 'assets/icon.png'),
    titleBarStyle: 'default',
    show: false
  });

  // Load the app
  mainWindow.loadFile('index.html');

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Focus on window
    if (process.platform === 'darwin') {
      app.dock.show();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Create application menu
  createMenu();
}

function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Order',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.send('menu-new-order');
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
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
      label: 'Trading',
      submenu: [
        {
          label: 'Spot Trading',
          click: () => {
            mainWindow.webContents.send('navigate-to', 'spot-trading');
          }
        },
        {
          label: 'Futures Trading',
          click: () => {
            mainWindow.webContents.send('navigate-to', 'futures-trading');
          }
        },
        {
          label: 'P2P Trading',
          click: () => {
            mainWindow.webContents.send('navigate-to', 'p2p-trading');
          }
        }
      ]
    },
    {
      label: 'Account',
      submenu: [
        {
          label: 'Profile',
          click: () => {
            mainWindow.webContents.send('navigate-to', 'profile');
          }
        },
        {
          label: 'Security',
          click: () => {
            mainWindow.webContents.send('navigate-to', 'security');
          }
        },
        {
          label: 'Verification',
          click: () => {
            mainWindow.webContents.send('navigate-to', 'verification');
          }
        }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About TigerEx',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About TigerEx',
              message: 'TigerEx Desktop',
              detail: 'Version 1.0.0\nComplete Cryptocurrency Exchange Platform'
            });
          }
        },
        {
          label: 'Support',
          click: () => {
            shell.openExternal('https://support.tigerex.com');
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App event handlers
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC handlers
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('show-notification', (event, title, body) => {
  notifier.notify({
    title: title,
    message: body,
    icon: path.join(__dirname, 'assets/icon.png'),
    sound: true
  });
});

ipcMain.handle('store-get', (event, key) => {
  return store.get(key);
});

ipcMain.handle('store-set', (event, key, value) => {
  store.set(key, value);
});
