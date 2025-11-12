import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  FlatList,
  RefreshControl,
  Dimensions,
  Image,
  Modal,
  ActivityIndicator,
} from 'react-native';
import { LineChart, BarChart, CandlestickChart } from 'react-native-charts-wrapper';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { Icon } from 'react-native-elements';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuthentication } from '../hooks/useAuthentication';

const { width, height } = Dimensions.get('window');

interface Trade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: string;
  price: string;
  timestamp: string;
  status: 'pending' | 'filled' | 'cancelled';
}

interface Portfolio {
  totalValue: string;
  pnl24h: string;
  pnlPercentage: string;
  balances: Array<{
    symbol: string;
    balance: string;
    value: string;
  }>;
}

interface MarketData {
  symbol: string;
  price: string;
  change24h: string;
  volume24h: string;
  high24h: string;
  low24h: string;
}

interface OrderBookEntry {
  price: string;
  quantity: string;
  total: string;
}

const CompleteMobileTradingApp: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'markets' | 'portfolio' | 'trading' | 'orders'>('markets');
  const [selectedSymbol, setSelectedSymbol] = useState<string>('BTC/USDT');
  const [chartData, setChartData] = useState<any>(null);
  const [orderBook, setOrderBook] = useState<{ bids: OrderBookEntry[], asks: OrderBookEntry[] }>({ bids: [], asks: [] });
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [orderQuantity, setOrderQuantity] = useState<string>('');
  const [orderPrice, setOrderPrice] = useState<string>('');
  const [showOrderModal, setShowOrderModal] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [chartInterval, setChartInterval] = useState<string>('1h');

  const { user, isAuthenticated, login, logout } = useAuthentication();
  const { isConnected, sendMessage, lastMessage } = useWebSocket('wss://api.tigerex.com/ws');

  // Initialize app
  useEffect(() => {
    if (isAuthenticated) {
      loadMarketData();
      loadPortfolio();
      loadTrades();
      loadOrderBook(selectedSymbol);
    }
  }, [isAuthenticated, selectedSymbol]);

  // WebSocket message handling
  useEffect(() => {
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data);
      handleWebSocketMessage(data);
    }
  }, [lastMessage]);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'market_update':
        updateMarketData(data.payload);
        break;
      case 'trade_update':
        updateTrades(data.payload);
        break;
      case 'order_book_update':
        updateOrderBook(data.payload);
        break;
      case 'portfolio_update':
        setPortfolio(data.payload);
        break;
    }
  };

  const loadMarketData = async () => {
    try {
      setLoading(true);
      // Simulate API call
      const symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT'];
      const data = symbols.map(symbol => ({
        symbol,
        price: (Math.random() * 50000 + 100).toFixed(2),
        change24h: (Math.random() * 20 - 10).toFixed(2),
        volume24h: (Math.random() * 1000000000).toFixed(0),
        high24h: (Math.random() * 55000 + 100).toFixed(2),
        low24h: (Math.random() * 45000 + 90).toFixed(2),
      }));
      setMarketData(data);
    } catch (error) {
      console.error('Error loading market data:', error);
      Alert.alert('Error', 'Failed to load market data');
    } finally {
      setLoading(false);
    }
  };

  const loadPortfolio = async () => {
    try {
      // Simulate portfolio data
      const portfolioData: Portfolio = {
        totalValue: '50000.00',
        pnl24h: '500.00',
        pnlPercentage: '1.00',
        balances: [
          { symbol: 'USDT', balance: '10000.00', value: '10000.00' },
          { symbol: 'BTC', balance: '0.5', value: '25000.00' },
          { symbol: 'ETH', balance: '5.0', value: '10000.00' },
          { symbol: 'BNB', balance: '20.0', value: '5000.00' },
        ]
      };
      setPortfolio(portfolioData);
    } catch (error) {
      console.error('Error loading portfolio:', error);
    }
  };

  const loadTrades = async () => {
    try {
      // Simulate trade history
      const tradeData: Trade[] = Array.from({ length: 20 }, (_, i) => ({
        id: `trade_${i}`,
        symbol: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'][Math.floor(Math.random() * 3)],
        side: Math.random() > 0.5 ? 'buy' : 'sell',
        quantity: (Math.random() * 10 + 0.1).toFixed(4),
        price: (Math.random() * 50000 + 100).toFixed(2),
        timestamp: new Date(Date.now() - i * 3600000).toISOString(),
        status: 'filled',
      }));
      setTrades(tradeData);
    } catch (error) {
      console.error('Error loading trades:', error);
    }
  };

  const loadOrderBook = async (symbol: string) => {
    try {
      // Simulate order book data
      const basePrice = Math.random() * 50000 + 100;
      const bids: OrderBookEntry[] = Array.from({ length: 15 }, (_, i) => ({
        price: (basePrice - i * 10).toFixed(2),
        quantity: (Math.random() * 5 + 0.1).toFixed(4),
        total: ((basePrice - i * 10) * (Math.random() * 5 + 0.1)).toFixed(2),
      }));
      const asks: OrderBookEntry[] = Array.from({ length: 15 }, (_, i) => ({
        price: (basePrice + i * 10).toFixed(2),
        quantity: (Math.random() * 5 + 0.1).toFixed(4),
        total: ((basePrice + i * 10) * (Math.random() * 5 + 0.1)).toFixed(2),
      }));
      setOrderBook({ bids, asks });
    } catch (error) {
      console.error('Error loading order book:', error);
    }
  };

  const loadChartData = async (symbol: string, interval: string) => {
    try {
      // Simulate chart data
      const dataPoints = Array.from({ length: 100 }, (_, i) => ({
        x: i,
        y: Math.random() * 1000 + 45000,
      }));
      setChartData({
        dataSets: [{
          values: dataPoints,
          label: symbol,
          config: {
            color: '#4CAF50',
            drawCircles: false,
            drawValues: false,
          },
        }],
      });
    } catch (error) {
      console.error('Error loading chart data:', error);
    }
  };

  const placeOrder = async () => {
    if (!orderQuantity) {
      Alert.alert('Error', 'Please enter quantity');
      return;
    }
    if (orderType === 'limit' && !orderPrice) {
      Alert.alert('Error', 'Please enter price for limit order');
      return;
    }

    try {
      setLoading(true);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      
      // Simulate order placement
      const newTrade: Trade = {
        id: `trade_${Date.now()}`,
        symbol: selectedSymbol,
        side: orderSide,
        quantity: orderQuantity,
        price: orderType === 'market' ? marketData.find(m => m.symbol === selectedSymbol)?.price || '0' : orderPrice,
        timestamp: new Date().toISOString(),
        status: 'filled',
      };

      setTrades([newTrade, ...trades]);
      setShowOrderModal(false);
      setOrderQuantity('');
      setOrderPrice('');
      
      Alert.alert('Success', 'Order placed successfully');
    } catch (error) {
      console.error('Error placing order:', error);
      Alert.alert('Error', 'Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadMarketData();
    loadPortfolio();
    loadTrades();
    loadOrderBook(selectedSymbol);
    loadChartData(selectedSymbol, chartInterval);
    setRefreshing(false);
  }, [selectedSymbol, chartInterval]);

  const renderMarketItem = ({ item }: { item: MarketData }) => (
    <TouchableOpacity
      style={styles.marketItem}
      onPress={() => {
        setSelectedSymbol(item.symbol);
        loadOrderBook(item.symbol);
        loadChartData(item.symbol, chartInterval);
        setActiveTab('trading');
      }}
    >
      <View style={styles.marketItemHeader}>
        <Text style={styles.symbolText}>{item.symbol}</Text>
        <Text style={styles.priceText}>${item.price}</Text>
      </View>
      <View style={styles.marketItemDetails}>
        <Text style={[
          styles.changeText,
          { color: parseFloat(item.change24h) >= 0 ? '#4CAF50' : '#F44336' }
        ]}>
          {parseFloat(item.change24h) >= 0 ? '+' : ''}{item.change24h}%
        </Text>
        <Text style={styles.volumeText}>Vol: ${item.volume24h}</Text>
      </View>
    </TouchableOpacity>
  );

  const renderTradeItem = ({ item }: { item: Trade }) => (
    <View style={styles.tradeItem}>
      <View style={styles.tradeHeader}>
        <Text style={styles.tradeSymbol}>{item.symbol}</Text>
        <View style={[
          styles.tradeSideBadge,
          { backgroundColor: item.side === 'buy' ? '#4CAF50' : '#F44336' }
        ]}>
          <Text style={styles.tradeSideText}>{item.side.toUpperCase()}</Text>
        </View>
      </View>
      <View style={styles.tradeDetails}>
        <Text style={styles.tradeQuantity}>{item.quantity}</Text>
        <Text style={styles.tradePrice}>${item.price}</Text>
        <Text style={styles.tradeTime}>
          {new Date(item.timestamp).toLocaleTimeString()}
        </Text>
      </View>
    </View>
  );

  const renderOrderBookEntry = ({ item, index, type }: { item: OrderBookEntry; index: number; type: 'bid' | 'ask' }) => (
    <View style={styles.orderBookRow}>
      <Text style={[
        styles.orderBookPrice,
        { color: type === 'bid' ? '#4CAF50' : '#F44336' }
      ]}>
        ${item.price}
      </Text>
      <Text style={styles.orderBookQuantity}>{item.quantity}</Text>
      <Text style={styles.orderBookTotal}>{item.total}</Text>
    </View>
  );

  const renderMarketsTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.marketHeader}>
        <Text style={styles.marketTitle}>Markets</Text>
        <TouchableOpacity onPress={onRefresh}>
          <Icon name="refresh" type="material" color="#fff" />
        </TouchableOpacity>
      </View>
      <FlatList
        data={marketData}
        renderItem={renderMarketItem}
        keyExtractor={(item) => item.symbol}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      />
    </View>
  );

  const renderPortfolioTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.portfolioHeader}>
        <Text style={styles.portfolioTitle}>Portfolio</Text>
      </View>
      <LinearGradient
        colors={['#1E88E5', '#1565C0']}
        style={styles.portfolioCard}
      >
        <Text style={styles.totalValueText}>${portfolio?.totalValue || '0.00'}</Text>
        <Text style={styles.pnlText}>
          {portfolio?.pnl24h.startsWith('-') ? '' : '+'}{portfolio?.pnl24h || '0.00'} 
          ({portfolio?.pnlPercentage.startsWith('-') ? '' : '+'}{portfolio?.pnlPercentage || '0.00'}%)
        </Text>
      </LinearGradient>
      <Text style={styles.balancesTitle}>Balances</Text>
      <FlatList
        data={portfolio?.balances || []}
        renderItem={({ item }) => (
          <View style={styles.balanceItem}>
            <Text style={styles.balanceSymbol}>{item.symbol}</Text>
            <Text style={styles.balanceAmount}>{item.balance}</Text>
            <Text style={styles.balanceValue}>${item.value}</Text>
          </View>
        )}
        keyExtractor={(item) => item.symbol}
      />
    </View>
  );

  const renderTradingTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.tradingHeader}>
        <TouchableOpacity onPress={() => setActiveTab('markets')}>
          <Icon name="arrow-back" type="material" color="#fff" />
        </TouchableOpacity>
        <Text style={styles.tradingTitle}>{selectedSymbol}</Text>
        <TouchableOpacity onPress={() => setShowOrderModal(true)}>
          <Icon name="add" type="material" color="#fff" />
        </TouchableOpacity>
      </View>
      
      <View style={styles.chartContainer}>
        {chartData && (
          <LineChart
            style={styles.chart}
            data={chartData}
            chartDescription={{ text: '' }}
            legend={{ enabled: false }}
            xAxis={{ enabled: false }}
            yAxis={{ left: { enabled: false }, right: { enabled: false } }}
            drawGridBackground={false}
            borderColor="#333"
            borderWidth={1}
          />
        )}
      </View>

      <View style={styles.orderBookContainer}>
        <View style={styles.orderBookHeader}>
          <Text style={styles.orderBookTitle}>Order Book</Text>
        </View>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View>
            <Text style={styles.orderBookHeaders}>Price</Text>
            <Text style={styles.orderBookHeaders}>Quantity</Text>
            <Text style={styles.orderBookHeaders}>Total</Text>
          </View>
        </ScrollView>
        <ScrollView>
          {orderBook.asks.slice().reverse().map((item, index) => (
            renderOrderBookEntry({ item, index, type: 'ask' })
          ))}
          <View style={styles.spreadRow}>
            <Text style={styles.spreadText}>
              Spread: ${(parseFloat(orderBook.asks[0]?.price || '0') - parseFloat(orderBook.bids[0]?.price || '0')).toFixed(2)}
            </Text>
          </View>
          {orderBook.bids.map((item, index) => (
            renderOrderBookEntry({ item, index, type: 'bid' })
          ))}
        </ScrollView>
      </View>
    </View>
  );

  const renderOrdersTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.ordersHeader}>
        <Text style={styles.ordersTitle}>Trade History</Text>
        <TouchableOpacity onPress={onRefresh}>
          <Icon name="refresh" type="material" color="#fff" />
        </TouchableOpacity>
      </View>
      <FlatList
        data={trades}
        renderItem={renderTradeItem}
        keyExtractor={(item) => item.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      />
    </View>
  );

  if (!isAuthenticated) {
    return (
      <View style={styles.loginContainer}>
        <LinearGradient colors={['#1E88E5', '#1565C0']} style={styles.loginGradient}>
          <Text style={styles.loginTitle}>TigerEx</Text>
          <Text style={styles.loginSubtitle}>Professional Trading Platform</Text>
          <TouchableOpacity
            style={styles.loginButton}
            onPress={() => login('demo@tigerex.com', 'password')}
          >
            <Text style={styles.loginButtonText}>Login</Text>
          </TouchableOpacity>
        </LinearGradient>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>TigerEx</Text>
        <View style={styles.headerIcons}>
          <TouchableOpacity>
            <Icon name="notifications" type="material" color="#fff" />
          </TouchableOpacity>
          <TouchableOpacity onPress={logout}>
            <Icon name="logout" type="material" color="#fff" />
          </TouchableOpacity>
        </View>
      </View>

      {activeTab === 'markets' && renderMarketsTab()}
      {activeTab === 'portfolio' && renderPortfolioTab()}
      {activeTab === 'trading' && renderTradingTab()}
      {activeTab === 'orders' && renderOrdersTab()}

      <View style={styles.tabBar}>
        {[
          { key: 'markets', icon: 'trending-up', label: 'Markets' },
          { key: 'portfolio', icon: 'account-balance-wallet', label: 'Portfolio' },
          { key: 'trading', icon: 'show-chart', label: 'Trading' },
          { key: 'orders', icon: 'history', label: 'Orders' },
        ].map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[
              styles.tabItem,
              activeTab === tab.key && styles.activeTab
            ]}
            onPress={() => setActiveTab(tab.key as any)}
          >
            <Icon
              name={tab.icon}
              type="material"
              color={activeTab === tab.key ? '#1E88E5' : '#666'}
              size={24}
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

      <Modal
        visible={showOrderModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowOrderModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.orderModal}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Place Order</Text>
              <TouchableOpacity onPress={() => setShowOrderModal(false)}>
                <Icon name="close" type="material" color="#333" />
              </TouchableOpacity>
            </View>
            
            <View style={styles.orderTypeSelector}>
              <TouchableOpacity
                style={[
                  styles.orderTypeButton,
                  orderSide === 'buy' && styles.buyButton
                ]}
                onPress={() => setOrderSide('buy')}
              >
                <Text style={[
                  styles.orderTypeText,
                  orderSide === 'buy' && styles.buyButtonText
                ]}>
                  Buy
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.orderTypeButton,
                  orderSide === 'sell' && styles.sellButton
                ]}
                onPress={() => setOrderSide('sell')}
              >
                <Text style={[
                  styles.orderTypeText,
                  orderSide === 'sell' && styles.sellButtonText
                ]}>
                  Sell
                </Text>
              </TouchableOpacity>
            </View>

            <View style={styles.orderTypeSelector}>
              <TouchableOpacity
                style={[
                  styles.orderTypeButton,
                  orderType === 'market' && styles.marketButton
                ]}
                onPress={() => setOrderType('market')}
              >
                <Text style={styles.orderTypeText}>Market</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.orderTypeButton,
                  orderType === 'limit' && styles.limitButton
                ]}
                onPress={() => setOrderType('limit')}
              >
                <Text style={styles.orderTypeText}>Limit</Text>
              </TouchableOpacity>
            </View>

            <TextInput
              style={styles.quantityInput}
              placeholder="Quantity"
              value={orderQuantity}
              onChangeText={setOrderQuantity}
              keyboardType="numeric"
              placeholderTextColor="#666"
            />

            {orderType === 'limit' && (
              <TextInput
                style={styles.priceInput}
                placeholder="Price"
                value={orderPrice}
                onChangeText={setOrderPrice}
                keyboardType="numeric"
                placeholderTextColor="#666"
              />
            )}

            <TouchableOpacity
              style={[
                styles.placeOrderButton,
                orderSide === 'buy' ? styles.buyButton : styles.sellButton
              ]}
              onPress={placeOrder}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.placeOrderButtonText}>
                  {orderSide === 'buy' ? 'Buy' : 'Sell'} {selectedSymbol}
                </Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 10,
    backgroundColor: '#1E1E1E',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerIcons: {
    flexDirection: 'row',
    gap: 15,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#1E1E1E',
    borderTopWidth: 1,
    borderTopColor: '#333',
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 10,
  },
  activeTab: {
    borderTopWidth: 2,
    borderTopColor: '#1E88E5',
  },
  tabLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  activeTabLabel: {
    color: '#1E88E5',
  },
  tabContent: {
    flex: 1,
    backgroundColor: '#121212',
  },
  loginContainer: {
    flex: 1,
  },
  loginGradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loginTitle: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 10,
  },
  loginSubtitle: {
    fontSize: 16,
    color: '#fff',
    marginBottom: 40,
    opacity: 0.8,
  },
  loginButton: {
    backgroundColor: '#fff',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 25,
  },
  loginButtonText: {
    color: '#1E88E5',
    fontSize: 16,
    fontWeight: 'bold',
  },
  marketHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#1E1E1E',
  },
  marketTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  marketItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  marketItemHeader: {
    flex: 1,
  },
  symbolText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  priceText: {
    fontSize: 14,
    color: '#fff',
    marginTop: 4,
  },
  marketItemDetails: {
    alignItems: 'flex-end',
  },
  changeText: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  volumeText: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  portfolioHeader: {
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#1E1E1E',
  },
  portfolioTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  portfolioCard: {
    margin: 20,
    padding: 30,
    borderRadius: 15,
    alignItems: 'center',
  },
  totalValueText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
  },
  pnlText: {
    fontSize: 16,
    color: '#fff',
    marginTop: 8,
    opacity: 0.8,
  },
  balancesTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    paddingHorizontal: 20,
    marginBottom: 15,
  },
  balanceItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  balanceSymbol: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  balanceAmount: {
    fontSize: 14,
    color: '#fff',
  },
  balanceValue: {
    fontSize: 14,
    color: '#666',
  },
  tradingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#1E1E1E',
  },
  tradingTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  chartContainer: {
    height: 250,
    backgroundColor: '#1E1E1E',
    marginHorizontal: 20,
    marginVertical: 10,
    borderRadius: 10,
    padding: 10,
  },
  chart: {
    flex: 1,
  },
  orderBookContainer: {
    flex: 1,
    backgroundColor: '#1E1E1E',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 10,
    padding: 15,
  },
  orderBookHeader: {
    marginBottom: 15,
  },
  orderBookTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  orderBookHeaders: {
    fontSize: 12,
    color: '#666',
    marginBottom: 10,
  },
  orderBookRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  orderBookPrice: {
    fontSize: 12,
    fontWeight: 'bold',
    flex: 1,
  },
  orderBookQuantity: {
    fontSize: 12,
    color: '#fff',
    flex: 1,
    textAlign: 'center',
  },
  orderBookTotal: {
    fontSize: 12,
    color: '#666',
    flex: 1,
    textAlign: 'right',
  },
  spreadRow: {
    alignItems: 'center',
    paddingVertical: 8,
    marginVertical: 4,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#333',
  },
  spreadText: {
    fontSize: 12,
    color: '#1E88E5',
    fontWeight: 'bold',
  },
  ordersHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#1E1E1E',
  },
  ordersTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  tradeItem: {
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  tradeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  tradeSymbol: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  tradeSideBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  tradeSideText: {
    fontSize: 10,
    color: '#fff',
    fontWeight: 'bold',
  },
  tradeDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  tradeQuantity: {
    fontSize: 14,
    color: '#fff',
  },
  tradePrice: {
    fontSize: 14,
    color: '#666',
  },
  tradeTime: {
    fontSize: 12,
    color: '#666',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'flex-end',
  },
  orderModal: {
    backgroundColor: '#1E1E1E',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  orderTypeSelector: {
    flexDirection: 'row',
    marginBottom: 20,
    backgroundColor: '#333',
    borderRadius: 25,
    padding: 4,
  },
  orderTypeButton: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 20,
    alignItems: 'center',
  },
  buyButton: {
    backgroundColor: '#4CAF50',
  },
  sellButton: {
    backgroundColor: '#F44336',
  },
  marketButton: {
    backgroundColor: '#1E88E5',
  },
  limitButton: {
    backgroundColor: '#FF9800',
  },
  orderTypeText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#fff',
  },
  buyButtonText: {
    color: '#fff',
  },
  sellButtonText: {
    color: '#fff',
  },
  quantityInput: {
    backgroundColor: '#333',
    color: '#fff',
    fontSize: 16,
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
  },
  priceInput: {
    backgroundColor: '#333',
    color: '#fff',
    fontSize: 16,
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
  },
  placeOrderButton: {
    paddingVertical: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  placeOrderButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
});

export default CompleteMobileTradingApp;