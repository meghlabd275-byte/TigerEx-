import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  TextInput,
  FlatList,
  RefreshControl,
  Switch,
  Dimensions,
} from 'react-native';
import {
  LineChart,
  BarChart,
  PieChart,
} from 'react-native-chart-kit';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Card, Button, Badge } from 'react-native-paper';

const { width: screenWidth } = Dimensions.get('window');

// Types for comprehensive mobile admin
interface TradingPair {
  id: string;
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  status: 'active' | 'paused' | 'suspended';
  price: number;
  change24h: number;
  volume24h: number;
  leverage: number;
  futuresEnabled: boolean;
  marginEnabled: boolean;
  optionsEnabled: boolean;
  gridEnabled: boolean;
  copyEnabled: boolean;
}

interface GridBot {
  id: string;
  pairSymbol: string;
  gridType: 'arithmetic' | 'geometric' | 'linear';
  status: 'active' | 'paused' | 'stopped' | 'completed';
  profit: number;
  winRate: number;
  investment: number;
  completedGrids: number;
  aiOptimized: boolean;
}

interface CopyTrader {
  id: string;
  masterTraderId: string;
  status: 'active' | 'paused' | 'terminated';
  totalProfit: number;
  winRate: number;
  followersCount: number;
  copyMode: 'fixed_amount' | 'percentage' | 'ratio';
}

interface BlockchainNetwork {
  id: string;
  name: string;
  chainId: number;
  status: 'active' | 'inactive' | 'maintenance';
  currentBlock: number;
  gasPrice: number;
  supportedTokens: string[];
}

interface IOUContract {
  id: string;
  iouType: 'payment' | 'loan' | 'deposit';
  amount: number;
  currency: string;
  status: 'pending' | 'active' | 'settled' | 'expired';
  maturityDate?: string;
  interestRate?: number;
}

interface VirtualCoin {
  id: string;
  symbol: string;
  name: string;
  coinType: 'utility' | 'security' | 'stablecoin';
  currentPrice: number;
  status: 'pending' | 'active' | 'delisted';
  tradingPairs: string[];
  totalSupply: string;
  circulatingSupply: string;
}

const ComprehensiveMobileAdminApp: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [modalType, setModalType] = useState('');

  // State for all components
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [gridBots, setGridBots] = useState<GridBot[]>([]);
  const [copyTraders, setCopyTraders] = useState<CopyTrader[]>([]);
  const [blockchainNetworks, setBlockchainNetworks] = useState<BlockchainNetwork[]>([]);
  const [iouContracts, setIOUContracts] = useState<IOUContract[]>([]);
  const [virtualCoins, setVirtualCoins] = useState<VirtualCoin[]>([]);

  // Form data for creation
  const [formData, setFormData] = useState({
    baseAsset: '',
    quoteAsset: 'USDT',
    minPrice: '',
    maxPrice: '',
    leverage: '10',
    enableMargin: false,
    enableFutures: false,
    enableOptions: false,
    enableGrid: false,
    enableCopy: false,
  });

  // Initialize with mock data
  useEffect(() => {
    loadMockData();
  }, []);

  const loadMockData = () => {
    setTradingPairs([
      {
        id: '1',
        symbol: 'BTC/USDT',
        baseAsset: 'BTC',
        quoteAsset: 'USDT',
        status: 'active',
        price: 43250.50,
        change24h: 2.5,
        volume24h: 125000000,
        leverage: 125,
        futuresEnabled: true,
        marginEnabled: true,
        optionsEnabled: true,
        gridEnabled: true,
        copyEnabled: true,
      },
      {
        id: '2',
        symbol: 'ETH/USDT',
        baseAsset: 'ETH',
        quoteAsset: 'USDT',
        status: 'active',
        price: 2280.75,
        change24h: -1.2,
        volume24h: 87500000,
        leverage: 75,
        futuresEnabled: true,
        marginEnabled: true,
        optionsEnabled: true,
        gridEnabled: true,
        copyEnabled: true,
      },
      {
        id: '3',
        symbol: 'SOL/USDT',
        baseAsset: 'SOL',
        quoteAsset: 'USDT',
        status: 'paused',
        price: 98.45,
        change24h: -3.8,
        volume24h: 45000000,
        leverage: 50,
        futuresEnabled: true,
        marginEnabled: false,
        optionsEnabled: false,
        gridEnabled: true,
        copyEnabled: false,
      },
    ]);

    setGridBots([
      {
        id: 'g1',
        pairSymbol: 'BTC/USDT',
        gridType: 'arithmetic',
        status: 'active',
        profit: 450.50,
        winRate: 68.5,
        investment: 10000,
        completedGrids: 125,
        aiOptimized: true,
      },
      {
        id: 'g2',
        pairSymbol: 'ETH/USDT',
        gridType: 'geometric',
        status: 'active',
        profit: 225.75,
        winRate: 72.3,
        investment: 5000,
        completedGrids: 89,
        aiOptimized: true,
      },
    ]);

    setCopyTraders([
      {
        id: 'c1',
        masterTraderId: 'master001',
        status: 'active',
        totalProfit: 1250.75,
        winRate: 72.3,
        followersCount: 156,
        copyMode: 'percentage',
      },
      {
        id: 'c2',
        masterTraderId: 'master002',
        status: 'active',
        totalProfit: 875.50,
        winRate: 68.9,
        followersCount: 89,
        copyMode: 'fixed_amount',
      },
    ]);

    setBlockchainNetworks([
      {
        id: 'eth',
        name: 'Ethereum Mainnet',
        chainId: 1,
        status: 'active',
        currentBlock: 18543210,
        gasPrice: 25.5,
        supportedTokens: ['ETH', 'USDT', 'USDC', 'WBTC'],
      },
      {
        id: 'bsc',
        name: 'Binance Smart Chain',
        chainId: 56,
        status: 'active',
        currentBlock: 32456789,
        gasPrice: 5.2,
        supportedTokens: ['BNB', 'BUSD', 'USDT', 'USDC'],
      },
    ]);

    setIOUContracts([
      {
        id: 'iou1',
        iouType: 'payment',
        amount: 10000,
        currency: 'USDT',
        status: 'active',
        maturityDate: '2024-02-15T00:00:00Z',
      },
      {
        id: 'iou2',
        iouType: 'loan',
        amount: 50000,
        currency: 'USDC',
        status: 'active',
        maturityDate: '2024-04-15T00:00:00Z',
        interestRate: 0.05,
      },
    ]);

    setVirtualCoins([
      {
        id: 'vc1',
        symbol: 'VTIGER',
        name: 'Virtual Tiger Token',
        coinType: 'utility',
        currentPrice: 1.25,
        status: 'active',
        tradingPairs: ['VTIGER/USDT', 'VTIGER/USDC'],
        totalSupply: '1000000000',
        circulatingSupply: '500000000',
      },
      {
        id: 'vc2',
        symbol: 'VSTABLE',
        name: 'Virtual Stablecoin',
        coinType: 'stablecoin',
        currentPrice: 1.00,
        status: 'active',
        tradingPairs: ['VSTABLE/USDT'],
        totalSupply: '100000000',
        circulatingSupply: '75000000',
      },
    ]);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      loadMockData();
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handlePairAction = (pairId: string, action: 'pause' | 'resume' | 'suspend') => {
    Alert.alert(
      'Confirm Action',
      `Are you sure you want to ${action} this trading pair?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Confirm',
          onPress: () => {
            setTradingPairs(prev =>
              prev.map(pair =>
                pair.id === pairId
                  ? { ...pair, status: action === 'pause' ? 'paused' : action === 'resume' ? 'active' : 'suspended' }
                  : pair
              )
            );
            Alert.alert('Success', `Trading pair ${action}d successfully`);
          },
        },
      ]
    );
  };

  const handleGridBotAction = (botId: string, action: 'pause' | 'resume' | 'stop') => {
    Alert.alert(
      'Confirm Bot Action',
      `Are you sure you want to ${action} this grid bot?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Confirm',
          onPress: () => {
            setGridBots(prev =>
              prev.map(bot =>
                bot.id === botId
                  ? { ...bot, status: action === 'pause' ? 'paused' : action === 'resume' ? 'active' : 'stopped' }
                  : bot
              )
            );
            Alert.alert('Success', `Grid bot ${action}d successfully`);
          },
        },
      ]
    );
  };

  const handleCopyTraderAction = (traderId: string, action: 'pause' | 'resume' | 'terminate') => {
    Alert.alert(
      'Confirm Action',
      `Are you sure you want to ${action} this copy trader?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Confirm',
          onPress: () => {
            setCopyTraders(prev =>
              prev.map(trader =>
                trader.id === traderId
                  ? { ...trader, status: action === 'pause' ? 'paused' : action === 'resume' ? 'active' : 'terminated' }
                  : trader
              )
            );
            Alert.alert('Success', `Copy trader ${action}d successfully`);
          },
        },
      ]
    );
  };

  const handleCreateTradingPair = () => {
    // Simulate creation
    Alert.alert('Success', 'Trading pair created successfully');
    setShowCreateModal(false);
    loadMockData();
  };

  const renderOverviewTab = () => (
    <ScrollView style={styles.tabContent} refreshControl={
      <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
    }>
      {/* Key Metrics */}
      <View style={styles.metricsGrid}>
        <Card style={styles.metricCard}>
          <View style={styles.metricContent}>
            <Icon name="trending-up" size={24} color="#3B82F6" />
            <Text style={styles.metricValue}>$2.4B</Text>
            <Text style={styles.metricLabel}>Total Volume</Text>
            <Text style={styles.metricChange}>+12.5%</Text>
          </View>
        </Card>

        <Card style={styles.metricCard}>
          <View style={styles.metricContent}>
            <Icon name="people" size={24} color="#10B981" />
            <Text style={styles.metricValue}>125.4K</Text>
            <Text style={styles.metricLabel}>Active Users</Text>
            <Text style={styles.metricChange}>+8.2%</Text>
          </View>
        </Card>

        <Card style={styles.metricCard}>
          <View style={styles.metricContent}>
            <Icon name="show-chart" size={24} color="#F59E0B" />
            <Text style={styles.metricValue}>45.7K</Text>
            <Text style={styles.metricLabel}>Open Positions</Text>
            <Text style={styles.metricChangeNegative}>-3.1%</Text>
          </View>
        </Card>

        <Card style={styles.metricCard}>
          <View style={styles.metricContent}>
            <Icon name="speed" size={24} color="#8B5CF6" />
            <Text style={styles.metricValue}>99.9%</Text>
            <Text style={styles.metricLabel}>System Health</Text>
            <Text style={styles.metricChange}>Optimal</Text>
          </View>
        </Card>
      </View>

      {/* Platform Status */}
      <Card style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>Platform Status</Text>
        <View style={styles.platformStatus}>
          <View style={styles.statusItem}>
            <Icon name="smartphone" size={20} color="#10B981" />
            <Text style={styles.statusText}>Mobile App: Operational</Text>
          </View>
          <View style={styles.statusItem}>
            <Icon name="computer" size={20} color="#10B981" />
            <Text style={styles.statusText}>Desktop App: Operational</Text>
          </View>
          <View style={styles.statusItem}>
            <Icon name="web" size={20} color="#10B981" />
            <Text style={styles.statusText}>Web App: Operational</Text>
          </View>
        </View>
      </Card>

      {/* Quick Actions */}
      <Card style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.quickActionsGrid}>
          <TouchableOpacity 
            style={styles.quickActionButton} 
            onPress={() => setShowCreateModal(true)}
          >
            <Icon name="add" size={20} color="#FFFFFF" />
            <Text style={styles.quickActionText}>Create Pair</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.quickActionButton}>
            <Icon name="pause" size={20} color="#FFFFFF" />
            <Text style={styles.quickActionText}>Pause All</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.quickActionButton}>
            <Icon name="settings" size={20} color="#FFFFFF" />
            <Text style={styles.quickActionText}>Settings</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.quickActionButton}>
            <Icon name="assessment" size={20} color="#FFFFFF" />
            <Text style={styles.quickActionText}>Reports</Text>
          </TouchableOpacity>
        </View>
      </Card>

      {/* Recent Activity */}
      <Card style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        <View style={styles.activityList}>
          <View style={styles.activityItem}>
            <View style={[styles.activityDot, { backgroundColor: '#10B981' }]} />
            <View style={styles.activityContent}>
              <Text style={styles.activityTitle}>BTC/USDT trading pair created</Text>
              <Text style={styles.activityTime}>2 minutes ago</Text>
            </View>
          </View>
          <View style={styles.activityItem}>
            <View style={[styles.activityDot, { backgroundColor: '#F59E0B' }]} />
            <View style={styles.activityContent}>
              <Text style={styles.activityTitle}>Grid bot for ETH/USDT paused</Text>
              <Text style={styles.activityTime}>15 minutes ago</Text>
            </View>
          </View>
          <View style={styles.activityItem}>
            <View style={[styles.activityDot, { backgroundColor: '#EF4444' }]} />
            <View style={styles.activityContent}>
              <Text style={styles.activityTitle}>Futures contract maintenance completed</Text>
              <Text style={styles.activityTime}>1 hour ago</Text>
            </View>
          </View>
        </View>
      </Card>
    </ScrollView>
  );

  const renderSpotTradingTab = () => (
    <ScrollView style={styles.tabContent} refreshControl={
      <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
    }>
      <View style={styles.tabHeader}>
        <Text style={styles.tabTitle}>Spot Trading Pairs</Text>
        <TouchableOpacity 
          style={styles.createButton} 
          onPress={() => setShowCreateModal(true)}
        >
          <Icon name="add" size={16} color="#FFFFFF" />
          <Text style={styles.createButtonText}>Create Pair</Text>
        </TouchableOpacity>
      </View>

      {tradingPairs.map((pair) => (
        <Card key={pair.id} style={styles.pairCard}>
          <View style={styles.pairHeader}>
            <View>
              <Text style={styles.pairSymbol}>{pair.symbol}</Text>
              <Text style={styles.pairAssets}>{pair.baseAsset}/{pair.quoteAsset}</Text>
            </View>
            <Badge 
              style={[
                styles.statusBadge,
                pair.status === 'active' ? styles.activeBadge :
                pair.status === 'paused' ? styles.pausedBadge : styles.suspendedBadge
              ]}
            >
              {pair.status.toUpperCase()}
            </Badge>
          </View>

          <View style={styles.pairDetails}>
            <View style={styles.priceInfo}>
              <Text style={styles.currentPrice}>${pair.price.toLocaleString()}</Text>
              <Text style={[
                styles.priceChange,
                pair.change24h >= 0 ? styles.positiveChange : styles.negativeChange
              ]}>
                {pair.change24h >= 0 ? '+' : ''}{pair.change24h}%
              </Text>
            </View>

            <View style={styles.pairStats}>
              <Text style={styles.statText}>Vol: ${(pair.volume24h / 1000000).toFixed(1)}M</Text>
              <Text style={styles.statText}>Leverage: {pair.leverage}x</Text>
            </View>
          </View>

          <View style={styles.featuresList}>
            {pair.futuresEnabled && (
              <Badge style={styles.featureBadge}>F</Badge>
            )}
            {pair.marginEnabled && (
              <Badge style={styles.featureBadge}>M</Badge>
            )}
            {pair.optionsEnabled && (
              <Badge style={styles.featureBadge}>O</Badge>
            )}
            {pair.gridEnabled && (
              <Badge style={styles.featureBadge}>G</Badge>
            )}
            {pair.copyEnabled && (
              <Badge style={styles.featureBadge}>C</Badge>
            )}
          </View>

          <View style={styles.pairActions}>
            {pair.status === 'active' && (
              <TouchableOpacity 
                style={[styles.actionButton, styles.pauseButton]}
                onPress={() => handlePairAction(pair.id, 'pause')}
              >
                <Icon name="pause" size={16} color="#FFFFFF" />
                <Text style={styles.actionButtonText}>Pause</Text>
              </TouchableOpacity>
            )}
            
            {pair.status === 'paused' && (
              <TouchableOpacity 
                style={[styles.actionButton, styles.resumeButton]}
                onPress={() => handlePairAction(pair.id, 'resume')}
              >
                <Icon name="play-arrow" size={16} color="#FFFFFF" />
                <Text style={styles.actionButtonText}>Resume</Text>
              </TouchableOpacity>
            )}

            <TouchableOpacity style={[styles.actionButton, styles.settingsButton]}>
              <Icon name="settings" size={16} color="#FFFFFF" />
              <Text style={styles.actionButtonText}>Settings</Text>
            </TouchableOpacity>

            <TouchableOpacity style={[styles.actionButton, styles.viewButton]}>
              <Icon name="visibility" size={16} color="#FFFFFF" />
              <Text style={styles.actionButtonText}>View</Text>
            </TouchableOpacity>
          </View>
        </Card>
      ))}
    </ScrollView>
  );

  const renderGridTradingTab = () => (
    <ScrollView style={styles.tabContent} refreshControl={
      <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
    }>
      <View style={styles.tabHeader}>
        <Text style={styles.tabTitle}>Grid Trading Bots</Text>
        <TouchableOpacity style={styles.createButton}>
          <Icon name="add" size={16} color="#FFFFFF" />
          <Text style={styles.createButtonText}>Create Bot</Text>
        </TouchableOpacity>
      </View>

      {gridBots.map((bot) => (
        <Card key={bot.id} style={styles.pairCard}>
          <View style={styles.pairHeader}>
            <View>
              <Text style={styles.pairSymbol}>Grid Bot #{bot.id}</Text>
              <Text style={styles.pairAssets}>{bot.pairSymbol} • {bot.gridType}</Text>
            </View>
            <Badge 
              style={[
                styles.statusBadge,
                bot.status === 'active' ? styles.activeBadge : styles.pausedBadge
              ]}
            >
              {bot.status.toUpperCase()}
            </Badge>
          </View>

          <View style={styles.pairDetails}>
            <View style={styles.priceInfo}>
              <Text style={styles.currentPrice}>${bot.profit.toFixed(2)}</Text>
              <Text style={[styles.priceChange, styles.positiveChange]}>
                Profit
              </Text>
            </View>

            <View style={styles.pairStats}>
              <Text style={styles.statText}>Win Rate: {bot.winRate}%</Text>
              <Text style={styles.statText}>Investment: ${bot.investment.toLocaleString()}</Text>
              <Text style={styles.statText}>Completed: {bot.completedGrids}</Text>
            </View>
          </View>

          {bot.aiOptimized && (
            <View style={styles.aiIndicator}>
              <Icon name="auto-awesome" size={16} color="#F59E0B" />
              <Text style={styles.aiText}>AI Optimized</Text>
            </View>
          )}

          <View style={styles.pairActions}>
            <TouchableOpacity 
              style={[styles.actionButton, styles.pauseButton]}
              onPress={() => handleGridBotAction(bot.id, bot.status === 'active' ? 'pause' : 'resume')}
            >
              <Icon name={bot.status === 'active' ? 'pause' : 'play-arrow'} size={16} color="#FFFFFF" />
              <Text style={styles.actionButtonText}>
                {bot.status === 'active' ? 'Pause' : 'Resume'}
              </Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.actionButton, styles.settingsButton]}>
              <Icon name="settings" size={16} color="#FFFFFF" />
              <Text style={styles.actionButtonText}>Config</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.actionButton, styles.viewButton]}>
              <Icon name="visibility" size={16} color="#FFFFFF" />
              <Text style={styles.actionButtonText}>Details</Text>
            </TouchableOpacity>
          </View>
        </Card>
      ))}
    </ScrollView>
  );

  const renderCopyTradingTab = () => (
    <ScrollView style={styles.tabContent} refreshControl={
      <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
    }>
      <View style={styles.tabHeader}>
        <Text style={styles.tabTitle}>Copy Trading</Text>
        <TouchableOpacity style={styles.createButton}>
          <Icon name="add" size={16} color="#FFFFFF" />
          <Text style={styles.createButtonText}>Add Trader</Text>
        </TouchableOpacity>
      </View>

      {copyTraders.map((trader) => (
        <Card key={trader.id} style={styles.pairCard}>
          <View style={styles.pairHeader}>
            <View>
              <Text style={styles.pairSymbol}>Master: {trader.masterTraderId}</Text>
              <Text style={styles.pairAssets}>Copy Relationship #{trader.id}</Text>
            </View>
            <Badge 
              style={[
                styles.statusBadge,
                trader.status === 'active' ? styles.activeBadge : styles.pausedBadge
              ]}
            >
              {trader.status.toUpperCase()}
            </Badge>
          </View>

          <View style={styles.pairDetails}>
            <View style={styles.priceInfo}>
              <Text style={styles.currentPrice}>${trader.totalProfit.toFixed(2)}</Text>
              <Text style={[styles.priceChange, styles.positiveChange]}>
                Total Profit
              </Text>
            </View>

            <View style={styles.pairStats}>
              <Text style={styles.statText}>Win Rate: {trader.winRate}%</Text>
              <Text style={styles.statText}>Followers: {trader.followersCount}</Text>
              <Text style={styles.statText}>Mode: {trader.copyMode}</Text>
            </View>
          </View>

          <View style={styles.pairActions}>
            <TouchableOpacity style={[styles.actionButton, styles.pauseButton]}>
              <Icon name="pause" size={16} color="#FFFFFF" />
              <Text style={styles.actionButtonText}>Pause</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.actionButton, styles.settingsButton]}>
              <Icon name="settings" size={16} color="#FFFFFF" />
              <Text style={styles.actionButtonText}>Settings</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.actionButton, styles.viewButton]}>
              <Icon name="visibility" size={16} color="#FFFFFF" />
              <Text style={styles.actionButtonText}>View</Text>
            </TouchableOpacity>
          </View>
        </Card>
      ))}
    </ScrollView>
  );

  const renderBlockchainTab = () => (
    <ScrollView style={styles.tabContent} refreshControl={
      <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
    }>
      <View style={styles.tabHeader}>
        <Text style={styles.tabTitle}>Blockchain Networks</Text>
        <TouchableOpacity style={styles.createButton}>
          <Icon name="add" size={16} color="#FFFFFF" />
          <Text style={styles.createButtonText}>Add Network</Text>
        </TouchableOpacity>
      </View>

      {blockchainNetworks.map((network) => (
        <Card key={network.id} style={styles.pairCard}>
          <View style={styles.pairHeader}>
            <View>
              <Text style={styles.pairSymbol}>{network.name}</Text>
              <Text style={styles.pairAssets}>Chain ID: {network.chainId}</Text>
            </View>
            <Badge 
              style={[
                styles.statusBadge,
                network.status === 'active' ? styles.activeBadge : styles.pausedBadge
              ]}
            >
              {network.status.toUpperCase()}
            </Badge>
          </View>

          <View style={styles.pairDetails}>
            <View style={styles.priceInfo}>
              <Text style={styles.currentPrice}>{network.currentBlock.toLocaleString()}</Text>
              <Text style={[styles.priceChange, styles.neutralChange]}>
                Current Block
              </Text>
            </View>

            <View style={styles.pairStats}>
              <Text style={styles.statText}>Gas: {network.gasPrice} Gwei</Text>
              <Text style={styles.statText}>Tokens: {network.supportedTokens.length}</Text>
            </View>
          </View>

          <View style={styles.tokensList}>
            {network.supportedTokens.slice(0, 3).map((token, index) => (
              <Badge key={index} style={styles.tokenBadge}>
                {token}
              </Badge>
            ))}
            {network.supportedTokens.length > 3 && (
              <Badge style={styles.tokenBadge}>
                +{network.supportedTokens.length - 3}
              </Badge>
            )}
          </View>

          <View style={styles.pairActions}>
            <TouchableOpacity style={[styles.actionButton, styles.settingsButton]}>
              <Icon name="settings" size={16} color="#FFFFFF" />
              <Text style={styles.actionButtonText}>Configure</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.actionButton, styles.viewButton]}>
              <Icon name="visibility" size={16} color="#FFFFFF" />
              <Text style={styles.actionButtonText}>Monitor</Text>
            </TouchableOpacity>
          </View>
        </Card>
      ))}
    </ScrollView>
  );

  const renderCreateModal = () => (
    <Modal
      visible={showCreateModal}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Create Trading Pair</Text>
          <TouchableOpacity onPress={() => setShowCreateModal(false)}>
            <Icon name="close" size={24} color="#333" />
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent}>
          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Base Asset</Text>
            <TextInput
              style={styles.formInput}
              value={formData.baseAsset}
              onChangeText={(text) => setFormData({...formData, baseAsset: text})}
              placeholder="e.g., BTC"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Quote Asset</Text>
            <TextInput
              style={styles.formInput}
              value={formData.quoteAsset}
              onChangeText={(text) => setFormData({...formData, quoteAsset: text})}
              placeholder="e.g., USDT"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Minimum Price</Text>
            <TextInput
              style={styles.formInput}
              value={formData.minPrice}
              onChangeText={(text) => setFormData({...formData, minPrice: text})}
              placeholder="0.00"
              keyboardType="numeric"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Maximum Price</Text>
            <TextInput
              style={styles.formInput}
              value={formData.maxPrice}
              onChangeText={(text) => setFormData({...formData, maxPrice: text})}
              placeholder="0.00"
              keyboardType="numeric"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Leverage</Text>
            <TextInput
              style={styles.formInput}
              value={formData.leverage}
              onChangeText={(text) => setFormData({...formData, leverage: text})}
              placeholder="10"
              keyboardType="numeric"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Enable Features</Text>
            
            <View style={styles.switchRow}>
              <Text style={styles.switchLabel}>Margin Trading</Text>
              <Switch
                value={formData.enableMargin}
                onValueChange={(value) => setFormData({...formData, enableMargin: value})}
              />
            </View>

            <View style={styles.switchRow}>
              <Text style={styles.switchLabel}>Futures Trading</Text>
              <Switch
                value={formData.enableFutures}
                onValueChange={(value) => setFormData({...formData, enableFutures: value})}
              />
            </View>

            <View style={styles.switchRow}>
              <Text style={styles.switchLabel}>Options Trading</Text>
              <Switch
                value={formData.enableOptions}
                onValueChange={(value) => setFormData({...formData, enableOptions: value})}
              />
            </View>

            <View style={styles.switchRow}>
              <Text style={styles.switchLabel}>Grid Trading</Text>
              <Switch
                value={formData.enableGrid}
                onValueChange={(value) => setFormData({...formData, enableGrid: value})}
              />
            </View>

            <View style={styles.switchRow}>
              <Text style={styles.switchLabel}>Copy Trading</Text>
              <Switch
                value={formData.enableCopy}
                onValueChange={(value) => setFormData({...formData, enableCopy: value})}
              />
            </View>
          </View>
        </ScrollView>

        <View style={styles.modalFooter}>
          <TouchableOpacity 
            style={[styles.modalButton, styles.cancelButton]}
            onPress={() => setShowCreateModal(false)}
          >
            <Text style={styles.cancelButtonText}>Cancel</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.modalButton, styles.createButtonModal]}
            onPress={handleCreateTradingPair}
          >
            <Text style={styles.createButtonText}>Create Pair</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>TigerEx Admin</Text>
        <Text style={styles.headerSubtitle}>Complete Trading Platform Management</Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabNavigation}>
        {[
          { key: 'overview', label: 'Overview', icon: 'dashboard' },
          { key: 'spot', label: 'Spot', icon: 'trending-up' },
          { key: 'grid', label: 'Grid', icon: 'grid-on' },
          { key: 'copy', label: 'Copy', icon: 'content-copy' },
          { key: 'blockchain', label: 'Blockchain', icon: 'link' },
        ].map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[
              styles.tabButton,
              activeTab === tab.key && styles.activeTabButton
            ]}
            onPress={() => setActiveTab(tab.key)}
          >
            <Icon 
              name={tab.icon} 
              size={20} 
              color={activeTab === tab.key ? '#3B82F6' : '#6B7280'} 
            />
            <Text style={[
              styles.tabButtonText,
              activeTab === tab.key && styles.activeTabButtonText
            ]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Tab Content */}
      {activeTab === 'overview' && renderOverviewTab()}
      {activeTab === 'spot' && renderSpotTradingTab()}
      {activeTab === 'grid' && renderGridTradingTab()}
      {activeTab === 'copy' && renderCopyTradingTab()}
      {activeTab === 'blockchain' && renderBlockchainTab()}

      {/* Create Modal */}
      {renderCreateModal()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    backgroundColor: '#3B82F6',
    padding: 20,
    paddingTop: 40,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#E5E7EB',
    marginTop: 4,
  },
  tabNavigation: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTabButton: {
    borderBottomColor: '#3B82F6',
  },
  tabButtonText: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  activeTabButtonText: {
    color: '#3B82F6',
    fontWeight: '600',
  },
  tabContent: {
    flex: 1,
    padding: 16,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  metricCard: {
    width: '48%',
    marginBottom: 12,
    backgroundColor: '#FFFFFF',
  },
  metricContent: {
    padding: 16,
    alignItems: 'center',
  },
  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 8,
  },
  metricLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  metricChange: {
    fontSize: 12,
    color: '#10B981',
    marginTop: 2,
  },
  metricChangeNegative: {
    color: '#EF4444',
  },
  sectionCard: {
    backgroundColor: '#FFFFFF',
    marginBottom: 16,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  platformStatus: {
    gap: 8,
  },
  statusItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  statusText: {
    fontSize: 14,
    color: '#374151',
    marginLeft: 8,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickActionButton: {
    width: '48%',
    backgroundColor: '#3B82F6',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  quickActionText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 4,
  },
  activityList: {
    gap: 12,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  activityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginTop: 6,
    marginRight: 12,
  },
  activityContent: {
    flex: 1,
  },
  activityTitle: {
    fontSize: 14,
    color: '#111827',
    marginBottom: 2,
  },
  activityTime: {
    fontSize: 12,
    color: '#6B7280',
  },
  tabHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  tabTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111827',
  },
  createButton: {
    backgroundColor: '#3B82F6',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
  },
  createButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 4,
  },
  pairCard: {
    backgroundColor: '#FFFFFF',
    marginBottom: 12,
    padding: 16,
  },
  pairHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  pairSymbol: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  pairAssets: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  activeBadge: {
    backgroundColor: '#10B981',
  },
  pausedBadge: {
    backgroundColor: '#F59E0B',
  },
  suspendedBadge: {
    backgroundColor: '#EF4444',
  },
  pairDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  priceInfo: {
    alignItems: 'flex-start',
  },
  currentPrice: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
  },
  priceChange: {
    fontSize: 12,
    marginTop: 2,
  },
  positiveChange: {
    color: '#10B981',
  },
  negativeChange: {
    color: '#EF4444',
  },
  neutralChange: {
    color: '#6B7280',
  },
  pairStats: {
    alignItems: 'flex-end',
  },
  statText: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 2,
  },
  featuresList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
    marginBottom: 12,
  },
  featureBadge: {
    backgroundColor: '#E5E7EB',
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  pairActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 8,
    borderRadius: 6,
    marginHorizontal: 2,
  },
  pauseButton: {
    backgroundColor: '#F59E0B',
  },
  resumeButton: {
    backgroundColor: '#10B981',
  },
  settingsButton: {
    backgroundColor: '#6B7280',
  },
  viewButton: {
    backgroundColor: '#3B82F6',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 4,
  },
  aiIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF3C7',
    padding: 6,
    borderRadius: 4,
    marginBottom: 12,
    alignSelf: 'flex-start',
  },
  aiText: {
    fontSize: 12,
    color: '#92400E',
    marginLeft: 4,
  },
  tokensList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
    marginBottom: 12,
  },
  tokenBadge: {
    backgroundColor: '#E5E7EB',
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  // Modal styles
  modalContainer: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  formGroup: {
    marginBottom: 20,
  },
  formLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#111827',
    marginBottom: 8,
  },
  formInput: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#111827',
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  switchLabel: {
    fontSize: 14,
    color: '#374151',
  },
  modalFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  modalButton: {
    flex: 1,
    marginHorizontal: 8,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#F3F4F6',
  },
  cancelButtonText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '500',
  },
  createButtonModal: {
    backgroundColor: '#3B82F6',
  },
});

export default ComprehensiveMobileAdminApp;