/**
 * TigerEx Desktop Application - Preload Script
 * Exposes secure APIs to the renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Store operations
  store: {
    get: (key) => ipcRenderer.invoke('store-get', key),
    set: (key, value) => ipcRenderer.invoke('store-set', key, value),
    delete: (key) => ipcRenderer.invoke('store-delete', key)
  },

  // API requests
  api: {
    request: (method, endpoint, data, headers) => 
      ipcRenderer.invoke('api-request', { method, endpoint, data, headers })
  },

  // Navigation
  navigation: {
    onNavigate: (callback) => ipcRenderer.on('navigate', (event, route) => callback(route))
  },

  // External links
  openExternal: (url) => ipcRenderer.invoke('open-external', url),

  // Notifications
  showNotification: (title, body) => 
    ipcRenderer.invoke('show-notification', { title, body }),

  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),

  // Order dialog
  onOpenOrderDialog: (callback) => 
    ipcRenderer.on('open-order-dialog', () => callback())
});