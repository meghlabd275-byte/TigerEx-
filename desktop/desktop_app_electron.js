// TigerEx Desktop Application - Advanced Trading Platform
// Electron.js implementation with React and TypeScript

const { app, BrowserWindow, ipcMain, Menu, shell, dialog, nativeImage } = require('electron');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const axios = require('axios');
const Store = require('electron-store');

// Initialize secure storage
const store = new Store();

// Security configuration
const SECURITY_CONFIG = {
    enableRemoteModule: false,
    nodeIntegration: false,
    contextIsolation: true,
    webSecurity: true,
    allowRunningInsecureContent: false,
    experimentalFeatures: false
};

class TigerExDesktopApp {
    constructor() {
        this.mainWindow = null;
        this.tradingWindow = null;
        this.settingsWindow = null;
        this.isDevelopment = process.env.NODE_ENV === 'development';
        this.setupSecurity();
    }

    setupSecurity() {
        // Set application user model ID for Windows
        if (process.platform === 'win32') {
            app.setAppUserModelId('com.tigerex.desktop');
        }

        // Security settings
        app.on('web-contents-created', (event, contents) => {
            contents.on('new-window', (event, navigationUrl) => {
                event.preventDefault();
                shell.openExternal(navigationUrl);
            });

            contents.on('will-navigate', (event, navigationUrl) => {
                const parsedUrl = new URL(navigationUrl);
                if (parsedUrl.origin !== 'http://localhost:3000' && 
                    parsedUrl.origin !== 'https://app.tigerex.com') {
                    event.preventDefault();
                }
            });
        });
    }

    createMainWindow() {
        this.mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            minWidth: 1200,
            minHeight: 700,
            show: false,
            frame: false,
            titleBarStyle: 'hiddenInset',
            backgroundColor: '#0A0E1A',
            webPreferences: {
                ...SECURITY_CONFIG,
                preload: path.join(__dirname, 'preload.js')
            },
            icon: path.join(__dirname, 'assets/icon.png')
        });

        // Load the application
        if (this.isDevelopment) {
            this.mainWindow.loadURL('http://localhost:3000');
            this.mainWindow.webContents.openDevTools();
        } else {
            this.mainWindow.loadFile(path.join(__dirname, 'build/index.html'));
        }

        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
            this.mainWindow.focus();
        });

        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });

        this.setupMenu();
        this.setupIpcHandlers();
    }

    createTradingWindow() {
        this.tradingWindow = new BrowserWindow({
            width: 1600,
            height: 1000,
            minWidth: 1400,
            minHeight: 800,
            parent: this.mainWindow,
            show: false,
            frame: false,
            backgroundColor: '#0A0E1A',
            webPreferences: {
                ...SECURITY_CONFIG,
                preload: path.join(__dirname, 'preload.js')
            }
        });

        if (this.isDevelopment) {
            this.tradingWindow.loadURL('http://localhost:3000/trading');
        } else {
            this.tradingWindow.loadFile(path.join(__dirname, 'build/index.html'), {
                hash: '/trading'
            });
        }

        this.tradingWindow.once('ready-to-show', () => {
            this.tradingWindow.show();
        });

        this.tradingWindow.on('closed', () => {
            this.tradingWindow = null;
        });
    }

    createSettingsWindow() {
        this.settingsWindow = new BrowserWindow({
            width: 600,
            height: 700,
            parent: this.mainWindow,
            show: false,
            frame: false,
            backgroundColor: '#0A0E1A',
            resizable: false,
            webPreferences: {
                ...SECURITY_CONFIG,
                preload: path.join(__dirname, 'preload.js')
            }
        });

        if (this.isDevelopment) {
            this.settingsWindow.loadURL('http://localhost:3000/settings');
        } else {
            this.settingsWindow.loadFile(path.join(__dirname, 'build/index.html'), {
                hash: '/settings'
            });
        }

        this.settingsWindow.once('ready-to-show', () => {
            this.settingsWindow.show();
        });

        this.settingsWindow.on('closed', () => {
            this.settingsWindow = null;
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
                                message: 'TigerEx Desktop Application',
                                detail: 'Advanced cryptocurrency trading platform v2.0.0',
                                buttons: ['OK']
                            });
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Preferences',
                        accelerator: process.platform === 'darwin' ? 'Cmd+,' : 'Ctrl+,',
                        click: () => this.createSettingsWindow()
                    },
                    { type: 'separator' },
                    {
                        label: 'Quit',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => app.quit()
                    }
                ]
            },
            {
                label: 'Trading',
                submenu: [
                    {
                        label: 'New Trading Window',
                        accelerator: 'CmdOrCtrl+T',
                        click: () => this.createTradingWindow()
                    },
                    {
                        label: 'Advanced Chart',
                        accelerator: 'CmdOrCtrl+D',
                        click: () => {
                            if (this.mainWindow) {
                                this.mainWindow.webContents.send('open-advanced-chart');
                            }
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
                label: 'Window',
                submenu: [
                    { role: 'minimize' },
                    { role: 'close' }
                ]
            },
            {
                label: 'Help',
                submenu: [
                    {
                        label: 'Documentation',
                        click: () => shell.openExternal('https://docs.tigerex.com')
                    },
                    {
                        label: 'Support',
                        click: () => shell.openExternal('https://support.tigerex.com')
                    },
                    {
                        label: 'Report Issue',
                        click: () => shell.openExternal('https://github.com/tigerex/issues')
                    }
                ]
            }
        ];

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    setupIpcHandlers() {
        // Authentication handlers
        ipcMain.handle('authenticate', async (event, credentials) => {
            try {
                const response = await axios.post('https://api.tigerex.com/auth/login', credentials);
                const { access_token, refresh_token, user } = response.data;
                
                // Securely store tokens
                store.set('access_token', this.encrypt(access_token));
                store.set('refresh_token', this.encrypt(refresh_token));
                store.set('user', user);
                
                return { success: true, user };
            } catch (error) {
                return { success: false, error: error.message };
            }
        });

        ipcMain.handle('logout', async () => {
            store.delete('access_token');
            store.delete('refresh_token');
            store.delete('user');
            return { success: true };
        });

        ipcMain.handle('getStoredUser', async () => {
            const encryptedToken = store.get('access_token');
            if (encryptedToken) {
                const token = this.decrypt(encryptedToken);
                // Verify token validity
                try {
                    const response = await axios.get('https://api.tigerex.com/auth/me', {
                        headers: { Authorization: `Bearer ${token}` }
                    });
                    return response.data;
                } catch (error) {
                    // Token invalid, clear storage
                    store.delete('access_token');
                    store.delete('refresh_token');
                    return null;
                }
            }
            return null;
        });

        // Trading handlers
        ipcMain.handle('getMarketData', async (event, symbol) => {
            try {
                const token = this.decrypt(store.get('access_token'));
                const response = await axios.get(`https://api.tigerex.com/markets/${symbol}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                return response.data;
            } catch (error) {
                return { error: error.message };
            }
        });

        ipcMain.handle('placeOrder', async (event, orderData) => {
            try {
                const token = this.decrypt(store.get('access_token'));
                const response = await axios.post('https://api.tigerex.com/orders', orderData, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                return response.data;
            } catch (error) {
                return { error: error.message };
            }
        });

        ipcMain.handle('getUserOrders', async (event, status) => {
            try {
                const token = this.decrypt(store.get('access_token'));
                const response = await axios.get(`https://api.tigerex.com/orders?status=${status}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                return response.data;
            } catch (error) {
                return { error: error.message };
            }
        });

        // Portfolio handlers
        ipcMain.handle('getPortfolio', async () => {
            try {
                const token = this.decrypt(store.get('access_token'));
                const response = await axios.get('https://api.tigerex.com/portfolio', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                return response.data;
            } catch (error) {
                return { error: error.message };
            }
        });

        // Settings handlers
        ipcMain.handle('getSettings', async () => {
            return store.get('settings', {
                theme: 'dark',
                notifications: true,
                autoStart: false,
                language: 'en',
                tradingPairs: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
            });
        });

        ipcMain.handle('saveSettings', async (event, settings) => {
            store.set('settings', settings);
            return { success: true };
        });

        // System handlers
        ipcMain.handle('getSystemInfo', async () => {
            return {
                platform: process.platform,
                arch: process.arch,
                electronVersion: process.versions.electron,
                nodeVersion: process.versions.node,
                chromeVersion: process.versions.chrome,
                appVersion: app.getVersion()
            };
        });

        ipcMain.handle('minimizeWindow', () => {
            if (this.mainWindow) {
                this.mainWindow.minimize();
            }
        });

        ipcMain.handle('maximizeWindow', () => {
            if (this.mainWindow) {
                if (this.mainWindow.isMaximized()) {
                    this.mainWindow.unmaximize();
                } else {
                    this.mainWindow.maximize();
                }
            }
        });

        ipcMain.handle('closeWindow', () => {
            if (this.mainWindow) {
                this.mainWindow.close();
            }
        });

        ipcMain.handle('openTradingWindow', () => {
            if (!this.tradingWindow) {
                this.createTradingWindow();
            } else {
                this.tradingWindow.focus();
            }
        });

        ipcMain.handle('openSettingsWindow', () => {
            if (!this.settingsWindow) {
                this.createSettingsWindow();
            } else {
                this.settingsWindow.focus();
            }
        });

        // Notification handlers
        ipcMain.handle('showNotification', (event, options) => {
            const { title, body, icon } = options;
            
            // Show native notification
            if (Notification.isSupported()) {
                const notification = new Notification({
                    title,
                    body,
                    icon: icon ? path.join(__dirname, 'assets', icon) : undefined,
                    urgency: 'normal'
                });
                
                notification.on('click', () => {
                    if (this.mainWindow) {
                        this.mainWindow.focus();
                    }
                });
                
                notification.show();
            }
        });
    }

    encrypt(text) {
        const algorithm = 'aes-256-gcm';
        const secretKey = crypto.scryptSync('tigerex-desktop-key', 'salt', 32);
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipher(algorithm, secretKey, iv);
        
        let encrypted = cipher.update(text, 'utf8', 'hex');
        encrypted += cipher.final('hex');
        
        const authTag = cipher.getAuthTag();
        return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
    }

    decrypt(encryptedText) {
        const algorithm = 'aes-256-gcm';
        const secretKey = crypto.scryptSync('tigerex-desktop-key', 'salt', 32);
        
        const parts = encryptedText.split(':');
        const iv = Buffer.from(parts[0], 'hex');
        const authTag = Buffer.from(parts[1], 'hex');
        const encrypted = parts[2];
        
        const decipher = crypto.createDecipher(algorithm, secretKey, iv);
        decipher.setAuthTag(authTag);
        
        let decrypted = decipher.update(encrypted, 'hex', 'utf8');
        decrypted += decipher.final('utf8');
        
        return decrypted;
    }
}

// Application initialization
const tigerExApp = new TigerExDesktopApp();

app.whenReady().then(() => {
    tigerExApp.createMainWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            tigerExApp.createMainWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Security: Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
    app.quit();
} else {
    app.on('second-instance', () => {
        // Someone tried to run a second instance, we should focus our window
        if (tigerExApp.mainWindow) {
            if (tigerExApp.mainWindow.isMinimized()) tigerExApp.mainWindow.restore();
            tigerExApp.mainWindow.focus();
        }
    });
}

// Auto-updater configuration (for production)
if (!tigerExApp.isDevelopment) {
    const { autoUpdater } = require('electron-updater');
    
    autoUpdater.checkForUpdatesAndNotify();
    
    autoUpdater.on('update-downloaded', () => {
        dialog.showMessageBox(tigerExApp.mainWindow, {
            type: 'info',
            title: 'Update Available',
            message: 'A new version of TigerEx is available. Restart to apply updates.',
            buttons: ['Restart Now', 'Later']
        }).then((result) => {
            if (result.response === 0) {
                autoUpdater.quitAndInstall();
            }
        });
    });
}

module.exports = TigerExDesktopApp;