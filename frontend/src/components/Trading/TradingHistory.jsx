/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

import React, { useState, useEffect } from 'react';
import { Card, Tabs, Table, Select, Button, Tag, DatePicker, Space } from 'antd';
import { FilterOutlined, DownloadOutlined } from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';

const { TabPane } = Tabs;
const { Option } = Select;
const { RangePicker } = DatePicker;

const TradingHistory = () => {
  const [activeTab, setActiveTab] = useState('order_history');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    asset: null,
    type: null,
    dateRange: null
  });

  useEffect(() => {
    fetchData();
  }, [activeTab, filters]);

  const fetchData = async () => {
    setLoading(true);
    try {
      let endpoint = '';
      switch (activeTab) {
        case 'order_history':
          endpoint = '/api/trading-history/order-history';
          break;
        case 'position_history':
          endpoint = '/api/trading-history/position-history';
          break;
        case 'trade_history':
          endpoint = '/api/trading-history/trade-history';
          break;
        case 'transaction_history':
          endpoint = '/api/trading-history/transaction-history';
          break;
        case 'funding_fee':
          endpoint = '/api/trading-history/funding-fee';
          break;
        default:
          endpoint = '/api/trading-history/order-history';
      }

      const params = {};
      if (filters.asset) params.asset = filters.asset;
      if (filters.type) params.type_filter = filters.type;

      const response = await axios.get(endpoint, { params });
      
      const dataKey = {
        'order_history': 'orders',
        'position_history': 'positions',
        'trade_history': 'trades',
        'transaction_history': 'transactions',
        'funding_fee': 'funding_fees'
      }[activeTab];

      setData(response.data[dataKey] || []);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  const getColumns = () => {
    switch (activeTab) {
      case 'order_history':
        return [
          {
            title: 'Symbol',
            dataIndex: 'symbol',
            key: 'symbol',
            render: (text) => <span className="symbol">{text}</span>
          },
          {
            title: 'Type',
            dataIndex: 'type',
            key: 'type',
            render: (text) => <Tag color="blue">{text.toUpperCase()}</Tag>
          },
          {
            title: 'Side',
            dataIndex: 'side',
            key: 'side',
            render: (text) => (
              <Tag color={text === 'buy' ? 'green' : 'red'}>
                {text.toUpperCase()}
              </Tag>
            )
          },
          {
            title: 'Amount',
            dataIndex: 'amount',
            key: 'amount',
            render: (text) => text.toFixed(8)
          },
          {
            title: 'Price',
            dataIndex: 'price',
            key: 'price',
            render: (text) => text.toFixed(2)
          },
          {
            title: 'Filled',
            dataIndex: 'filled',
            key: 'filled',
            render: (text) => `${text.toFixed(8)}`
          },
          {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (text) => {
              const color = {
                'filled': 'green',
                'partial': 'orange',
                'cancelled': 'red',
                'pending': 'blue'
              }[text] || 'default';
              return <Tag color={color}>{text.toUpperCase()}</Tag>;
            }
          },
          {
            title: 'Time',
            dataIndex: 'timestamp',
            key: 'timestamp',
            render: (text) => moment(text).format('YYYY-MM-DD HH:mm:ss')
          }
        ];

      case 'position_history':
        return [
          {
            title: 'Symbol',
            dataIndex: 'symbol',
            key: 'symbol'
          },
          {
            title: 'Side',
            dataIndex: 'side',
            key: 'side',
            render: (text) => (
              <Tag color={text === 'long' ? 'green' : 'red'}>
                {text.toUpperCase()}
              </Tag>
            )
          },
          {
            title: 'Entry Price',
            dataIndex: 'entry_price',
            key: 'entry_price',
            render: (text) => text.toFixed(2)
          },
          {
            title: 'Close Price',
            dataIndex: 'close_price',
            key: 'close_price',
            render: (text) => text.toFixed(2)
          },
          {
            title: 'Amount',
            dataIndex: 'amount',
            key: 'amount',
            render: (text) => text.toFixed(8)
          },
          {
            title: 'PNL',
            dataIndex: 'pnl',
            key: 'pnl',
            render: (text) => (
              <span className={text >= 0 ? 'profit' : 'loss'}>
                {text >= 0 ? '+' : ''}{text.toFixed(2)} USDT
              </span>
            )
          },
          {
            title: 'Time',
            dataIndex: 'timestamp',
            key: 'timestamp',
            render: (text) => moment(text).format('YYYY-MM-DD HH:mm:ss')
          }
        ];

      case 'funding_fee':
        return [
          {
            title: 'Asset',
            dataIndex: 'asset',
            key: 'asset',
            render: (text) => <span className="asset">{text}</span>
          },
          {
            title: 'Type',
            dataIndex: 'type',
            key: 'type',
            render: (text) => <span className="fee-type">{text}</span>
          },
          {
            title: 'Symbol',
            dataIndex: 'symbol',
            key: 'symbol',
            render: (text) => <span className="symbol">{text}</span>
          },
          {
            title: 'Amount',
            dataIndex: 'amount',
            key: 'amount',
            render: (text) => (
              <span className={text >= 0 ? 'profit' : 'loss'}>
                {text.toFixed(8)}
              </span>
            )
          },
          {
            title: 'Time',
            dataIndex: 'timestamp',
            key: 'timestamp',
            render: (text) => moment(text).format('YYYY-MM-DD HH:mm:ss')
          }
        ];

      default:
        return [
          {
            title: 'Type',
            dataIndex: 'type',
            key: 'type'
          },
          {
            title: 'Asset',
            dataIndex: 'asset',
            key: 'asset'
          },
          {
            title: 'Amount',
            dataIndex: 'amount',
            key: 'amount',
            render: (text) => text.toFixed(8)
          },
          {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (text) => <Tag>{text.toUpperCase()}</Tag>
          },
          {
            title: 'Time',
            dataIndex: 'timestamp',
            key: 'timestamp',
            render: (text) => moment(text).format('YYYY-MM-DD HH:mm:ss')
          }
        ];
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="trading-history">
      <Card 
        title={
          <div className="header-title">
            <span>My Trades</span>
            <Select 
              defaultValue="USD-M Futures" 
              style={{ marginLeft: 16 }}
              size="small"
            >
              <Option value="USD-M Futures">USD-M Futures</Option>
              <Option value="COIN-M Futures">COIN-M Futures</Option>
              <Option value="Spot">Spot</Option>
            </Select>
          </div>
        }
        extra={
          <Space>
            <Button icon={<FilterOutlined />} size="small">
              Filter
            </Button>
            <Button icon={<DownloadOutlined />} size="small">
              Export
            </Button>
          </Space>
        }
      >
        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab}
          className="history-tabs"
        >
          <TabPane tab="Order History" key="order_history" />
          <TabPane tab="Position History" key="position_history" />
          <TabPane tab="Trade History" key="trade_history" />
          <TabPane tab="Transaction History" key="transaction_history" />
          <TabPane tab="Funding Fee" key="funding_fee" />
        </Tabs>

        {/* Filters */}
        <div className="filters-section">
          <Space>
            <Select
              placeholder="Asset"
              style={{ width: 120 }}
              allowClear
              onChange={(value) => handleFilterChange('asset', value)}
            >
              <Option value="USDT">USDT</Option>
              <Option value="BTC">BTC</Option>
              <Option value="ETH">ETH</Option>
              <Option value="BNB">BNB</Option>
            </Select>
            
            <Select
              placeholder="Type"
              style={{ width: 120 }}
              allowClear
              onChange={(value) => handleFilterChange('type', value)}
            >
              <Option value="market">Market</Option>
              <Option value="limit">Limit</Option>
              <Option value="stop">Stop</Option>
            </Select>
          </Space>
        </div>

        {/* Data Table */}
        <Table
          columns={getColumns()}
          dataSource={data}
          loading={loading}
          rowKey="id"
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `Total ${total} items`
          }}
          scroll={{ x: 800 }}
        />
      </Card>

      <style jsx>{`
        .trading-history {
          padding: 20px;
        }

        .header-title {
          display: flex;
          align-items: center;
        }

        .history-tabs .ant-tabs-tab {
          font-size: 14px;
          padding: 8px 16px;
        }

        .filters-section {
          margin: 16px 0;
          padding: 16px;
          background: #fafafa;
          border-radius: 6px;
        }

        .symbol {
          font-weight: 600;
          color: #1890ff;
        }

        .asset {
          font-weight: 600;
        }

        .fee-type {
          color: #666;
        }

        .profit {
          color: #52c41a;
          font-weight: 500;
        }

        .loss {
          color: #ff4d4f;
          font-weight: 500;
        }

        .ant-table-tbody > tr > td {
          padding: 12px 16px;
        }

        .ant-table-thead > tr > th {
          background: #fafafa;
          font-weight: 600;
        }

        @media (max-width: 768px) {
          .trading-history {
            padding: 10px;
          }
          
          .filters-section {
            padding: 12px;
          }
        }
      `}</style>
    </div>
  );
};

export default TradingHistory;