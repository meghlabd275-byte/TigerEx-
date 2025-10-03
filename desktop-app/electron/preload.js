/**
 * Security preload for desktop-app/electron
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Secure IPC communication
  send: (channel, data) => {
    const validChannels = ['new-order', 'navigate', 'trading-mode', 'open-tool', 'show-about'];
    if (validChannels.includes(channel)) {
      ipcRenderer.send(channel, data);
    }
  },
  
  receive: (channel, callback) => {
    const validChannels = ['new-order', 'navigate', 'trading-mode', 'open-tool', 'show-about'];
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (event, data) => callback(data));
    }
  },
  
  // Settings management
  saveSettings: (settings) => {
    ipcRenderer.send('save-settings', settings);
  },
  
  getSettings: () => {
    ipcRenderer.send('get-settings');
  },
  
  saveSession: (session) => {
    ipcRenderer.send('save-session', session);
  },
  
  getSession: () => {
    ipcRenderer.send('get-session');
  },
  
  clearSession: () => {
    ipcRenderer.send('clear-session');
  },
  
  openNewWindow: (route) => {
    ipcRenderer.send('open-new-window', route);
  },
  
  showNotification: (title, body) => {
    ipcRenderer.send('show-notification', { title, body });
  }
});

// Listen for responses
ipcRenderer.on('settings-saved', (event, data) => {
  window.postMessage({ type: 'settings-saved', data }, '*');
});

ipcRenderer.on('settings-loaded', (event, data) => {
  window.postMessage({ type: 'settings-loaded', data }, '*');
});

ipcRenderer.on('session-loaded', (event, data) => {
  window.postMessage({ type: 'session-loaded', data }, '*');
});

ipcRenderer.on('session-cleared', (event, data) => {
  window.postMessage({ type: 'session-cleared', data }, '*');
});