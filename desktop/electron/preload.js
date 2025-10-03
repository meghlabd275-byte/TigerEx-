/**
 * Security preload for desktop/electron
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Secure IPC communication
  send: (channel, data) => {
    const validChannels = ['new-order', 'navigate', 'trading-mode'];
    if (validChannels.includes(channel)) {
      ipcRenderer.send(channel, data);
    }
  },
  
  receive: (channel, callback) => {
    const validChannels = ['new-order', 'navigate', 'trading-mode'];
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (event, data) => callback(data));
    }
  }
});