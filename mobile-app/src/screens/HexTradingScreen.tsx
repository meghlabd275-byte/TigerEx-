import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  RefreshControl,
  Dimensions,
  Switch,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { LineChart, BarChart } from 'react-native-chart-kit';

const { width: screenWidth } = Dimensions.get('window');

interface TradingPair {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  price: number;
  change24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
}

interface PriceQuote {
  cex: {
    price: number;
    liquidity: number;
    fees: number;
    executionTime: number;
  };
  dex: {
    price: number;
    liquidity: number;
    fees: number;
    executionTime: number;
    gasCost: number;
  };
  bestPrice: number;
  bestVenue: 'cex' | 'dex';
  savings: number;
}

interface Portfolio {
  totalValue: number;
  pnl24h: number;
  cexBalances: { [key: string]: number };
  dexBalances: { [key: string]: number };
}

const HexTradingScreen: React.FC = () => {
  const [selectedPair, setSelectedPair] = useState<TradingPair>({
    symbol: 'BTC/USDT',
    baseAsset: 'BTC',
    quoteAsset: 'USDT',
    price: 50000,
    change24h: 2.5,
    volume24h: 1250000000,
    high24h: 51200,
    low24h: 48800
  });

  const [hexMode, setHexMode] = useState<boolean>(true);
  const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [quantity, setQuantity] = useState<string>('');
  const [price, setPrice] = useState<string>('');
  const [venue, setVenue] = useState<'cex' | 'dex' | 'hybrid'>('hybrid');
  const [slippage, setSlippage] = useState<number>(0.5);
  
  const [priceQuote, setPriceQuote] = useState<PriceQuote | null>(null);
  const [portfolio, setPortfolio] = useState<Portfolio>({
    totalValue: 150000,
    pnl24h: 2500,
    cexBalances: { BTC: 1.5, ETH: 10.0, USDT: 50000 },
    dexBalances: { BTC: 0.5, ETH: 5.0, USDT: 25000 }
  });
  
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'trade' | 'portfolio' | 'orders'>('trade');

  // Chart data
  const priceData = {
    labels: ['1h', '4h', '12h', '1d', '3d', '1w'],
    datasets: [{
      data: [48500, 49200, 50100, 49800, 50500, 50000],
      color: (opacity = 1) => `rgba(34, 197, 94, ${opacity})`,
      strokeWidth: 2
    }]
  };

  const volumeData = {
    labels: ['CEX', 'DEX'],
    datasets: [{
      data: [750000000, 500000000]
    }]
  };

  // Fetch price quotes
  const fetchPriceQuote = useCallback(async () => {
    if (!quantity || parseFloat(quantity) <= 0) return;

    try {
      const response = await fetch(`/api/v1/price/${selectedPair.symbol}?side=${side}&quantity=${quantity}`);
      const data = await response.json();
      
      if (data.success) {
        setPriceQuote(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch price quote:', error);
    }
  }, [selectedPair.symbol, side, quantity]);

  // Execute trade
  const executeTrade = async () => {
    if (!quantity || parseFloat(quantity) <= 0) {
      Alert.alert('Error', 'Please enter a valid quantity');
      return;
    }

    setIsLoading(true);
    try {
      const tradeRequest = {
        user_id: 'user123',
        symbol: selectedPair.symbol,
        side,
        order_type: orderType,
        quantity: parseFloat(quantity),
        price: orderType === 'limit' ? parseFloat(price) : undefined,
        exchange_type: venue,
        slippage_tolerance: slippage
      };

      const response = await fetch('/api/v1/trade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tradeRequest)
      });

      const data = await response.json();
      
      if (data.success) {
        Alert.alert(
          'Trade Executed',
          `${side.toUpperCase()} ${quantity} ${selectedPair.baseAsset} at ${data.data.price} on ${data.data.exchange.toUpperCase()}`,
          [{ text: 'OK' }]
        );
        
        setQuantity('');
        setPrice('');
        await fetchPortfolio();
      }
    } catch (error) {
      Alert.alert('Error', 'Trade execution failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch portfolio
  const fetchPortfolio = async () => {
    try {
      const response = await fetch('/api/v1/portfolio/user123');
      const data = await response.json();
      
      if (data.success) {
        setPortfolio({
          totalValue: data.data.total_value_usd,
          pnl24h: data.data.pnl_24h,
          cexBalances: data.data.cex_balances,
          dexBalances: data.data.dex_balances
        });
      }
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
    }
  };

  // Refresh data
  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([fetchPriceQuote(), fetchPortfolio()]);
    setRefreshing(false);
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  useEffect(() => {
    const timer = setTimeout(fetchPriceQuote, 500);
    return () => clearTimeout(timer);
  }, [fetchPriceQuote]);

  const formatCurrency = (value: number, decimals: number = 2) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  };

  const formatNumber = (value: number, decimals: number = 8) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  };

  const renderTradeTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Price Header */}
      <LinearGradient
        colors={['#1f2937', '#374151']}
        style={styles.priceHeader}
      >
        <View style={styles.priceInfo}>
          <Text style={styles.pairSymbol}>{selectedPair.symbol}</Text>
          <Text style={styles.currentPrice}>{formatCurrency(selectedPair.price)}</Text>
          <View style={styles.priceChange}>
            <Ionicons 
              name={selectedPair.change24h >= 0 ? 'trending-up' : 'trending-down'} 
              size={16} 
              color={selectedPair.change24h >= 0 ? '#10b981' : '#ef4444'} 
            />
            <Text style={[
              styles.changeText,
              { color: selectedPair.change24h >= 0 ? '#10b981' : '#ef4444' }
            ]}>
              {selectedPair.change24h >= 0 ? '+' : ''}{selectedPair.change24h.toFixed(2)}%
            </Text>
          </View>
        </View>
        
        <View style={styles.hexToggle}>
          <Text style={styles.hexLabel}>Hex Mode</Text>
          <Switch
            value={hexMode}
            onValueChange={setHexMode}
            trackColor={{ false: '#767577', true: '#10b981' }}
            thumbColor={hexMode ? '#ffffff' : '#f4f3f4'}
          />
        </View>
      </LinearGradient>

      {/* Chart */}
      <View style={styles.chartContainer}>
        <Text style={styles.sectionTitle}>Price Chart</Text>
        <LineChart
          data={priceData}
          width={screenWidth - 32}
          height={200}
          chartConfig={{
            backgroundColor: '#ffffff',
            backgroundGradientFrom: '#ffffff',
            backgroundGradientTo: '#ffffff',
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(34, 197, 94, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
            style: {
              borderRadius: 16
            },
            propsForDots: {
              r: '4',
              strokeWidth: '2',
              stroke: '#22c55e'
            }
          }}
          bezier
          style={styles.chart}
        />
      </View>

      {/* Trading Panel */}
      <View style={styles.tradingPanel}>
        <Text style={styles.sectionTitle}>Place Order</Text>
        
        {/* Order Type */}
        <View style={styles.orderTypeContainer}>
          <TouchableOpacity
            style={[styles.orderTypeButton, orderType === 'market' && styles.activeOrderType]}
            onPress={() => setOrderType('market')}
          >
            <Text style={[styles.orderTypeText, orderType === 'market' && styles.activeOrderTypeText]}>
              Market
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.orderTypeButton, orderType === 'limit' && styles.activeOrderType]}
            onPress={() => setOrderType('limit')}
          >
            <Text style={[styles.orderTypeText, orderType === 'limit' && styles.activeOrderTypeText]}>
              Limit
            </Text>
          </TouchableOpacity>
        </View>

        {/* Buy/Sell Toggle */}
        <View style={styles.sideContainer}>
          <TouchableOpacity
            style={[styles.sideButton, styles.buyButton, side === 'buy' && styles.activeBuy]}
            onPress={() => setSide('buy')}
          >
            <Text style={[styles.sideText, side === 'buy' && styles.activeSideText]}>
              Buy
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.sideButton, styles.sellButton, side === 'sell' && styles.activeSell]}
            onPress={() => setSide('sell')}
          >
            <Text style={[styles.sideText, side === 'sell' && styles.activeSideText]}>
              Sell
            </Text>
          </TouchableOpacity>
        </View>

        {/* Venue Selection */}
        {hexMode && (
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Execution Venue</Text>
            <View style={styles.venueContainer}>
              {['hybrid', 'cex', 'dex'].map((v) => (
                <TouchableOpacity
                  key={v}
                  style={[styles.venueButton, venue === v && styles.activeVenue]}
                  onPress={() => setVenue(v as 'cex' | 'dex' | 'hybrid')}
                >
                  <Text style={[styles.venueText, venue === v && styles.activeVenueText]}>
                    {v.toUpperCase()}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* Price Input (Limit Orders) */}
        {orderType === 'limit' && (
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Price ({selectedPair.quoteAsset})</Text>
            <TextInput
              style={styles.input}
              placeholder="0.00"
              value={price}
              onChangeText={setPrice}
              keyboardType="numeric"
              placeholderTextColor="#9ca3af"
            />
          </View>
        )}

        {/* Quantity Input */}
        <View style={styles.inputContainer}>
          <Text style={styles.inputLabel}>Quantity ({selectedPair.baseAsset})</Text>
          <TextInput
            style={styles.input}
            placeholder="0.00"
            value={quantity}
            onChangeText={setQuantity}
            keyboardType="numeric"
            placeholderTextColor="#9ca3af"
          />
        </View>

        {/* Price Quote */}
        {priceQuote && hexMode && (
          <View style={styles.quoteContainer}>
            <Text style={styles.quoteTitle}>Price Comparison</Text>
            <View style={styles.quoteRow}>
              <Text style={styles.quoteLabel}>CEX Price:</Text>
              <Text style={styles.quoteValue}>{formatCurrency(priceQuote.cex.price)}</Text>
            </View>
            <View style={styles.quoteRow}>
              <Text style={styles.quoteLabel}>DEX Price:</Text>
              <Text style={styles.quoteValue}>{formatCurrency(priceQuote.dex.price)}</Text>
            </View>
            <View style={styles.quoteRow}>
              <Text style={styles.quoteLabelBest}>Best Price:</Text>
              <Text style={styles.quoteValueBest}>
                {formatCurrency(priceQuote.bestPrice)} ({priceQuote.bestVenue.toUpperCase()})
              </Text>
            </View>
            <View style={styles.quoteRow}>
              <Text style={styles.quoteLabel}>Savings:</Text>
              <Text style={styles.quoteSavings}>{formatCurrency(priceQuote.savings)}</Text>
            </View>
          </View>
        )}

        {/* Total */}
        <View style={styles.totalContainer}>
          <Text style={styles.totalLabel}>Total</Text>
          <Text style={styles.totalValue}>
            {quantity && (orderType === 'market' ? selectedPair.price : parseFloat(price || '0')) 
              ? formatCurrency(parseFloat(quantity || '0') * (orderType === 'market' ? selectedPair.price : parseFloat(price || '0')))
              : formatCurrency(0)
            }
          </Text>
        </View>

        {/* Execute Button */}
        <TouchableOpacity
          style={[
            styles.executeButton,
            side === 'buy' ? styles.buyExecuteButton : styles.sellExecuteButton,
            (isLoading || !quantity || parseFloat(quantity) <= 0) && styles.disabledButton
          ]}
          onPress={executeTrade}
          disabled={isLoading || !quantity || parseFloat(quantity) <= 0}
        >
          {isLoading ? (
            <Text style={styles.executeButtonText}>Processing...</Text>
          ) : (
            <Text style={styles.executeButtonText}>
              {side === 'buy' ? 'Buy' : 'Sell'} {selectedPair.baseAsset}
            </Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );

  const renderPortfolioTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Portfolio Summary */}
      <LinearGradient
        colors={['#1f2937', '#374151']}
        style={styles.portfolioHeader}
      >
        <Text style={styles.portfolioTitle}>Total Portfolio Value</Text>
        <Text style={styles.portfolioValue}>{formatCurrency(portfolio.totalValue)}</Text>
        <View style={styles.pnlContainer}>
          <Ionicons 
            name={portfolio.pnl24h >= 0 ? 'trending-up' : 'trending-down'} 
            size={16} 
            color={portfolio.pnl24h >= 0 ? '#10b981' : '#ef4444'} 
          />
          <Text style={[
            styles.pnlText,
            { color: portfolio.pnl24h >= 0 ? '#10b981' : '#ef4444' }
          ]}>
            {portfolio.pnl24h >= 0 ? '+' : ''}{formatCurrency(portfolio.pnl24h)} (24h)
          </Text>
        </View>
      </LinearGradient>

      {/* CEX Balances */}
      <View style={styles.balanceSection}>
        <Text style={styles.sectionTitle}>CEX Balances</Text>
        {Object.entries(portfolio.cexBalances).map(([asset, balance]) => (
          <View key={asset} style={styles.balanceRow}>
            <Text style={styles.assetName}>{asset}</Text>
            <Text style={styles.assetBalance}>{formatNumber(balance, 4)}</Text>
          </View>
        ))}
      </View>

      {/* DEX Balances */}
      <View style={styles.balanceSection}>
        <Text style={styles.sectionTitle}>DEX Balances</Text>
        {Object.entries(portfolio.dexBalances).map(([asset, balance]) => (
          <View key={asset} style={styles.balanceRow}>
            <Text style={styles.assetName}>{asset}</Text>
            <Text style={styles.assetBalance}>{formatNumber(balance, 4)}</Text>
          </View>
        ))}
      </View>

      {/* Volume Distribution */}
      <View style={styles.chartContainer}>
        <Text style={styles.sectionTitle}>Volume Distribution</Text>
        <BarChart
          data={volumeData}
          width={screenWidth - 32}
          height={200}
          yAxisLabel="$"
          yAxisSuffix="M"
          chartConfig={{
            backgroundColor: '#ffffff',
            backgroundGradientFrom: '#ffffff',
            backgroundGradientTo: '#ffffff',
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
          }}
          style={styles.chart}
        />
      </View>
    </ScrollView>
  );

  const renderOrdersTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.ordersContainer}>
        <Text style={styles.sectionTitle}>Open Orders</Text>
        <Text style={styles.emptyState}>No open orders</Text>
      </View>
      
      <View style={styles.ordersContainer}>
        <Text style={styles.sectionTitle}>Order History</Text>
        <Text style={styles.emptyState}>No recent orders</Text>
      </View>
    </ScrollView>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>TigerEx Hex</Text>
        <TouchableOpacity style={styles.settingsButton}>
          <Ionicons name="settings-outline" size={24} color="#ffffff" />
        </TouchableOpacity>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabNavigation}>
        {[
          { key: 'trade', label: 'Trade', icon: 'swap-horizontal' },
          { key: 'portfolio', label: 'Portfolio', icon: 'pie-chart' },
          { key: 'orders', label: 'Orders', icon: 'list' }
        ].map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[styles.tabButton, activeTab === tab.key && styles.activeTab]}
            onPress={() => setActiveTab(tab.key as 'trade' | 'portfolio' | 'orders')}
          >
            <Ionicons 
              name={tab.icon as any} 
              size={20} 
              color={activeTab === tab.key ? '#3b82f6' : '#6b7280'} 
            />
            <Text style={[
              styles.tabLabel,
              activeTab === tab.key && styles.activeTabLabel
            ]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Tab Content */}
      {activeTab === 'trade' && renderTradeTab()}
      {activeTab === 'portfolio' && renderPortfolioTab()}
      {activeTab === 'orders' && renderOrdersTab()}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#1f2937',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  settingsButton: {
    padding: 8,
  },
  tabNavigation: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  tabButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: '#3b82f6',
  },
  tabLabel: {
    marginLeft: 4,
    fontSize: 14,
    color: '#6b7280',
  },
  activeTabLabel: {
    color: '#3b82f6',
    fontWeight: '600',
  },
  tabContent: {
    flex: 1,
  },
  priceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    margin: 16,
    borderRadius: 12,
  },
  priceInfo: {
    flex: 1,
  },
  pairSymbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  currentPrice: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  priceChange: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  changeText: {
    marginLeft: 4,
    fontSize: 14,
    fontWeight: '600',
  },
  hexToggle: {
    alignItems: 'center',
  },
  hexLabel: {
    color: '#ffffff',
    fontSize: 12,
    marginBottom: 4,
  },
  chartContainer: {
    margin: 16,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 12,
  },
  tradingPanel: {
    margin: 16,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
  },
  orderTypeContainer: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  orderTypeButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderWidth: 1,
    borderColor: '#d1d5db',
    backgroundColor: '#ffffff',
    marginRight: 8,
    borderRadius: 8,
    alignItems: 'center',
  },
  activeOrderType: {
    backgroundColor: '#3b82f6',
    borderColor: '#3b82f6',
  },
  orderTypeText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
  },
  activeOrderTypeText: {
    color: '#ffffff',
  },
  sideContainer: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  sideButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderWidth: 1,
    marginRight: 8,
    borderRadius: 8,
    alignItems: 'center',
  },
  buyButton: {
    borderColor: '#10b981',
    backgroundColor: '#ffffff',
  },
  sellButton: {
    borderColor: '#ef4444',
    backgroundColor: '#ffffff',
  },
  activeBuy: {
    backgroundColor: '#10b981',
  },
  activeSell: {
    backgroundColor: '#ef4444',
  },
  sideText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
  },
  activeSideText: {
    color: '#ffffff',
  },
  inputContainer: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: '#ffffff',
  },
  venueContainer: {
    flexDirection: 'row',
  },
  venueButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: '#d1d5db',
    backgroundColor: '#ffffff',
    marginRight: 8,
    borderRadius: 6,
    alignItems: 'center',
  },
  activeVenue: {
    backgroundColor: '#3b82f6',
    borderColor: '#3b82f6',
  },
  venueText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6b7280',
  },
  activeVenueText: {
    color: '#ffffff',
  },
  quoteContainer: {
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  quoteTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  quoteRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  quoteLabel: {
    fontSize: 12,
    color: '#6b7280',
  },
  quoteLabelBest: {
    fontSize: 12,
    fontWeight: '600',
    color: '#374151',
  },
  quoteValue: {
    fontSize: 12,
    color: '#374151',
  },
  quoteValueBest: {
    fontSize: 12,
    fontWeight: '600',
    color: '#10b981',
  },
  quoteSavings: {
    fontSize: 12,
    color: '#10b981',
  },
  totalContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  totalLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  totalValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  executeButton: {
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  buyExecuteButton: {
    backgroundColor: '#10b981',
  },
  sellExecuteButton: {
    backgroundColor: '#ef4444',
  },
  disabledButton: {
    backgroundColor: '#9ca3af',
  },
  executeButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  portfolioHeader: {
    padding: 20,
    margin: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  portfolioTitle: {
    fontSize: 16,
    color: '#d1d5db',
    marginBottom: 8,
  },
  portfolioValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  pnlContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  pnlText: {
    marginLeft: 4,
    fontSize: 14,
    fontWeight: '600',
  },
  balanceSection: {
    margin: 16,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
  },
  balanceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  assetName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  assetBalance: {
    fontSize: 16,
    color: '#6b7280',
  },
  ordersContainer: {
    margin: 16,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
  },
  emptyState: {
    textAlign: 'center',
    color: '#9ca3af',
    fontSize: 14,
    paddingVertical: 20,
  },
});

export default HexTradingScreen;