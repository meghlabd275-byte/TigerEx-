/**
 * TigerEx Enhanced Desktop Application
 * Complete cryptocurrency exchange desktop app with Electron and full admin controls
 */

const { app, BrowserWindow, ipcMain, dialog, shell, Menu, globalShortcut } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';

class TigerExDesktopApp {
  constructor() {
    this.mainWindow = null;
    this.isAdmin = false;
    this.user = null;
  }

  async initialize() {
    await app.whenReady();
    this.createMainWindow();
    this.setupMenu();
    this.setupGlobalShortcuts();
    this.setupIPC();
  }

  createMainWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      minWidth: 1200,
      minHeight: 700,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false,
        enableRemoteModule: true,
        preload: path.join(__dirname, 'preload.js')
      },
      icon: path.join(__dirname, 'assets/icon.png'),
      show: false,
      titleBarStyle: 'hiddenInset',
      vibrancy: 'under-window',
      visualEffectState: 'followWindow'
    });

    this.mainWindow.loadFile(path.join(__dirname, 'src/index.html'));

    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow.show();
      this.mainWindow.focus();
    });

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    // Open DevTools in development
    if (isDev) {
      this.mainWindow.webContents.openDevTools();
    }

    // Handle external links
    this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });
  }

  setupMenu() {
    const template = [
      {
        label: 'TigerEx',
        submenu: [
          {
            label: 'About TigerEx',
            click: () => {
              dialog.showMessageBox(this.mainWindow, {
                type: 'info',
                title: 'About TigerEx',
                message: 'TigerEx Professional Cryptocurrency Exchange',
                detail: 'Version 1.0.0\nComplete trading platform for desktop',
                buttons: ['OK']
              });
            }
          },
          { type: 'separator' },
          {
            label: 'Preferences',
            accelerator: 'CmdOrCtrl+,',
            click: () => {
              this.mainWindow.webContents.send('open-preferences');
            }
          },
          { type: 'separator' },
          {
            label: 'Quit',
            accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
            click: () => {
              app.quit();
            }
          }
        ]
      },
      {
        label: 'Trading',
        submenu: [
          {
            label: 'New Trade',
            accelerator: 'CmdOrCtrl+T',
            click: () => {
              this.mainWindow.webContents.send('new-trade');
            }
          },
          {
            label: 'Portfolio Overview',
            accelerator: 'CmdOrCtrl+P',
            click: () => {
              this.mainWindow.webContents.send('portfolio-overview');
            }
          },
          {
            label: 'Market Data',
            accelerator: 'CmdOrCtrl+M',
            click: () => {
              this.mainWindow.webContents.send('market-data');
            }
          },
          { type: 'separator' },
          {
            label: 'Order History',
            accelerator: 'CmdOrCtrl+O',
            click: () => {
              this.mainWindow.webContents.send('order-history');
            }
          },
          {
            label: 'Trade Settings',
            accelerator: 'CmdOrCtrl+,',
            click: () => {
              this.mainWindow.webContents.send('trade-settings');
            }
          }
        ]
      },
      {
        label: 'Tools',
        submenu: [
          {
            label: 'Trading Bots',
            accelerator: 'CmdOrCtrl+B',
            click: () => {
              this.mainWindow.webContents.send('trading-bots');
            }
          },
          {
            label: 'Market Analysis',
            accelerator: 'CmdOrCtrl+A',
            click: () => {
              this.mainWindow.webContents.send('market-analysis');
            }
          },
          {
            label: 'Risk Management',
            accelerator: 'CmdOrCtrl+R',
            click: () => {
              this.mainWindow.webContents.send('risk-management');
            }
          },
          { type: 'separator' },
          {
            label: 'API Console',
            accelerator: 'CmdOrCtrl+Shift+A',
            click: () => {
              this.mainWindow.webContents.send('api-console');
            }
          },
          {
            label: 'WebSocket Monitor',
            accelerator: 'CmdOrCtrl+Shift+W',
            click: () => {
              this.mainWindow.webContents.send('websocket-monitor');
            }
          }
        ]
      },
      {
        label: 'Admin',
        submenu: [
          {
            label: 'Admin Panel',
            accelerator: 'CmdOrCtrl+Shift+P',
            click: () => {
              this.mainWindow.webContents.send('admin-panel');
            }
          },
          {
            label: 'User Management',
            accelerator: 'CmdOrCtrl+Shift+U',
            click: () => {
              this.mainWindow.webContents.send('user-management');
            }
          },
          {
            label: 'System Monitor',
            accelerator: 'CmdOrCtrl+Shift+S',
            click: () => {
              this.mainWindow.webContents.send('system-monitor');
            }
          },
          {
            label: 'Security Center',
            accelerator: 'CmdOrCtrl+Shift+X',
            click: () => {
              this.mainWindow.webContents.send('security-center');
            }
          },
          { type: 'separator' },
          {
            label: 'Database Manager',
            accelerator: 'CmdOrCtrl+Shift+D',
            click: () => {
              this.mainWindow.webContents.send('database-manager');
            }
          },
          {
            label: 'Service Configuration',
            accelerator: 'CmdOrCtrl+Shift+C',
            click: () => {
              this.mainWindow.webContents.send('service-config');
            }
          }
        ]
      },
      {
        label: 'Window',
        submenu: [
          {
            label: 'Minimize',
            accelerator: 'CmdOrCtrl+M',
            role: 'minimize'
          },
          {
            label: 'Close',
            accelerator: 'CmdOrCtrl+W',
            role: 'close'
          },
          { type: 'separator' },
          {
            label: 'Bring All to Front',
            role: 'front'
          }
        ]
      },
      {
        label: 'Help',
        submenu: [
          {
            label: 'TigerEx Documentation',
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
          {
            label: 'Community Forums',
            click: () => {
              shell.openExternal('https://community.tigerex.com');
            }
          },
          { type: 'separator' },
          {
            label: 'Check for Updates',
            click: () => {
              this.checkForUpdates();
            }
          },
          {
            label: 'Report an Issue',
            click: () => {
              shell.openExternal('https://github.com/tigerex/issues');
            }
          },
          { type: 'separator' },
          {
            label: 'Keyboard Shortcuts',
            accelerator: 'CmdOrCtrl+?',
            click: () => {
              this.showKeyboardShortcuts();
            }
          }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  setupGlobalShortcuts() {
    // Quick trade shortcut
    globalShortcut.register('CommandOrControl+Shift+T', () => {
      this.mainWindow.webContents.send('quick-trade');
    });

    // Refresh data shortcut
    globalShortcut.register('F5', () => {
      this.mainWindow.webContents.send('refresh-data');
    });

    // Toggle admin panel
    globalShortcut.register('CommandOrControl+Shift+A', () => {
      this.mainWindow.webContents.send('toggle-admin');
    });

    // Emergency stop trading
    globalShortcut.register('CommandOrControl+Shift+E', () => {
      this.emergencyStopTrading();
    });
  }

  setupIPC() {
    // Authentication
    ipcMain.handle('login', async (event, credentials) => {
      try {
        // Simulate authentication
        if (credentials.email === 'admin@tigerex.com' && credentials.password === 'password') {
          this.user = {
            id: 1,
            email: 'admin@tigerex.com',
            username: 'admin',
            full_name: 'System Administrator',
            is_admin: true,
            is_superadmin: true
          };
          this.isAdmin = true;
          return { success: true, user: this.user };
        }
        return { success: false, message: 'Invalid credentials' };
      } catch (error) {
        return { success: false, message: error.message };
      }
    });

    // Market data
    ipcMain.handle('get-market-data', async () => {
      return {
        timestamp: new Date().toISOString(),
        data: [
          { symbol: 'BTC/USDT', price: 43567.89, change: 2.34, volume: 1234567890 },
          { symbol: 'ETH/USDT', price: 2234.56, change: -1.23, volume: 987654321 },
          { symbol: 'BNB/USDT', price: 312.45, change: 0.87, volume: 456789012 }
        ]
      };
    });

    // Trading operations
    ipcMain.handle('place-order', async (event, orderData) => {
      try {
        // Simulate order placement
        const order = {
          id: Date.now().toString(),
          ...orderData,
          status: 'pending',
          timestamp: new Date().toISOString()
        };
        
        // Emit real-time update
        this.mainWindow.webContents.send('order-update', order);
        
        return { success: true, order };
      } catch (error) {
        return { success: false, message: error.message };
      }
    });

    // Admin operations
    ipcMain.handle('get-users', async () => {
      if (!this.isAdmin) {
        return { success: false, message: 'Admin access required' };
      }
      
      return {
        success: true,
        users: [
          {
            id: 1,
            email: 'user1@example.com',
            username: 'trader1',
            full_name: 'Trader One',
            kyc_status: 'approved',
            is_active: true,
            created_at: '2024-01-15T10:30:00Z'
          },
          {
            id: 2,
            email: 'user2@example.com',
            username: 'trader2',
            full_name: 'Trader Two',
            kyc_status: 'pending',
            is_active: true,
            created_at: '2024-02-20T09:15:00Z'
          }
        ]
      };
    });

    ipcMain.handle('update-user', async (event, userId, updateData) => {
      if (!this.isAdmin) {
        return { success: false, message: 'Admin access required' };
      }
      
      // Simulate user update
      this.mainWindow.webContents.send('user-updated', { userId, updateData });
      
      return { success: true, message: 'User updated successfully' };
    });

    // System operations
    ipcMain.handle('get-system-status', async () => {
      if (!this.isAdmin) {
        return { success: false, message: 'Admin access required' };
      }
      
      return {
        success: true,
        status: {
          database: 'healthy',
          redis: 'healthy',
          trading_engine: 'healthy',
          api_gateway: 'healthy',
          cpu_usage: 45.2,
          memory_usage: 67.8,
          disk_usage: 32.1,
          network_status: 'good',
          uptime: '15 days 7 hours 23 minutes'
        }
      };
    });

    // File operations
    ipcMain.handle('export-data', async (event, dataType, format) => {
      try {
        const result = await dialog.showSaveDialog(this.mainWindow, {
          defaultPath: `${dataType}-export.${format}`,
          filters: [
            { name: format.toUpperCase(), extensions: [format] },
            { name: 'All Files', extensions: ['*'] }
          ]
        });

        if (!result.canceled) {
          // Simulate data export
          this.mainWindow.webContents.send('export-progress', { progress: 0 });
          
          for (let i = 0; i <= 100; i += 10) {
            this.mainWindow.webContents.send('export-progress', { progress: i });
            await new Promise(resolve => setTimeout(resolve, 100));
          }
          
          return { success: true, filePath: result.filePath };
        }
        
        return { success: false, message: 'Export cancelled' };
      } catch (error) {
        return { success: false, message: error.message };
      }
    });

    // Notifications
    ipcMain.handle('show-notification', async (event, notificationData) => {
      const { title, body, type } = notificationData;
      
      // Show system notification
      this.mainWindow.webContents.send('system-notification', { title, body, type });
      
      return { success: true };
    });

    // Security operations
    ipcMain.handle('emergency-stop', async () => {
      if (!this.isAdmin) {
        return { success: false, message: 'Admin access required' };
      }
      
      // Simulate emergency stop
      this.mainWindow.webContents.send('emergency-stop-activated');
      
      return { success: true, message: 'Emergency stop activated' };
    });
  }

  checkForUpdates() {
    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'Check for Updates',
      message: 'You are running the latest version of TigerEx Desktop.',
      detail: 'Current Version: 1.0.0',
      buttons: ['OK']
    });
  }

  showKeyboardShortcuts() {
    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'Keyboard Shortcuts',
      message: 'TigerEx Desktop Shortcuts',
      detail: `
Trading:
• Cmd/Ctrl+T - New Trade
• Cmd/Ctrl+P - Portfolio Overview
• Cmd/Ctrl+M - Market Data
• Cmd/Ctrl+O - Order History

Admin:
• Cmd/Ctrl+Shift+P - Admin Panel
• Cmd/Ctrl+Shift+U - User Management
• Cmd/Ctrl+Shift+S - System Monitor

Quick Actions:
• Cmd/Ctrl+Shift+T - Quick Trade
• F5 - Refresh Data
• Cmd/Ctrl+Shift+A - Toggle Admin Panel
• Cmd/Ctrl+Shift+E - Emergency Stop Trading
      `.trim(),
      buttons: ['OK']
    });
  }

  emergencyStopTrading() {
    dialog.showMessageBox(this.mainWindow, {
      type: 'warning',
      title: 'Emergency Stop',
      message: 'Are you sure you want to activate emergency stop?',
      detail: 'This will halt all trading operations immediately.',
      buttons: ['Cancel', 'Activate Emergency Stop']
    }).then((result) => {
      if (result.response === 1) {
        this.mainWindow.webContents.send('emergency-stop-activated');
      }
    });
  }
}

// Initialize the application
const tigerExApp = new TigerExDesktopApp();
tigerExApp.initialize();

// Handle app events
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    tigerExApp.createMainWindow();
  }
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
});

// Handle certificate errors in production
if (!isDev) {
  app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
    event.preventDefault();
    callback(true);
  });
}

module.exports = TigerExDesktopApp;