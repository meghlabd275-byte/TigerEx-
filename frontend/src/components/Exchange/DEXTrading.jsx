import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Select, Input, Button, Table, Tabs, Switch, message, Modal } from 'antd';
import { WalletOutlined, SwapOutlined, LinkOutlined, DisconnectOutlined } from '@ant-design/icons';

const { Option } = Select;
const { TabPane } = Tabs;

const DEXTrading = ({ selectedPair, setSelectedPair }) => {
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');
  const [fromToken, setFromToken] = useState('ETH');
  const [toToken, setToToken] = useState('USDT');
  const [fromAmount, setFromAmount] = useState('');
  const [toAmount, setToAmount] = useState('');
  const [slippage, setSlippage] = useState(0.5);
  const [gasPrice, setGasPrice] = useState('21');
  const [liquidityPools, setLiquidityPools] = useState([]);
  const [userLiquidity, setUserLiquidity] = useState([]);
  const [showConnectModal, setShowConnectModal] = useState(false);

  useEffect(() => {
    fetchLiquidityPools();
    fetchUserLiquidity();
  }, []);

  useEffect(() => {
    if (fromAmount && fromToken && toToken) {
      calculateSwapAmount();
    }
  }, [fromAmount, fromToken, toToken]);

  const fetchLiquidityPools = () => {
    // Mock liquidity pools data
    const mockPools = [
      {
        id: '1',
        pair: 'ETH/USDT',
        tvl: 12500000,
        apr: 15.2,
        volume24h: 2500000,
        fees24h: 7500
      },
      {
        id: '2',
        pair: 'BTC/ETH',
        tvl: 8750000,
        apr: 12.8,
        volume24h: 1800000,
        fees24h: 5400
      },
      {
        id: '3',
        pair: 'USDT/USDC',
        tvl: 25000000,
        apr: 8.5,
        volume24h: 5000000,
        fees24h: 15000
      }
    ];
    setLiquidityPools(mockPools);
  };

  const fetchUserLiquidity = () => {
    if (!walletConnected) return;
    
    // Mock user liquidity positions
    const mockUserLiquidity = [
      {
        id: '1',
        pair: 'ETH/USDT',
        liquidity: 5000,
        share: 0.04,
        earned: 125.50
      }
    ];
    setUserLiquidity(mockUserLiquidity);
  };

  const calculateSwapAmount = () => {
    // Mock swap calculation
    const rate = fromToken === 'ETH' ? 2650 : fromToken === 'BTC' ? 67000 : 1;
    const toRate = toToken === 'ETH' ? 2650 : toToken === 'BTC' ? 67000 : 1;
    const amount = (parseFloat(fromAmount) * rate) / toRate;
    setToAmount(amount.toFixed(6));
  };

  const connectWallet = async (walletType) => {
    // Mock wallet connection
    setWalletConnected(true);
    setWalletAddress('0x742d35Cc6634C0532925a3b8D0C9e3e0C8b8E8E8');
    setShowConnectModal(false);
    message.success(`${walletType} wallet connected successfully`);
    fetchUserLiquidity();
  };

  const disconnectWallet = () => {
    setWalletConnected(false);
    setWalletAddress('');
    setUserLiquidity([]);
    message.info('Wallet disconnected');
  };

  const handleSwap = async () => {
    if (!walletConnected) {
      message.error('Please connect your wallet first');
      return;
    }

    if (!fromAmount || !toAmount) {
      message.error('Please enter swap amounts');
      return;
    }

    // Mock swap transaction
    message.loading('Processing swap transaction...', 2);
    setTimeout(() => {
      message.success('Swap completed successfully!');
      setFromAmount('');
      setToAmount('');
    }, 2000);
  };

  const addLiquidity = (poolId) => {
    if (!walletConnected) {
      message.error('Please connect your wallet first');
      return;
    }
    message.info('Add liquidity feature coming soon');
  };

  const removeLiquidity = (positionId) => {
    message.info('Remove liquidity feature coming soon');
  };

  const poolColumns = [
    {
      title: 'Pool',
      dataIndex: 'pair',
      key: 'pair',
      render: (pair) => <strong>{pair}</strong>
    },
    {
      title: 'TVL',
      dataIndex: 'tvl',
      key: 'tvl',
      render: (tvl) => `$${(tvl / 1000000).toFixed(2)}M`
    },
    {
      title: 'APR',
      dataIndex: 'apr',
      key: 'apr',
      render: (apr) => <span style={{ color: '#52c41a' }}>{apr}%</span>
    },
    {
      title: '24h Volume',
      dataIndex: 'volume24h',
      key: 'volume24h',
      render: (volume) => `$${(volume / 1000000).toFixed(2)}M`
    },
    {
      title: '24h Fees',
      dataIndex: 'fees24h',
      key: 'fees24h',
      render: (fees) => `$${fees.toLocaleString()}`
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Button
          type="primary"
          size="small"
          onClick={() => addLiquidity(record.id)}
        >
          Add Liquidity
        </Button>
      )
    }
  ];

  const userLiquidityColumns = [
    {
      title: 'Pool',
      dataIndex: 'pair',
      key: 'pair'
    },
    {
      title: 'Liquidity',
      dataIndex: 'liquidity',
      key: 'liquidity',
      render: (liquidity) => `$${liquidity.toLocaleString()}`
    },
    {
      title: 'Pool Share',
      dataIndex: 'share',
      key: 'share',
      render: (share) => `${share}%`
    },
    {
      title: 'Earned',
      dataIndex: 'earned',
      key: 'earned',
      render: (earned) => <span style={{ color: '#52c41a' }}>${earned}</span>
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Button
          type="default"
          size="small"
          onClick={() => removeLiquidity(record.id)}
        >
          Remove
        </Button>
      )
    }
  ];

  return (
    <div className="dex-trading">
      {/* Wallet Connection */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card>
            <div className="wallet-section">
              {!walletConnected ? (
                <div className="connect-wallet">
                  <Button
                    type="primary"
                    size="large"
                    icon={<WalletOutlined />}
                    onClick={() => setShowConnectModal(true)}
                  >
                    Connect Wallet
                  </Button>
                  <p>Connect your wallet to start trading on DEX</p>
                </div>
              ) : (
                <div className="wallet-connected">
                  <div className="wallet-info">
                    <WalletOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                    <span>Connected: {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}</span>
                  </div>
                  <Button
                    icon={<DisconnectOutlined />}
                    onClick={disconnectWallet}
                  >
                    Disconnect
                  </Button>
                </div>
              )}
            </div>
          </Card>
        </Col>

        {/* Swap Interface */}
        <Col span={12}>
          <Card title="Swap Tokens" className="swap-card">
            <div className="swap-form">
              <div className="token-input">
                <div className="input-header">
                  <span>From</span>
                  <span>Balance: 2.5 ETH</span>
                </div>
                <div className="input-row">
                  <Input
                    placeholder="0.0"
                    value={fromAmount}
                    onChange={(e) => setFromAmount(e.target.value)}
                    size="large"
                  />
                  <Select
                    value={fromToken}
                    onChange={setFromToken}
                    style={{ width: 120 }}
                    size="large"
                  >
                    <Option value="ETH">ETH</Option>
                    <Option value="BTC">BTC</Option>
                    <Option value="USDT">USDT</Option>
                    <Option value="USDC">USDC</Option>
                  </Select>
                </div>
              </div>

              <div className="swap-arrow">
                <Button
                  icon={<SwapOutlined />}
                  shape="circle"
                  onClick={() => {
                    setFromToken(toToken);
                    setToToken(fromToken);
                    setFromAmount(toAmount);
                    setToAmount(fromAmount);
                  }}
                />
              </div>

              <div className="token-input">
                <div className="input-header">
                  <span>To</span>
                  <span>Balance: 5,000 USDT</span>
                </div>
                <div className="input-row">
                  <Input
                    placeholder="0.0"
                    value={toAmount}
                    readOnly
                    size="large"
                  />
                  <Select
                    value={toToken}
                    onChange={setToToken}
                    style={{ width: 120 }}
                    size="large"
                  >
                    <Option value="ETH">ETH</Option>
                    <Option value="BTC">BTC</Option>
                    <Option value="USDT">USDT</Option>
                    <Option value="USDC">USDC</Option>
                  </Select>
                </div>
              </div>

              <div className="swap-settings">
                <div className="setting-row">
                  <span>Slippage Tolerance:</span>
                  <Select
                    value={slippage}
                    onChange={setSlippage}
                    style={{ width: 100 }}
                  >
                    <Option value={0.1}>0.1%</Option>
                    <Option value={0.5}>0.5%</Option>
                    <Option value={1.0}>1.0%</Option>
                    <Option value={3.0}>3.0%</Option>
                  </Select>
                </div>
                <div className="setting-row">
                  <span>Gas Price:</span>
                  <Input
                    value={gasPrice}
                    onChange={(e) => setGasPrice(e.target.value)}
                    suffix="Gwei"
                    style={{ width: 100 }}
                  />
                </div>
              </div>

              <Button
                type="primary"
                size="large"
                block
                onClick={handleSwap}
                disabled={!walletConnected}
                className="swap-button"
              >
                {walletConnected ? 'Swap' : 'Connect Wallet to Swap'}
              </Button>
            </div>
          </Card>
        </Col>

        {/* Liquidity Pools */}
        <Col span={12}>
          <Card title="Liquidity Pools">
            <Table
              dataSource={liquidityPools}
              columns={poolColumns}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>

        {/* User Liquidity Positions */}
        {walletConnected && userLiquidity.length > 0 && (
          <Col span={24}>
            <Card title="Your Liquidity Positions">
              <Table
                dataSource={userLiquidity}
                columns={userLiquidityColumns}
                pagination={false}
                size="small"
              />
            </Card>
          </Col>
        )}
      </Row>

      {/* Wallet Connect Modal */}
      <Modal
        title="Connect Wallet"
        open={showConnectModal}
        onCancel={() => setShowConnectModal(false)}
        footer={null}
        className="connect-modal"
      >
        <div className="wallet-options">
          <Button
            block
            size="large"
            onClick={() => connectWallet('MetaMask')}
            style={{ marginBottom: 16 }}
          >
            <img src="/icons/metamask.png" alt="MetaMask" width="24" style={{ marginRight: 8 }} />
            MetaMask
          </Button>
          <Button
            block
            size="large"
            onClick={() => connectWallet('WalletConnect')}
            style={{ marginBottom: 16 }}
          >
            <img src="/icons/walletconnect.png" alt="WalletConnect" width="24" style={{ marginRight: 8 }} />
            WalletConnect
          </Button>
          <Button
            block
            size="large"
            onClick={() => connectWallet('Coinbase Wallet')}
          >
            <img src="/icons/coinbase.png" alt="Coinbase" width="24" style={{ marginRight: 8 }} />
            Coinbase Wallet
          </Button>
        </div>
      </Modal>

      <style jsx>{`
        .dex-trading {
          width: 100%;
        }

        .wallet-section {
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 20px;
        }

        .connect-wallet {
          text-align: center;
        }

        .connect-wallet p {
          margin-top: 16px;
          color: #666;
        }

        .wallet-connected {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
        }

        .wallet-info {
          display: flex;
          align-items: center;
          font-weight: 500;
        }

        .swap-card {
          height: fit-content;
        }

        .swap-form {
          padding: 16px 0;
        }

        .token-input {
          margin-bottom: 16px;
          padding: 16px;
          border: 1px solid #d9d9d9;
          border-radius: 8px;
          background: #fafafa;
        }

        .input-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          font-size: 12px;
          color: #666;
        }

        .input-row {
          display: flex;
          gap: 8px;
        }

        .input-row input {
          flex: 1;
        }

        .swap-arrow {
          display: flex;
          justify-content: center;
          margin: 16px 0;
        }

        .swap-settings {
          margin: 16px 0;
          padding: 16px;
          background: #f5f5f5;
          border-radius: 6px;
        }

        .setting-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .setting-row:last-child {
          margin-bottom: 0;
        }

        .swap-button {
          margin-top: 16px;
          height: 48px;
          font-size: 16px;
          font-weight: 500;
        }

        .wallet-options {
          padding: 16px 0;
        }

        .wallet-options button {
          display: flex;
          align-items: center;
          justify-content: flex-start;
          height: 56px;
          font-size: 16px;
        }

        @media (max-width: 768px) {
          .wallet-connected {
            flex-direction: column;
            gap: 16px;
          }
        }
      `}</style>
    </div>
  );
};

export default DEXTrading;