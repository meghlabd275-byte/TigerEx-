/**
 * TigerEx Spot Trading - Node.js/Express Version
 * Complete spot trading functionality
 */

const express = require('express');
const router = express.Router();
const authMiddleware = require('../middleware/auth');
const tradingService = require('../services/trading');
const marketService = require('../services/market');

// Get spot markets
router.get('/markets', async (req, res) => {
    try {
        const markets = await marketService.getSpotMarkets();
        res.json({ success: true, data: markets });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get market prices
router.get('/prices', async (req, res) => {
    try {
        const prices = await marketService.getPrices();
        res.json({ success: true, data: prices });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Buy spot - requires authentication
router.post('/buy', authMiddleware.requireAuth, async (req, res) => {
    try {
        const { symbol, amount, price, orderType } = req.body;
        const userId = req.user.id;
        
        const order = await tradingService.placeSpotOrder({
            userId,
            symbol,
            side: 'buy',
            amount,
            price,
            orderType: orderType || 'market'
        });
        
        res.json({ success: true, order });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Sell spot - requires authentication
router.post('/sell', authMiddleware.requireAuth, async (req, res) => {
    try {
        const { symbol, amount, price, orderType } = req.body;
        const userId = req.user.id;
        
        const order = await tradingService.placeSpotOrder({
            userId,
            symbol,
            side: 'sell',
            amount,
            price,
            orderType: orderType || 'market'
        });
        
        res.json({ success: true, order });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Get user balance
router.get('/balance', authMiddleware.requireAuth, async (req, res) => {
    try {
        const balance = await tradingService.getBalance(req.user.id);
        res.json({ success: true, balance });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get order history
router.get('/orders', authMiddleware.requireAuth, async (req, res) => {
    try {
        const orders = await tradingService.getOrderHistory(req.user.id);
        res.json({ success: true, orders });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Cancel order
router.delete('/order/:id', authMiddleware.requireAuth, async (req, res) => {
    try {
        await tradingService.cancelOrder(req.params.id, req.user.id);
        res.json({ success: true });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

module.exports = router;