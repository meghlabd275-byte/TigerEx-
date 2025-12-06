/**
 * TigerEx Unified Admin Panel - FastAPI Migration Bridge
 * This file provides backward compatibility while using the enhanced FastAPI backend
 */

const express = require('express');
const cors = require('cors');
const httpProxy = require('http-proxy-middleware');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// FastAPI backend proxy
const apiProxy = httpProxy.createProxyMiddleware({
  target: 'http://localhost:4001',
  changeOrigin: true,
  pathRewrite: {
    '^/api': '/api',
  },
});

// Proxy all API requests to FastAPI backend
app.use('/api', apiProxy);

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'unified-admin-panel-proxy',
    backend: 'fastapi',
    message: 'Proxying to enhanced FastAPI backend'
  });
});

// Serve static files for admin UI
app.use(express.static('public'));

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`TigerEx Unified Admin Panel Proxy running on port ${PORT}`);
  console.log(`FastAPI backend should be running on port 4001`);
});

module.exports = app;