const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const Store = require('electron-store');

const store = new Store();

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    icon: path.join(__dirname, '../assets/icon.png'),
  });

  // Load the app
  const startUrl = process.env.ELECTRON_START_URL || `file://${path.join(__dirname, '../build/index.html')}`;
  mainWindow.loadURL(startUrl);

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  // Create application menu
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Order',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.send('new-order');
          },
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          },
        },
      ],
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Dashboard',
          accelerator: 'CmdOrCtrl+1',
          click: () => {
            mainWindow.webContents.send('navigate', 'dashboard');
          },
        },
        {
          label: 'Trading',
          accelerator: 'CmdOrCtrl+2',
          click: () => {
            mainWindow.webContents.send('navigate', 'trading');
          },
        },
        {
          label: 'Wallet',
          accelerator: 'CmdOrCtrl+3',
          click: () => {
            mainWindow.webContents.send('navigate', 'wallet');
          },
        },
        {
          label: 'Admin Panel',
          accelerator: 'CmdOrCtrl+A',
          click: () => {
            mainWindow.webContents.send('navigate', 'admin');
          },
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
        { role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Trading',
      submenu: [
        {
          label: 'Spot Trading',
          click: () => {
            mainWindow.webContents.send('trading-mode', 'spot');
          },
        },
        {
          label: 'Futures Trading',
          click: () => {
            mainWindow.webContents.send('trading-mode', 'futures');
          },
        },
        {
          label: 'Options Trading',
          click: () => {
            mainWindow.webContents.send('trading-mode', 'options');
          },
        },
        { type: 'separator' },
        {
          label: 'Trading Bots',
          click: () => {
            mainWindow.webContents.send('navigate', 'bots');
          },
        },
        {
          label: 'Copy Trading',
          click: () => {
            mainWindow.webContents.send('navigate', 'copy-trading');
          },
        },
      ],
    },
    {
      label: 'Tools',
      submenu: [
        {
          label: 'Price Alerts',
          click: () => {
            mainWindow.webContents.send('open-tool', 'alerts');
          },
        },
        {
          label: 'Portfolio Tracker',
          click: () => {
            mainWindow.webContents.send('open-tool', 'portfolio');
          },
        },
        {
          label: 'Market Scanner',
          click: () => {
            mainWindow.webContents.send('open-tool', 'scanner');
          },
        },
        {
          label: 'Technical Analysis',
          click: () => {
            mainWindow.webContents.send('open-tool', 'analysis');
          },
        },
      ],
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: () => {
            require('electron').shell.openExternal('https://docs.tigerex.com');
          },
        },
        {
          label: 'API Documentation',
          click: () => {
            require('electron').shell.openExternal('https://api.tigerex.com/docs');
          },
        },
        { type: 'separator' },
        {
          label: 'Support',
          click: () => {
            require('electron').shell.openExternal('https://support.tigerex.com');
          },
        },
        {
          label: 'About TigerEx',
          click: () => {
            mainWindow.webContents.send('show-about');
          },
        },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App lifecycle
app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// IPC handlers
ipcMain.on('save-settings', (event, settings) => {
  store.set('settings', settings);
  event.reply('settings-saved', true);
});

ipcMain.on('get-settings', (event) => {
  const settings = store.get('settings', {});
  event.reply('settings-loaded', settings);
});

ipcMain.on('save-session', (event, session) => {
  store.set('session', session);
});

ipcMain.on('get-session', (event) => {
  const session = store.get('session', null);
  event.reply('session-loaded', session);
});

ipcMain.on('clear-session', (event) => {
  store.delete('session');
  event.reply('session-cleared', true);
});

// Multi-window support
ipcMain.on('open-new-window', (event, route) => {
  const newWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  const startUrl = process.env.ELECTRON_START_URL || `file://${path.join(__dirname, '../build/index.html')}`;
  newWindow.loadURL(`${startUrl}#${route}`);
});

// Notifications
ipcMain.on('show-notification', (event, { title, body }) => {
  const { Notification } = require('electron');
  new Notification({ title, body }).show();
});

console.log('TigerEx Desktop App Started');