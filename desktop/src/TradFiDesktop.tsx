/**
 * TigerEx TradFi Desktop Trading Application
 * CFD, Forex, ETF, Derivatives Trading
 */

import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area 
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Globe, Activity, Settings,
  Wallet, Clock, Shield, Zap, Layers, CreditCard
} from 'lucide-react';

// TradFi Types
const INSTRUMENT_TYPES = {
  CFD: { name: 'CFD', color: '#f59e0b' },
  FOREX: { name: 'Forex', color: '#8b5cf6' },
  ETF: { name: 'ETF', color: '#10b981' },
  STOCK_TOKEN: { name: 'Stock', color: '#3b82f6' },
  DERIVATIVE: { name: 'Derivative', color: '#ec4899' },
  OPTION: { name: 'Option', color: '#06b6d4' },
  FUTURE: { name: 'Future', color: '#f97316' },
};

const TRADFI_INSTRUMENTS = [
  { symbol: 'BTC/USD', name: 'Bitcoin', type: 'CFD', price: 42500.00, change: 2.34, leverage: 100 },
  { symbol: 'ETH/USD', name: 'Ethereum', type: 'CFD', price: 2280.00, change: 1.56, leverage: 50 },
  { symbol: 'EUR/USD', name: 'Euro/Dollar', type: 'FOREX', price: 1.0845, change: 0.12, leverage: 30 },
  { symbol: 'GBP/USD', name: 'British Pound', type: 'FOREX', price: 1.2650, change: -0.08, leverage: 30 },
  { symbol: 'AAPL', name: 'Apple Inc', type: 'STOCK_TOKEN', price: 178.50, change: 1.23, leverage: 20 },
  { symbol: 'TSLA', name: 'Tesla Inc', type: 'STOCK_TOKEN', price: 245.20, change: -2.45, leverage: 20 },
  { symbol: 'SPY', name: 'S&P 500 ETF', type: 'ETF', price: 478.50, change: 0.45, leverage: 10 },
  { symbol: 'QQQ', name: 'Nasdaq ETF', type: 'ETF', price: 405.20, change: 0.78, leverage: 10 },
  { symbol: 'GLD', name: 'Gold ETF', type: 'ETF', price: 185.30, change: 0.34, leverage: 10 },
  { symbol: 'GOOGL', name: 'Alphabet', type: 'STOCK_TOKEN', price: 142.80, change: 0.89, leverage: 20 },
  { symbol: 'NVDA', name: 'NVIDIA', type: 'STOCK_TOKEN', price: 545.80, change: 3.45, leverage: 20 },
  { symbol: 'MSFT', name: 'Microsoft', type: 'STOCK_TOKEN', price: 378.50, change: 1.12, leverage: 20 },
  { symbol: 'META', name: 'Meta', type: 'STOCK_TOKEN', price: 378.20, change: 2.10, leverage: 20 },
  { symbol: 'AMZN', name: 'Amazon', type: 'STOCK_TOKEN', price: 155.30, change: 1.45, leverage: 20 },
  { symbol: 'XAU/USD', name: 'Gold', type: 'DERIVATIVE', price: 2025.50, change: 0.56, leverage: 100 },
  { symbol: 'XAG/USD', name: 'Silver', type: 'DERIVATIVE', price: 22.85, change: 1.23, leverage: 50 },
];

function generateChartData(basePrice) {
  const data = [];
  let price = basePrice * 0.98;
  for (let i = 0; i < 100; i++) {
    price = price * (1 + (Math.random() - 0.5) * 0.01);
    data.push({ time: i, price });
  }
  return data;
}

function TradFiDesktop() {
  const [selectedInstrument, setSelectedInstrument] = useState(TRADFI_INSTRUMENTS[0]);
  const [orderSide, setOrderSide] = useState('buy');
  const [orderType, setOrderType] = useState('market');
  const [quantity, setQuantity] = useState(1);
  const [leverage, setLeverage] = useState(1);
  const [stopLoss, setStopLoss] = useState('');
  const [takeProfit, setTakeProfit] = useState('');
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    setChartData(generateChartData(selectedInstrument.price));
  }, [selectedInstrument]);

  const orderValue = selectedInstrument.price * quantity * leverage;
  const margin = orderValue / leverage;
  const fee = orderValue * 0.001;
  const positionPnL = orderValue * 0.15 * (orderSide === 'buy' ? 1 : -1);

  const handleOpenPosition = () => {
    alert(`Position opened: ${orderSide.toUpperCase()} ${quantity} ${selectedInstrument.symbol} @ ${selectedInstrument.price}`);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#0f172a', color: 'white' }}>
      {/* Left Sidebar - Instruments */}
      <div style={{ width: 300, backgroundColor: '#1e293b', padding: 16, overflowY: 'auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
          <Globe size={32} color="#f59e0b" />
          <div>
            <div style={{ fontSize: 20, fontWeight: 'bold' }}>TigerEx TradFi</div>
            <div style={{ color: '#94a3b8', fontSize: 12 }}>CFD, Forex, ETF Trading</div>
          </div>
        </div>

        <input 
          type="text" 
          placeholder="Search instruments..." 
          style={{ 
            width: '100%', 
            padding: '12px', 
            backgroundColor: '#334155', 
            border: 'none', 
            borderRadius: 8,
            color: 'white',
            marginBottom: 16
          }}
        />

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
          {Object.entries(INSTRUMENT_TYPES).map(([type, info]) => (
            <button
              key={type}
              style={{ 
                padding: '6px 12px', 
                backgroundColor: '#334155', 
                border: 'none', 
                borderRadius: 4,
                color: 'white',
                cursor: 'pointer',
                fontSize: 12
              }}
            >
              {info.name}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {TRADFI_INSTRUMENTS.map(inst => (
            <div
              key={inst.symbol}
              onClick={() => setSelectedInstrument(inst)}
              style={{ 
                padding: 12, 
                backgroundColor: selectedInstrument.symbol === inst.symbol ? '#334155' : '#1e293b',
                borderRadius: 8,
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ fontWeight: 'bold' }}>{inst.symbol}</div>
                <div style={{ color: '#94a3b8', fontSize: 12 }}>{inst.name}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div>${inst.price.toLocaleString()}</div>
                <div style={{ color: inst.change >= 0 ? '#10b981' : '#ef4444', fontSize: 12 }}>
                  {inst.change >= 0 ? '+' : ''}{inst.change}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Area */}
      <div style={{ flex: 1, padding: 24, overflowY: 'auto' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
          <div>
            <div style={{ fontSize: 14, color: '#94a3b8' }}>{INSTRUMENT_TYPES[selectedInstrument.type]?.name}</div>
            <div style={{ fontSize: 32, fontWeight: 'bold' }}>{selectedInstrument.symbol}</div>
            <div style={{ color: '#94a3b8' }}>{selectedInstrument.name}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 32, fontWeight: 'bold' }}>${selectedInstrument.price.toLocaleString()}</div>
            <div style={{ color: selectedInstrument.change >= 0 ? '#10b981' : '#ef4444' }}>
              {selectedInstrument.change >= 0 ? '+' : ''}{selectedInstrument.change}%
            </div>
          </div>
        </div>

        {/* Chart */}
        <div style={{ backgroundColor: '#1e293b', borderRadius: 12, padding: 24, marginBottom: 24, height: 400 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" stroke="#64748b" />
              <YAxis domain={['auto', 'auto']} stroke="#64748b" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: 'none' }}
                labelStyle={{ color: '#94a3b8' }}
              />
              <Area 
                type="monotone" 
                dataKey="price" 
                stroke="#f59e0b" 
                fillOpacity={1} 
                fill="url(#colorPrice)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Order Form */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          <div style={{ backgroundColor: '#1e293b', borderRadius: 12, padding: 24 }}>
            <div style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 16 }}>Open Position</div>
            
            {/* Buy/Sell */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
              <button
                onClick={() => setOrderSide('buy')}
                style={{ 
                  flex: 1, 
                  padding: '16px', 
                  backgroundColor: orderSide === 'buy' ? '#10b981' : '#334155',
                  border: 'none',
                  borderRadius: 8,
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: 16,
                  cursor: 'pointer'
                }}
              >
                BUY
              </button>
              <button
                onClick={() => setOrderSide('sell')}
                style={{ 
                  flex: 1, 
                  padding: '16px', 
                  backgroundColor: orderSide === 'sell' ? '#ef4444' : '#334155',
                  border: 'none',
                  borderRadius: 8,
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: 16,
                  cursor: 'pointer'
                }}
              >
                SELL
              </button>
            </div>

            {/* Order Type */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
              {['market', 'limit', 'stop', 'oco'].map(type => (
                <button
                  key={type}
                  onClick={() => setOrderType(type)}
                  style={{ 
                    flex: 1,
                    padding: '12px', 
                    backgroundColor: orderType === type ? '#f59e0b' : '#334155',
                    border: 'none',
                    borderRadius: 8,
                    color: orderType === type ? 'black' : 'white',
                    cursor: 'pointer',
                    textTransform: 'capitalize'
                  }}
                >
                  {type}
                </button>
              ))}
            </div>

            {/* Quantity & Leverage */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
              <div>
                <div style={{ color: '#94a3b8', fontSize: 14, marginBottom: 8 }}>Quantity</div>
                <input 
                  type="number"
                  value={quantity}
                  onChange={e => setQuantity(Number(e.target.value))}
                  style={{ 
                    width: '100%', 
                    padding: '12px', 
                    backgroundColor: '#334155', 
                    border: 'none', 
                    borderRadius: 8,
                    color: 'white',
                    fontSize: 16
                  }}
                />
              </div>
              <div>
                <div style={{ color: '#94a3b8', fontSize: 14, marginBottom: 8 }}>Leverage</div>
                <select 
                  value={leverage}
                  onChange={e => setLeverage(Number(e.target.value))}
                  style={{ 
                    width: '100%', 
                    padding: '12px', 
                    backgroundColor: '#334155', 
                    border: 'none', 
                    borderRadius: 8,
                    color: 'white',
                    fontSize: 16
                  }}
                >
                  {[1, 2, 5, 10, 20, 50, 100].map(l => (
                    <option key={l} value={l}>{l}x</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Stop Loss & Take Profit */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
              <div>
                <div style={{ color: '#94a3b8', fontSize: 14, marginBottom: 8 }}>Stop Loss</div>
                <input 
                  type="number"
                  value={stopLoss}
                  onChange={e => setStopLoss(e.target.value)}
                  placeholder="0.00"
                  style={{ 
                    width: '100%', 
                    padding: '12px', 
                    backgroundColor: '#334155', 
                    border: 'none', 
                    borderRadius: 8,
                    color: 'white'
                  }}
                />
              </div>
              <div>
                <div style={{ color: '#94a3b8', fontSize: 14, marginBottom: 8 }}>Take Profit</div>
                <input 
                  type="number"
                  value={takeProfit}
                  onChange={e => setTakeProfit(e.target.value)}
                  placeholder="0.00"
                  style={{ 
                    width: '100%', 
                    padding: '12px', 
                    backgroundColor: '#334155', 
                    border: 'none', 
                    borderRadius: 8,
                    color: 'white'
                  }}
                />
              </div>
            </div>

            {/* Summary */}
            <div style={{ backgroundColor: '#334155', borderRadius: 8, padding: 16, marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ color: '#94a3b8' }}>Order Value</span>
                <span>${orderValue.toLocaleString()}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ color: '#94a3b8' }}>Margin</span>
                <span>${margin.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ color: '#94a3b8' }}>Fee (0.1%)</span>
                <span>${fee.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Max P&L</span>
                <span style={{ color: orderSide === 'buy' ? '#10b981' : '#ef4444' }}>
                  ${(orderValue * 0.3).toLocaleString()}
                </span>
              </div>
            </div>

            {/* Submit */}
            <button
              onClick={handleOpenPosition}
              style={{ 
                width: '100%', 
                padding: '16px', 
                backgroundColor: orderSide === 'buy' ? '#10b981' : '#ef4444',
                border: 'none',
                borderRadius: 8,
                color: 'white',
                fontWeight: 'bold',
                fontSize: 18,
                cursor: 'pointer'
              }}
            >
              {orderSide.toUpperCase()} {selectedInstrument.symbol}
            </button>
          </div>

          {/* Info Panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Instrument Info */}
            <div style={{ backgroundColor: '#1e293b', borderRadius: 12, padding: 24 }}>
              <div style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 16 }}>Instrument Info</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Type</span>
                  <span>{INSTRUMENT_TYPES[selectedInstrument.type]?.name}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Max Leverage</span>
                  <span>{selectedInstrument.leverage}x</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Trading Hours</span>
                  <span>24/7</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Maker Fee</span>
                  <span>0.01%</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Taker Fee</span>
                  <span>0.02%</span>
                </div>
              </div>
            </div>

            {/* Account */}
            <div style={{ backgroundColor: '#1e293b', borderRadius: 12, padding: 24 }}>
              <div style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 16 }}>Account</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Equity</span>
                  <span>$10,000.00</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Available</span>
                  <span>$8,500.00</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Margin Used</span>
                  <span>$1,500.00</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Unrealized P&L</span>
                  <span style={{ color: '#10b981' }}>+$250.00</span>
                </div>
              </div>
            </div>

            {/* Warning */}
            <div style={{ 
              backgroundColor: 'rgba(245, 158, 11, 0.1)', 
              border: '1px solid rgba(245, 158, 11, 0.3)', 
              borderRadius: 12, 
              padding: 16,
              display: 'flex',
              gap: 12
            }}>
              <Shield size={24} color="#f59e0b" />
              <div>
                <div style={{ fontWeight: 'bold', color: '#f59e0b', marginBottom: 4 }}>Leverage Warning</div>
                <div style={{ color: '#94a3b8', fontSize: 14 }}>
                  Higher leverage increases both profits and losses. Trade responsibly.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TradFiDesktop;