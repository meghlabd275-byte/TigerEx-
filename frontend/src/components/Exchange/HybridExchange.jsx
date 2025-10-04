import React, { useState, useEffect } from 'react';
import { Card, Tabs, Button, Select, Input, Table, Switch, message } from 'antd';
import { SwapOutlined, TradingViewOutlined, WalletOutlined } from '@ant-design/icons';
import CEXTrading from './CEXTrading';
import DEXTrading from './DEXTrading';

const { TabPane } = Tabs;
const { Option } = Select;

const HybridExchange = () => {
  const [exchangeMode, setExchangeMode] = useState('CEX'); // CEX or DEX
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [orderBook, setOrderBook] = useState({ bids: [], asks: [] });
  const [recentTrades, setRecentTrades] = useState([]);
  const [userOrders, setUserOrders] = useState([]);

  useEffect(() => {
    // Initialize exchange data
    fetchMarketData();
    fetchUserOrders();
  }, [exchangeMode, selectedPair]);

  const fetchMarketData = async () => {
    // Mock market data - in production, this would fetch from real APIs
    const mockOrderBook = {
      bids: [
        { price: 66950.00, amount: 0.5234, total: 35025.83 },
        { price: 66940.00, amount: 1.2341, total: 82634.75 },
        { price: 66930.00, amount: 0.8765, total: 58665.45 }
      ],
      asks: [
        { price: 67000.00, amount: 0.7543, total: 50538.10 },
        { price: 67010.00, amount: 1.1234, total: 75267.23 },
        { price: 67020.00, amount: 0.9876, total: 66198.67 }
      ]
    };

    const mockTrades = [
      { price: 66980.00, amount: 0.1234, time: '14:32:15', side: 'buy' },
      { price: 66975.00, amount: 0.5678, time: '14:32:10', side: 'sell' },
      { price: 66985.00, amount: 0.2345, time: '14:32:05', side: 'buy' }
    ];

    setOrderBook(mockOrderBook);
    setRecentTrades(mockTrades);
  };

  const fetchUserOrders = async () => {
    // Mock user orders
    const mockOrders = [
      {
        id: '1',
        pair: 'BTC/USDT',
        side: 'buy',
        type: 'limit',
        amount: 0.1,
        price: 66500.00,
        filled: 0.05,
        status: 'partial',
        time: '14:30:00'
      }
    ];
    setUserOrders(mockOrders);
  };

  const handleModeSwitch = (mode) => {
    setExchangeMode(mode);
    message.success(`Switched to ${mode} mode`);
  };

  const orderBookColumns = [
    {
      title: 'Price (USDT)',
      dataIndex: 'price',
      key: 'price',
      render: (price, record, index) => (
        <span className={index < 3 ? 'ask-price' : 'bid-price'}>
          {price.toFixed(2)}
        </span>
      )
    },
    {
      title: 'Amount (BTC)',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount) => amount.toFixed(4)
    },
    {
      title: 'Total (USDT)',
      dataIndex: 'total',
      key: 'total',
      render: (total) => total.toFixed(2)
    }
  ];

  const tradesColumns = [
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      render: (price, record) => (
        <span className={record.side === 'buy' ? 'buy-price' : 'sell-price'}>
          {price.toFixed(2)}
        </span>
      )
    },
    {
      title: 'Amount',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount) => amount.toFixed(4)
    },
    {
      title: 'Time',
      dataIndex: 'time',
      key: 'time'
    }
  ];

  return (
    <div className="hybrid-exchange">
      {/* Exchange Mode Selector */}
      <Card className="mode-selector">
        <div className="exchange-header">
          <h2>TigerEx Hybrid Exchange</h2>
          <div className="mode-switch">
            <Button
              type={exchangeMode === 'CEX' ? 'primary' : 'default'}
              icon={<TradingViewOutlined />}
              onClick={() => handleModeSwitch('CEX')}
            >
              CEX Trading
            </Button>
            <Button
              type={exchangeMode === 'DEX' ? 'primary' : 'default'}
              icon={<WalletOutlined />}
              onClick={() => handleModeSwitch('DEX')}
              style={{ marginLeft: 8 }}
            >
              DEX Wallet
            </Button>
          </div>
        </div>
        
        <div className="mode-description">
          {exchangeMode === 'CEX' ? (
            <p>🏛️ Centralized Exchange: High liquidity, advanced trading features, order matching</p>
          ) : (
            <p>🔗 Decentralized Exchange: Self-custody, blockchain transactions, DeFi integration</p>
          )}
        </div>
      </Card>

      {/* Trading Interface */}
      <div className="trading-interface">
        {exchangeMode === 'CEX' ? (
          <CEXTrading
            selectedPair={selectedPair}
            setSelectedPair={setSelectedPair}
            orderBook={orderBook}
            recentTrades={recentTrades}
            userOrders={userOrders}
          />
        ) : (
          <DEXTrading
            selectedPair={selectedPair}
            setSelectedPair={setSelectedPair}
          />
        )}
      </div>

      <style jsx>{`
        .hybrid-exchange {
          padding: 20px;
          max-width: 1400px;
          margin: 0 auto;
        }

        .mode-selector {
          margin-bottom: 20px;
        }

        .exchange-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .exchange-header h2 {
          margin: 0;
          color: #1890ff;
        }

        .mode-switch {
          display: flex;
          align-items: center;
        }

        .mode-description {
          padding: 12px;
          background: #f5f5f5;
          border-radius: 6px;
          margin-top: 16px;
        }

        .mode-description p {
          margin: 0;
          font-size: 14px;
          color: #666;
        }

        .trading-interface {
          min-height: 600px;
        }

        .ask-price {
          color: #ff4d4f;
        }

        .bid-price {
          color: #52c41a;
        }

        .buy-price {
          color: #52c41a;
        }

        .sell-price {
          color: #ff4d4f;
        }

        @media (max-width: 768px) {
          .hybrid-exchange {
            padding: 10px;
          }

          .exchange-header {
            flex-direction: column;
            gap: 16px;
          }

          .mode-switch {
            width: 100%;
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};

export default HybridExchange;