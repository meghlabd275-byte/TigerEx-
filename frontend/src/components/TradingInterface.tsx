'use client'

import React, { useState, useEffect } from 'react'
import { useWebSocket } from '@/contexts/WebSocketContext'

interface OrderBookEntry {
  price: string
  quantity: string
  total: string
}

interface TradingInterfaceProps {
  symbol?: string
}

export const TradingInterface: React.FC<TradingInterfaceProps> = ({ symbol = 'BTC/USDT' }) => {
  const [orderType, setOrderType] = useState<'market' | 'limit'>('limit')
  const [side, setSide] = useState<'buy' | 'sell'>('buy')
  const [price, setPrice] = useState('')
  const [quantity, setQuantity] = useState('')
  const [total, setTotal] = useState('')
  const [bids, setBids] = useState<OrderBookEntry[]>([])
  const [asks, setAsks] = useState<OrderBookEntry[]>([])
  const [currentPrice, setCurrentPrice] = useState('0')
  
  const { subscribeToSymbol, sendOrder } = useWebSocket()

  useEffect(() => {
    subscribeToSymbol(symbol)
    // Simulate order book data
    const mockBids: OrderBookEntry[] = [
      { price: '43250.00', quantity: '0.1234', total: '5335.85' },
      { price: '43249.50', quantity: '0.5678', total: '24562.23' },
      { price: '43249.00', quantity: '1.2345', total: '53370.32' },
    ]
    const mockAsks: OrderBookEntry[] = [
      { price: '43250.50', quantity: '0.2345', total: '10141.83' },
      { price: '43251.00', quantity: '0.8901', total: '38494.59' },
      { price: '43251.50', quantity: '2.3456', total: '101460.48' },
    ]
    setBids(mockBids)
    setAsks(mockAsks)
    setCurrentPrice('43250.25')
  }, [symbol, subscribeToSymbol])

  useEffect(() => {
    // Calculate total when price or quantity changes
    if (price && quantity) {
      const calculatedTotal = parseFloat(price) * parseFloat(quantity)
      setTotal(calculatedTotal.toFixed(2))
    } else {
      setTotal('')
    }
  }, [price, quantity])

  const handleSubmitOrder = () => {
    if (!quantity || (orderType === 'limit' && !price)) {
      alert('Please fill in all required fields')
      return
    }

    const order = {
      symbol,
      side,
      type: orderType,
      quantity: parseFloat(quantity),
      price: orderType === 'limit' ? parseFloat(price) : undefined
    }

    sendOrder(order)
    
    // Clear form
    setPrice('')
    setQuantity('')
    setTotal('')
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          {symbol} Trading
        </h2>
        <span className="text-2xl font-bold text-green-600 dark:text-green-400">
          ${currentPrice}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Form */}
        <div className="lg:col-span-1">
          <div className="space-y-4">
            {/* Order Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Order Type
              </label>
              <div className="flex space-x-2">
                <button
                  onClick={() => setOrderType('limit')}
                  className={`flex-1 py-2 px-4 rounded ${
                    orderType === 'limit'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  Limit
                </button>
                <button
                  onClick={() => setOrderType('market')}
                  className={`flex-1 py-2 px-4 rounded ${
                    orderType === 'market'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  Market
                </button>
              </div>
            </div>

            {/* Buy/Sell */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Side
              </label>
              <div className="flex space-x-2">
                <button
                  onClick={() => setSide('buy')}
                  className={`flex-1 py-2 px-4 rounded ${
                    side === 'buy'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  Buy
                </button>
                <button
                  onClick={() => setSide('sell')}
                  className={`flex-1 py-2 px-4 rounded ${
                    side === 'sell'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  Sell
                </button>
              </div>
            </div>

            {/* Price */}
            {orderType === 'limit' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Price (USDT)
                </label>
                <input
                  type="number"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="0.00"
                  step="0.01"
                />
              </div>
            )}

            {/* Quantity */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Quantity (BTC)
              </label>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="0.00"
                step="0.0001"
              />
            </div>

            {/* Total */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Total (USDT)
              </label>
              <input
                type="text"
                value={total}
                readOnly
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-100 dark:bg-gray-600 text-gray-900 dark:text-white"
                placeholder="0.00"
              />
            </div>

            {/* Submit Button */}
            <button
              onClick={handleSubmitOrder}
              className={`w-full py-3 px-4 rounded font-semibold transition duration-200 ${
                side === 'buy'
                  ? 'bg-green-600 hover:bg-green-700 text-white'
                  : 'bg-red-600 hover:bg-red-700 text-white'
              }`}
            >
              {side === 'buy' ? 'Buy' : 'Sell'} {symbol.split('/')[0]}
            </button>
          </div>
        </div>

        {/* Order Book */}
        <div className="lg:col-span-2">
          <div className="grid grid-cols-2 gap-4">
            {/* Bids */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Bids
              </h3>
              <div className="space-y-1">
                <div className="grid grid-cols-3 text-xs text-gray-600 dark:text-gray-400 pb-2 border-b border-gray-200 dark:border-gray-600">
                  <span>Price</span>
                  <span className="text-right">Quantity</span>
                  <span className="text-right">Total</span>
                </div>
                {bids.map((bid, index) => (
                  <div key={index} className="grid grid-cols-3 text-sm">
                    <span className="text-green-600 dark:text-green-400">{bid.price}</span>
                    <span className="text-right text-gray-600 dark:text-gray-300">{bid.quantity}</span>
                    <span className="text-right text-gray-600 dark:text-gray-300">{bid.total}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Asks */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Asks
              </h3>
              <div className="space-y-1">
                <div className="grid grid-cols-3 text-xs text-gray-600 dark:text-gray-400 pb-2 border-b border-gray-200 dark:border-gray-600">
                  <span>Price</span>
                  <span className="text-right">Quantity</span>
                  <span className="text-right">Total</span>
                </div>
                {asks.map((ask, index) => (
                  <div key={index} className="grid grid-cols-3 text-sm">
                    <span className="text-red-600 dark:text-red-400">{ask.price}</span>
                    <span className="text-right text-gray-600 dark:text-gray-300">{ask.quantity}</span>
                    <span className="text-right text-gray-600 dark:text-gray-300">{ask.total}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}