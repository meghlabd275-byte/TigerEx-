import React, { useState } from 'react';
import api from '../services/api';

const TradingForm = ({ symbol }) => {
    const [side, setSide] = useState('buy');
    const [orderType, setOrderType] = useState('market');
    const [quantity, setQuantity] = useState('');
    const [price, setPrice] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        if (!quantity) {
            setError('Quantity is required');
            return;
        }

        if (orderType === 'limit' && !price) {
            setError('Price is required for limit orders');
            return;
        }

        try {
            const orderData = {
                symbol,
                side,
                order_type: orderType,
                quantity: parseFloat(quantity),
                price: orderType === 'limit' ? parseFloat(price) : null,
                stop_price: (orderType === 'stop_loss' || orderType === 'take_profit') ? parseFloat(price) : null,
            };

            const response = await api.post('/orders', orderData);
            setSuccess(`Order placed successfully! Order ID: ${response.data.order_id}`);
            setQuantity('');
            setPrice('');
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred while placing the order');
        }
    };

    return (
        <div className="trading-form">
            <h3>Place Order</h3>
            {error && <div className="error">{error}</div>}
            {success && <div className="success">{success}</div>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Side:</label>
                    <select value={side} onChange={(e) => setSide(e.target.value)}>
                        <option value="buy">Buy</option>
                        <option value="sell">Sell</option>
                    </select>
                </div>
                <div>
                    <label>Order Type:</label>
                    <select value={orderType} onChange={(e) => setOrderType(e.target.value)}>
                        <option value="market">Market</option>
                        <option value="limit">Limit</option>
                        <option value="stop_loss">Stop-Loss</option>
                        <option value="take_profit">Take-Profit</option>
                    </select>
                </div>
                <div>
                    <label>Quantity:</label>
                    <input
                        type="number"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        placeholder="0.00"
                    />
                </div>
                {orderType === 'limit' && (
                    <div>
                        <label>Price:</label>
                        <input
                            type="number"
                            value={price}
                            onChange={(e) => setPrice(e.target.value)}
                            placeholder="0.00"
                        />
                    </div>
                )}
                {(orderType === 'stop_loss' || orderType === 'take_profit') && (
                    <div>
                        <label>Stop Price:</label>
                        <input
                            type="number"
                            value={price}
                            onChange={(e) => setPrice(e.target.value)}
                            placeholder="0.00"
                        />
                    </div>
                )}
                <button type="submit">Place {side === 'buy' ? 'Buy' : 'Sell'} Order</button>
            </form>
        </div>
    );
};

export default TradingForm;
