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
import { Card, Tabs, List, Button, Modal, Input, Select, message, Avatar, Space } from 'antd';
import { DownOutlined, CopyOutlined, QrcodeOutlined } from '@ant-design/icons';
import axios from 'axios';

const { TabPane } = Tabs;
const { Option } = Select;

const DepositWithdraw = () => {
  const [activeTab, setActiveTab] = useState('deposit');
  const [depositMethods, setDepositMethods] = useState([]);
  const [withdrawMethods, setWithdrawMethods] = useState([]);
  const [selectedMethod, setSelectedMethod] = useState(null);
  const [showMethodModal, setShowMethodModal] = useState(false);
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('USDT');
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMethods();
  }, []);

  const fetchMethods = async () => {
    try {
      const [depositRes, withdrawRes] = await Promise.all([
        axios.get('/api/deposit-withdraw/deposit-methods'),
        axios.get('/api/deposit-withdraw/withdraw-methods')
      ]);
      
      setDepositMethods(depositRes.data.deposit_methods);
      setWithdrawMethods(withdrawRes.data.withdraw_methods);
    } catch (error) {
      message.error('Failed to fetch methods');
    }
  };

  const handleMethodSelect = (method) => {
    setSelectedMethod(method);
    setShowMethodModal(true);
  };

  const handleDeposit = async () => {
    if (!selectedMethod || !amount) {
      message.error('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/deposit-withdraw/deposit', {
        method: selectedMethod.id,
        amount: parseFloat(amount),
        currency: currency
      });

      if (response.data.success) {
        message.success('Deposit request created successfully');
        setShowMethodModal(false);
        setAmount('');
        
        // Show deposit address for on-chain deposits
        if (response.data.deposit_address) {
          Modal.info({
            title: 'Deposit Address',
            content: (
              <div>
                <p>Send {currency} to this address:</p>
                <div style={{ 
                  background: '#f5f5f5', 
                  padding: '10px', 
                  borderRadius: '4px',
                  wordBreak: 'break-all'
                }}>
                  {response.data.deposit_address}
                </div>
                <Button 
                  icon={<CopyOutlined />} 
                  onClick={() => navigator.clipboard.writeText(response.data.deposit_address)}
                  style={{ marginTop: '10px' }}
                >
                  Copy Address
                </Button>
              </div>
            )
          });
        }
      }
    } catch (error) {
      message.error(error.response?.data?.detail || 'Deposit failed');
    } finally {
      setLoading(false);
    }
  };

  const handleWithdraw = async () => {
    if (!selectedMethod || !amount) {
      message.error('Please fill all required fields');
      return;
    }

    if (selectedMethod.id === 'on_chain' && !address) {
      message.error('Please enter withdrawal address');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/deposit-withdraw/withdraw', {
        method: selectedMethod.id,
        amount: parseFloat(amount),
        currency: currency,
        address: address
      });

      if (response.data.success) {
        message.success('Withdrawal request submitted successfully');
        setShowMethodModal(false);
        setAmount('');
        setAddress('');
      }
    } catch (error) {
      message.error(error.response?.data?.detail || 'Withdrawal failed');
    } finally {
      setLoading(false);
    }
  };

  const renderDepositMethods = () => (
    <List
      dataSource={depositMethods}
      renderItem={(method) => (
        <List.Item
          className="method-item"
          onClick={() => handleMethodSelect(method)}
        >
          <div className="method-content">
            <div className="method-icon">
              <span style={{ fontSize: '24px' }}>{method.icon}</span>
            </div>
            <div className="method-info">
              <div className="method-name">{method.name}</div>
              <div className="method-description">{method.description}</div>
            </div>
          </div>
        </List.Item>
      )}
    />
  );

  const renderWithdrawMethods = () => (
    <List
      dataSource={withdrawMethods}
      renderItem={(method) => (
        <List.Item
          className="method-item"
          onClick={() => handleMethodSelect(method)}
        >
          <div className="method-content">
            <div className="method-icon">
              <span style={{ fontSize: '24px' }}>{method.icon}</span>
            </div>
            <div className="method-info">
              <div className="method-name">{method.name}</div>
              <div className="method-description">{method.description}</div>
            </div>
          </div>
        </List.Item>
      )}
    />
  );

  return (
    <div className="deposit-withdraw">
      {/* Portfolio Overview */}
      <Card className="portfolio-overview">
        <div className="overview-header">
          <div className="portfolio-tabs">
            <span className="tab active">Overview</span>
            <span className="tab">Futures</span>
            <span className="tab">Spot</span>
            <span className="tab">Funding</span>
            <span className="tab">Earn</span>
          </div>
        </div>
        
        <div className="portfolio-value">
          <div className="total-value">
            <span className="value-label">Est. Total Value</span>
            <div className="value-amount">
              <span className="hidden-value">******</span>
              <Select defaultValue="USDT" size="small" style={{ marginLeft: 8 }}>
                <Option value="USDT">USDT</Option>
                <Option value="BTC">BTC</Option>
              </Select>
            </div>
          </div>
          
          <div className="pnl-info">
            <span className="pnl-label">Today's PNL</span>
            <span className="pnl-value">******</span>
          </div>
        </div>

        <div className="action-buttons">
          <Button type="primary" size="large">Add Funds</Button>
          <Button size="large">Send</Button>
          <Button size="large">Transfer</Button>
        </div>

        {/* Asset List */}
        <div className="asset-tabs">
          <span className="asset-tab active">Crypto</span>
          <span className="asset-tab">Account</span>
        </div>

        <div className="asset-list">
          <div className="asset-item">
            <Avatar src="/icons/usdt.png" size="small" />
            <div className="asset-info">
              <span className="asset-name">USDT</span>
              <span className="asset-network">TetherUS</span>
            </div>
            <div className="asset-actions">
              <Button size="small">Earn</Button>
              <Button size="small">Trade</Button>
            </div>
            <span className="asset-balance">******</span>
          </div>

          <div className="asset-item">
            <Avatar src="/icons/shib.png" size="small" />
            <div className="asset-info">
              <span className="asset-name">SHIB</span>
              <span className="asset-network">SHIBA INU</span>
            </div>
            <div className="asset-actions">
              <Button size="small">Earn</Button>
              <Button size="small">Trade</Button>
            </div>
            <span className="asset-balance">******</span>
          </div>
        </div>
      </Card>

      {/* Method Selection Modal */}
      <Modal
        title={activeTab === 'deposit' ? 'Select Deposit Method' : 'Select Withdraw Method'}
        open={showMethodModal}
        onCancel={() => setShowMethodModal(false)}
        footer={null}
        width={400}
      >
        {activeTab === 'deposit' ? renderDepositMethods() : renderWithdrawMethods()}
      </Modal>

      {/* Transaction Modal */}
      <Modal
        title={selectedMethod ? 
          (activeTab === 'deposit' ? selectedMethod.name : selectedMethod.name) : 
          'Transaction'
        }
        open={selectedMethod && showMethodModal}
        onCancel={() => {
          setSelectedMethod(null);
          setShowMethodModal(false);
        }}
        footer={[
          <Button key="cancel" onClick={() => {
            setSelectedMethod(null);
            setShowMethodModal(false);
          }}>
            Cancel
          </Button>,
          <Button 
            key="submit" 
            type="primary" 
            loading={loading}
            onClick={activeTab === 'deposit' ? handleDeposit : handleWithdraw}
          >
            {activeTab === 'deposit' ? 'Confirm Deposit' : 'Confirm Withdrawal'}
          </Button>
        ]}
      >
        {selectedMethod && (
          <div className="transaction-form">
            <div className="form-item">
              <label>Currency</label>
              <Select 
                value={currency} 
                onChange={setCurrency}
                style={{ width: '100%' }}
              >
                <Option value="USDT">USDT</Option>
                <Option value="BTC">BTC</Option>
                <Option value="ETH">ETH</Option>
              </Select>
            </div>

            <div className="form-item">
              <label>Amount</label>
              <Input
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Enter amount"
                suffix={currency}
              />
              <div className="amount-info">
                Min: {selectedMethod.min_amount} {currency} | 
                Max: {selectedMethod.max_amount} {currency}
              </div>
            </div>

            {activeTab === 'withdraw' && selectedMethod.id === 'on_chain' && (
              <div className="form-item">
                <label>Withdrawal Address</label>
                <Input
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Enter withdrawal address"
                />
              </div>
            )}

            <div className="method-details">
              <div className="detail-item">
                <span>Processing Time:</span>
                <span>{selectedMethod.processing_time}</span>
              </div>
              <div className="detail-item">
                <span>Fee:</span>
                <span>{selectedMethod.fee} {currency}</span>
              </div>
            </div>
          </div>
        )}
      </Modal>

      <style jsx>{`
        .deposit-withdraw {
          max-width: 400px;
          margin: 0 auto;
          padding: 20px;
        }

        .portfolio-overview {
          margin-bottom: 20px;
        }

        .overview-header {
          margin-bottom: 20px;
        }

        .portfolio-tabs {
          display: flex;
          gap: 20px;
        }

        .tab {
          padding: 8px 0;
          cursor: pointer;
          color: #666;
          border-bottom: 2px solid transparent;
        }

        .tab.active {
          color: #1890ff;
          border-bottom-color: #1890ff;
        }

        .portfolio-value {
          margin-bottom: 20px;
        }

        .total-value {
          margin-bottom: 8px;
        }

        .value-label, .pnl-label {
          font-size: 14px;
          color: #666;
        }

        .value-amount {
          display: flex;
          align-items: center;
          font-size: 24px;
          font-weight: 600;
        }

        .hidden-value {
          font-family: monospace;
        }

        .pnl-value {
          font-family: monospace;
        }

        .action-buttons {
          display: flex;
          gap: 12px;
          margin-bottom: 20px;
        }

        .action-buttons button {
          flex: 1;
        }

        .asset-tabs {
          display: flex;
          gap: 20px;
          margin-bottom: 16px;
          border-bottom: 1px solid #f0f0f0;
        }

        .asset-tab {
          padding: 8px 0;
          cursor: pointer;
          color: #666;
          border-bottom: 2px solid transparent;
        }

        .asset-tab.active {
          color: #1890ff;
          border-bottom-color: #1890ff;
        }

        .asset-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .asset-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 0;
        }

        .asset-info {
          flex: 1;
        }

        .asset-name {
          font-weight: 600;
          display: block;
        }

        .asset-network {
          font-size: 12px;
          color: #666;
        }

        .asset-actions {
          display: flex;
          gap: 8px;
        }

        .asset-balance {
          font-family: monospace;
          font-weight: 600;
        }

        .method-item {
          cursor: pointer;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 8px;
          border: 1px solid #f0f0f0;
        }

        .method-item:hover {
          background: #f5f5f5;
          border-color: #1890ff;
        }

        .method-content {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .method-info {
          flex: 1;
        }

        .method-name {
          font-weight: 600;
          margin-bottom: 4px;
        }

        .method-description {
          font-size: 12px;
          color: #666;
        }

        .transaction-form {
          padding: 16px 0;
        }

        .form-item {
          margin-bottom: 16px;
        }

        .form-item label {
          display: block;
          margin-bottom: 8px;
          font-weight: 500;
        }

        .amount-info {
          font-size: 12px;
          color: #666;
          margin-top: 4px;
        }

        .method-details {
          background: #f5f5f5;
          padding: 12px;
          border-radius: 6px;
          margin-top: 16px;
        }

        .detail-item {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
        }

        .detail-item:last-child {
          margin-bottom: 0;
        }
      `}</style>
    </div>
  );
};

export default DepositWithdraw;