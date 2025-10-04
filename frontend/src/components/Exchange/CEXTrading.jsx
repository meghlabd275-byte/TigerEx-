import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Select, Input, Button, Table, Tabs, Progress, Statistic } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const { Option } = Select;
const { TabPane } = Tabs;

const CEXTrading = ({ selectedPair, setSelectedPair, orderBook, recentTrades, userOrders }) => {
  const [orderType, setOrderType] = useState('limit');
  const [side, setSide] = useState('buy');
  const [price, setPrice] = useState('');
  const [amount, setAmount] = useState('');
  const [balance, setBalance] = useState({ USDT: 10000, BTC: 0.5 });
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    // Generate mock chart data
    const mockChartData = [];
    const basePrice = 67000;
    for (let i = 0; i < 24; i++) {
      mockChartData.push({
        time: `${i}:00`,
        price: basePrice + (Math.random() - 0.5) * 1000
      });
    }
    setChartData(mockChartData);
  }, [selectedPair]);

  const handlePlaceOrder = () => {
    const orderValue = parseFloat(price) * parseFloat(amount);
    
    if (side === 'buy' && orderValue > balance.USDT) {
      message.error('Insufficient USDT balance');
      return;
    }
    
    if (side === 'sell' && parseFloat(amount) > balance.BTC) {
      message.error('Insufficient BTC balance');
      return;
    }

    // Place order logic here
    console.log('Placing order:', { side, orderType, price, amount });
    message.success('Order placed successfully');
  };

  const orderBookData = [...orderBook.asks.reverse(), ...orderBook.bids];

  const orderBookColumns = [
    {
      title: 'Price (USDT)',
      dataIndex: 'price',
      key: 'price',
      render: (price, record, index) => {
        const isAsk = index < orderBook.asks.length;
        return (
          <span 
            className={isAsk ? 'ask-price' : 'bid-price'}
            onClick={() => setPrice(price.toString())}
            style={{ cursor: 'pointer' }}
          >
            {price.toFixed(2)}
          </span>
        );
      }
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

  const userOrdersColumns = [
    {
      title: 'Pair',
      dataIndex: 'pair',
      key: 'pair'
    },
    {
      title: 'Side',
      dataIndex: 'side',
      key: 'side',
      render: (side) => (
        <span className={side === 'buy' ? 'buy-side' : 'sell-side'}>
          {side.toUpperCase()}
        </span>
      )
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type'
    },
    {
      title: 'Amount',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount) => amount.toFixed(4)
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      render: (price) => price.toFixed(2)
    },
    {
      title: 'Filled',
      dataIndex: 'filled',
      key: 'filled',
      render: (filled, record) => (
        <div>
          <Progress 
            percent={(filled / record.amount) * 100} 
            size="small" 
            showInfo={false}
          />
          <span>{filled.toFixed(4)}</span>
        </div>
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <span className={`status-${status}`}>
          {status.toUpperCase()}
        </span>
      )
    }
  ];

  return (
    <div className="cex-trading">
      <Row gutter={[16, 16]}>
        {/* Trading Pair Selector */}
        <Col span={24}>
          <Card>
            <div className="pair-selector">
              <Select
                value={selectedPair}
                onChange={setSelectedPair}
                style={{ width: 200, marginRight: 16 }}
                size="large"
              >
                <Option value="BTC/USDT">BTC/USDT</Option>
                <Option value="ETH/USDT">ETH/USDT</Option>
                <Option value="BNB/USDT">BNB/USDT</Option>
                <Option value="ADA/USDT">ADA/USDT</Option>
              </Select>
              
              <div className="pair-stats">
                <Statistic title="Last Price" value={67000.00} precision={2} />
                <Statistic title="24h Change" value={2.5} precision={2} suffix="%" valueStyle={{ color: '#52c41a' }} />
                <Statistic title="24h Volume" value={1234567.89} precision={2} />
              </div>
            </div>
          </Card>
        </Col>

        {/* Price Chart */}
        <Col span={16}>
          <Card title="Price Chart" className="chart-card">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={['dataMin - 500', 'dataMax + 500']} />
                <Tooltip />
                <Line type="monotone" dataKey="price" stroke="#1890ff" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Order Form */}
        <Col span={8}>
          <Card title="Place Order" className="order-form">
            <Tabs activeKey={side} onChange={setSide}>
              <TabPane tab="Buy" key="buy">
                <div className="order-inputs">
                  <Select
                    value={orderType}
                    onChange={setOrderType}
                    style={{ width: '100%', marginBottom: 16 }}
                  >
                    <Option value="limit">Limit Order</Option>
                    <Option value="market">Market Order</Option>
                    <Option value="stop">Stop Order</Option>
                  </Select>

                  {orderType !== 'market' && (
                    <Input
                      placeholder="Price (USDT)"
                      value={price}
                      onChange={(e) => setPrice(e.target.value)}
                      style={{ marginBottom: 16 }}
                    />
                  )}

                  <Input
                    placeholder="Amount (BTC)"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    style={{ marginBottom: 16 }}
                  />

                  <div className="balance-info">
                    <span>Available: {balance.USDT.toFixed(2)} USDT</span>
                  </div>

                  <Button
                    type="primary"
                    size="large"
                    block
                    className="buy-button"
                    onClick={handlePlaceOrder}
                  >
                    Buy {selectedPair.split('/')[0]}
                  </Button>
                </div>
              </TabPane>

              <TabPane tab="Sell" key="sell">
                <div className="order-inputs">
                  <Select
                    value={orderType}
                    onChange={setOrderType}
                    style={{ width: '100%', marginBottom: 16 }}
                  >
                    <Option value="limit">Limit Order</Option>
                    <Option value="market">Market Order</Option>
                    <Option value="stop">Stop Order</Option>
                  </Select>

                  {orderType !== 'market' && (
                    <Input
                      placeholder="Price (USDT)"
                      value={price}
                      onChange={(e) => setPrice(e.target.value)}
                      style={{ marginBottom: 16 }}
                    />
                  )}

                  <Input
                    placeholder="Amount (BTC)"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    style={{ marginBottom: 16 }}
                  />

                  <div className="balance-info">
                    <span>Available: {balance.BTC.toFixed(4)} BTC</span>
                  </div>

                  <Button
                    type="primary"
                    size="large"
                    block
                    className="sell-button"
                    onClick={handlePlaceOrder}
                  >
                    Sell {selectedPair.split('/')[0]}
                  </Button>
                </div>
              </TabPane>
            </Tabs>
          </Card>
        </Col>

        {/* Order Book */}
        <Col span={8}>
          <Card title="Order Book" className="order-book">
            <Table
              dataSource={orderBookData}
              columns={orderBookColumns}
              pagination={false}
              size="small"
              scroll={{ y: 300 }}
            />
          </Card>
        </Col>

        {/* Recent Trades */}
        <Col span={8}>
          <Card title="Recent Trades" className="recent-trades">
            <Table
              dataSource={recentTrades}
              columns={tradesColumns}
              pagination={false}
              size="small"
              scroll={{ y: 300 }}
            />
          </Card>
        </Col>

        {/* User Orders */}
        <Col span={8}>
          <Card title="Open Orders" className="user-orders">
            <Table
              dataSource={userOrders}
              columns={userOrdersColumns}
              pagination={false}
              size="small"
              scroll={{ y: 300 }}
            />
          </Card>
        </Col>
      </Row>

      <style jsx>{`
        .cex-trading {
          width: 100%;
        }

        .pair-selector {
          display: flex;
          align-items: center;
          gap: 24px;
        }

        .pair-stats {
          display: flex;
          gap: 48px;
        }

        .chart-card .ant-card-body {
          padding: 16px;
        }

        .order-form {
          height: fit-content;
        }

        .order-inputs {
          padding: 16px 0;
        }

        .balance-info {
          margin-bottom: 16px;
          font-size: 12px;
          color: #666;
        }

        .buy-button {
          background: #52c41a;
          border-color: #52c41a;
        }

        .buy-button:hover {
          background: #73d13d;
          border-color: #73d13d;
        }

        .sell-button {
          background: #ff4d4f;
          border-color: #ff4d4f;
        }

        .sell-button:hover {
          background: #ff7875;
          border-color: #ff7875;
        }

        .ask-price {
          color: #ff4d4f;
          font-weight: 500;
        }

        .bid-price {
          color: #52c41a;
          font-weight: 500;
        }

        .buy-price {
          color: #52c41a;
        }

        .sell-price {
          color: #ff4d4f;
        }

        .buy-side {
          color: #52c41a;
          font-weight: 500;
        }

        .sell-side {
          color: #ff4d4f;
          font-weight: 500;
        }

        .status-partial {
          color: #faad14;
        }

        .status-filled {
          color: #52c41a;
        }

        .status-cancelled {
          color: #ff4d4f;
        }

        @media (max-width: 1200px) {
          .pair-stats {
            flex-direction: column;
            gap: 16px;
          }
        }

        @media (max-width: 768px) {
          .pair-selector {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
          }
        }
      `}</style>
    </div>
  );
};

export default CEXTrading;