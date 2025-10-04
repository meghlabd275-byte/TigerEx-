import React, { useState, useEffect } from 'react';
import { Card, Button, Modal, Select, Input, message, Spin, List, Avatar } from 'antd';
import { ArrowRightOutlined, SwapOutlined, HistoryOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Option } = Select;

const AdvancedTransfer = () => {
  const [wallets, setWallets] = useState([]);
  const [fromWallet, setFromWallet] = useState('');
  const [toWallet, setToWallet] = useState('');
  const [amount, setAmount] = useState('');
  const [coin, setCoin] = useState('USDT');
  const [loading, setLoading] = useState(false);
  const [transferHistory, setTransferHistory] = useState([]);
  const [showWalletModal, setShowWalletModal] = useState(false);
  const [selectingFor, setSelectingFor] = useState(''); // 'from' or 'to'

  useEffect(() => {
    fetchWallets();
    fetchTransferHistory();
  }, []);

  const fetchWallets = async () => {
    try {
      const response = await axios.get('/api/advanced-transfer/wallets');
      setWallets(response.data.wallets);
      if (response.data.wallets.length > 0) {
        setFromWallet('funding');
        setToWallet('usd_m_futures');
      }
    } catch (error) {
      message.error('Failed to fetch wallets');
    }
  };

  const fetchTransferHistory = async () => {
    try {
      const response = await axios.get('/api/advanced-transfer/transfer-history');
      setTransferHistory(response.data.transfers);
    } catch (error) {
      console.error('Failed to fetch transfer history');
    }
  };

  const handleTransfer = async () => {
    if (!fromWallet || !toWallet || !amount) {
      message.error('Please fill all fields');
      return;
    }

    if (fromWallet === toWallet) {
      message.error('Cannot transfer to the same wallet');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/advanced-transfer/transfer', {
        from_wallet: fromWallet,
        to_wallet: toWallet,
        coin: coin,
        amount: parseFloat(amount)
      });

      if (response.data.success) {
        message.success(response.data.message);
        setAmount('');
        fetchWallets();
        fetchTransferHistory();
      }
    } catch (error) {
      message.error(error.response?.data?.detail || 'Transfer failed');
    } finally {
      setLoading(false);
    }
  };

  const openWalletSelector = (type) => {
    setSelectingFor(type);
    setShowWalletModal(true);
  };

  const selectWallet = (walletId) => {
    if (selectingFor === 'from') {
      setFromWallet(walletId);
    } else {
      setToWallet(walletId);
    }
    setShowWalletModal(false);
  };

  const getWalletInfo = (walletId) => {
    return wallets.find(w => w.id === walletId) || {};
  };

  const getAvailableBalance = () => {
    const wallet = getWalletInfo(fromWallet);
    return wallet.balance || 0;
  };

  return (
    <div className="advanced-transfer">
      <Card title="Transfer" extra={<HistoryOutlined />}>
        {/* From Section */}
        <div className="transfer-section">
          <div className="section-label">From</div>
          <div 
            className="wallet-selector"
            onClick={() => openWalletSelector('from')}
          >
            <div className="wallet-info">
              <span className="wallet-icon">{getWalletInfo(fromWallet).icon}</span>
              <span className="wallet-name">{getWalletInfo(fromWallet).name || 'Select Wallet'}</span>
            </div>
            <ArrowRightOutlined />
          </div>
        </div>

        {/* To Section */}
        <div className="transfer-section">
          <div className="section-label">To</div>
          <div 
            className="wallet-selector"
            onClick={() => openWalletSelector('to')}
          >
            <div className="wallet-info">
              <span className="wallet-icon">{getWalletInfo(toWallet).icon}</span>
              <span className="wallet-name">{getWalletInfo(toWallet).name || 'Select Wallet'}</span>
            </div>
            <ArrowRightOutlined />
          </div>
        </div>

        {/* Coin Selection */}
        <div className="transfer-section">
          <div className="section-label">Coin</div>
          <div className="coin-selector">
            <Avatar src="/icons/btc.png" size="small" />
            <span>BTC</span>
            <span className="coin-name">Bitcoin</span>
            <ArrowRightOutlined />
          </div>
          {fromWallet && (
            <div className="balance-info">
              Available: {getAvailableBalance().toFixed(8)} {coin}
            </div>
          )}
        </div>

        {/* Amount Input */}
        <div className="transfer-section">
          <div className="section-label">Amount</div>
          <div className="amount-input">
            <Input
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00000000"
              suffix={
                <div className="amount-controls">
                  <span className="currency">{coin}</span>
                  <Button 
                    type="link" 
                    size="small"
                    onClick={() => setAmount(getAvailableBalance().toString())}
                  >
                    Max
                  </Button>
                </div>
              }
            />
          </div>
        </div>

        {/* Transfer Button */}
        <Button
          type="primary"
          size="large"
          block
          loading={loading}
          onClick={handleTransfer}
          disabled={!amount || !fromWallet || !toWallet}
          className="transfer-button"
        >
          Confirm Transfer
        </Button>

        {/* Transfer History */}
        {transferHistory.length > 0 && (
          <div className="transfer-history">
            <h3>Recent Transfers</h3>
            <List
              dataSource={transferHistory.slice(0, 5)}
              renderItem={(item) => (
                <List.Item>
                  <div className="history-item">
                    <div className="transfer-info">
                      <span>{item.from_wallet} → {item.to_wallet}</span>
                      <span className="amount">{item.amount} {item.currency}</span>
                    </div>
                    <div className="transfer-time">
                      {new Date(item.created_at).toLocaleString()}
                    </div>
                  </div>
                </List.Item>
              )}
            />
          </div>
        )}
      </Card>

      {/* Wallet Selection Modal */}
      <Modal
        title="Select a wallet"
        open={showWalletModal}
        onCancel={() => setShowWalletModal(false)}
        footer={null}
        className="wallet-selection-modal"
      >
        <List
          dataSource={wallets}
          renderItem={(wallet) => (
            <List.Item
              onClick={() => selectWallet(wallet.id)}
              className={`wallet-item ${
                (selectingFor === 'from' ? fromWallet : toWallet) === wallet.id ? 'selected' : ''
              }`}
            >
              <div className="wallet-option">
                <div className="wallet-icon-large">{wallet.icon}</div>
                <div className="wallet-details">
                  <div className="wallet-name">{wallet.name}</div>
                  <div className="wallet-balance">{wallet.balance} {wallet.currency}</div>
                </div>
              </div>
            </List.Item>
          )}
        />
      </Modal>

      <style jsx>{`
        .advanced-transfer {
          max-width: 400px;
          margin: 0 auto;
          padding: 20px;
        }

        .transfer-section {
          margin-bottom: 20px;
        }

        .section-label {
          font-size: 14px;
          color: #666;
          margin-bottom: 8px;
        }

        .wallet-selector, .coin-selector {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          border: 1px solid #d9d9d9;
          border-radius: 6px;
          cursor: pointer;
          background: #fff;
        }

        .wallet-selector:hover, .coin-selector:hover {
          border-color: #1890ff;
        }

        .wallet-info {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .wallet-icon {
          font-size: 20px;
        }

        .wallet-name {
          font-weight: 500;
        }

        .coin-name {
          color: #666;
          margin-left: 8px;
        }

        .balance-info {
          font-size: 12px;
          color: #666;
          margin-top: 4px;
        }

        .amount-input {
          position: relative;
        }

        .amount-controls {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .currency {
          font-weight: 500;
        }

        .transfer-button {
          margin-top: 20px;
          height: 48px;
          font-size: 16px;
          font-weight: 500;
        }

        .transfer-history {
          margin-top: 30px;
        }

        .history-item {
          width: 100%;
        }

        .transfer-info {
          display: flex;
          justify-content: space-between;
          font-weight: 500;
        }

        .transfer-time {
          font-size: 12px;
          color: #666;
        }

        .wallet-selection-modal .wallet-item {
          cursor: pointer;
          border-radius: 8px;
          margin-bottom: 8px;
        }

        .wallet-selection-modal .wallet-item:hover {
          background: #f5f5f5;
        }

        .wallet-selection-modal .wallet-item.selected {
          background: #e6f7ff;
          border: 1px solid #1890ff;
        }

        .wallet-option {
          display: flex;
          align-items: center;
          gap: 12px;
          width: 100%;
        }

        .wallet-icon-large {
          font-size: 24px;
        }

        .wallet-details {
          flex: 1;
        }

        .wallet-balance {
          font-size: 12px;
          color: #666;
        }
      `}</style>
    </div>
  );
};

export default AdvancedTransfer;