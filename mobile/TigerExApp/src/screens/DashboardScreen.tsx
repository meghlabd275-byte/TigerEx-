import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const { width } = Dimensions.get('window');

const DashboardScreen = ({ navigation }: any) => {
  const [refreshing, setRefreshing] = useState(false);
  const [portfolioData, setPortfolioData] = useState({
    totalValue: 125430.50,
    change24h: 3.45,
    changeAmount: 4180.25,
  });

  const [topAssets, setTopAssets] = useState([
    { symbol: 'BTC', name: 'Bitcoin', balance: 2.5, value: 87500, change: 2.3, icon: 'bitcoin' },
    { symbol: 'ETH', name: 'Ethereum', balance: 15.8, value: 31600, change: -1.2, icon: 'ethereum' },
    { symbol: 'USDT', name: 'Tether', balance: 5000, value: 5000, change: 0.0, icon: 'currency-usd' },
    { symbol: 'BNB', name: 'Binance Coin', balance: 8.2, value: 1330.5, change: 4.5, icon: 'alpha-b-circle' },
  ]);

  const [quickActions] = useState([
    { id: 1, title: 'Deposit', icon: 'plus-circle', color: '#4CAF50', route: 'Deposit' },
    { id: 2, title: 'Withdraw', icon: 'minus-circle', color: '#F44336', route: 'Withdraw' },
    { id: 3, title: 'Trade', icon: 'swap-horizontal', color: '#2196F3', route: 'Trading' },
    { id: 4, title: 'Earn', icon: 'chart-line', color: '#FF9800', route: 'Earn' },
  ]);

  const chartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        data: [118000, 120500, 119800, 122000, 121500, 123800, 125430],
        color: (opacity = 1) => `rgba(255, 107, 0, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  const onRefresh = async () => {
    setRefreshing(true);
    // Simulate API call
    setTimeout(() => {
      setRefreshing(false);
    }, 2000);
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#FF6B00" />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Good Morning</Text>
          <Text style={styles.userName}>John Doe</Text>
        </View>
        <View style={styles.headerIcons}>
          <TouchableOpacity style={styles.iconButton} onPress={() => navigation.navigate('Notifications')}>
            <Icon name="bell-outline" size={24} color="#FFF" />
            <View style={styles.badge}>
              <Text style={styles.badgeText}>3</Text>
            </View>
          </TouchableOpacity>
          <TouchableOpacity style={styles.iconButton} onPress={() => navigation.navigate('Settings')}>
            <Icon name="cog-outline" size={24} color="#FFF" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Portfolio Value Card */}
      <View style={styles.portfolioCard}>
        <Text style={styles.portfolioLabel}>Total Portfolio Value</Text>
        <Text style={styles.portfolioValue}>
          ${portfolioData.totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </Text>
        <View style={styles.portfolioChange}>
          <Icon
            name={portfolioData.change24h >= 0 ? 'trending-up' : 'trending-down'}
            size={20}
            color={portfolioData.change24h >= 0 ? '#4CAF50' : '#F44336'}
          />
          <Text
            style={[
              styles.changeText,
              { color: portfolioData.change24h >= 0 ? '#4CAF50' : '#F44336' },
            ]}
          >
            {portfolioData.change24h >= 0 ? '+' : ''}
            {portfolioData.change24h}% (${portfolioData.changeAmount.toFixed(2)})
          </Text>
        </View>
        <Text style={styles.timeframe}>Last 24 hours</Text>

        {/* Chart */}
        <LineChart
          data={chartData}
          width={width - 80}
          height={180}
          chartConfig={{
            backgroundColor: '#1A1F3A',
            backgroundGradientFrom: '#1A1F3A',
            backgroundGradientTo: '#1A1F3A',
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(255, 107, 0, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
            style: {
              borderRadius: 16,
            },
            propsForDots: {
              r: '4',
              strokeWidth: '2',
              stroke: '#FF6B00',
            },
          }}
          bezier
          style={styles.chart}
        />
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.quickActionsGrid}>
          {quickActions.map((action) => (
            <TouchableOpacity
              key={action.id}
              style={styles.quickActionCard}
              onPress={() => navigation.navigate(action.route)}
            >
              <View style={[styles.quickActionIcon, { backgroundColor: action.color + '20' }]}>
                <Icon name={action.icon} size={28} color={action.color} />
              </View>
              <Text style={styles.quickActionText}>{action.title}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Top Assets */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Top Assets</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Portfolio')}>
            <Text style={styles.seeAll}>See All</Text>
          </TouchableOpacity>
        </View>
        {topAssets.map((asset, index) => (
          <TouchableOpacity
            key={index}
            style={styles.assetCard}
            onPress={() => navigation.navigate('AssetDetail', { asset })}
          >
            <View style={styles.assetLeft}>
              <View style={styles.assetIcon}>
                <Icon name={asset.icon} size={32} color="#FF6B00" />
              </View>
              <View>
                <Text style={styles.assetSymbol}>{asset.symbol}</Text>
                <Text style={styles.assetName}>{asset.name}</Text>
              </View>
            </View>
            <View style={styles.assetRight}>
              <Text style={styles.assetValue}>
                ${asset.value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </Text>
              <View style={styles.assetChange}>
                <Icon
                  name={asset.change >= 0 ? 'trending-up' : 'trending-down'}
                  size={16}
                  color={asset.change >= 0 ? '#4CAF50' : '#F44336'}
                />
                <Text
                  style={[
                    styles.assetChangeText,
                    { color: asset.change >= 0 ? '#4CAF50' : '#F44336' },
                  ]}
                >
                  {asset.change >= 0 ? '+' : ''}
                  {asset.change}%
                </Text>
              </View>
            </View>
          </TouchableOpacity>
        ))}
      </View>

      {/* Market Overview */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Market Overview</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Markets')}>
            <Text style={styles.seeAll}>See All</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.marketStats}>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>24h Volume</Text>
            <Text style={styles.statValue}>$2.5T</Text>
            <Text style={styles.statChange}>+12.5%</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>Market Cap</Text>
            <Text style={styles.statValue}>$1.8T</Text>
            <Text style={styles.statChange}>+5.2%</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E27',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 24,
    paddingTop: 60,
  },
  greeting: {
    fontSize: 14,
    color: '#999',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFF',
    marginTop: 4,
  },
  headerIcons: {
    flexDirection: 'row',
    gap: 16,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1A1F3A',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  badge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: '#F44336',
    borderRadius: 10,
    width: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: '#FFF',
    fontSize: 10,
    fontWeight: 'bold',
  },
  portfolioCard: {
    backgroundColor: '#1A1F3A',
    borderRadius: 16,
    padding: 24,
    marginHorizontal: 24,
    marginBottom: 24,
  },
  portfolioLabel: {
    fontSize: 14,
    color: '#999',
    marginBottom: 8,
  },
  portfolioValue: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#FFF',
    marginBottom: 8,
  },
  portfolioChange: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  changeText: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 4,
  },
  timeframe: {
    fontSize: 12,
    color: '#666',
    marginBottom: 16,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  section: {
    paddingHorizontal: 24,
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFF',
  },
  seeAll: {
    fontSize: 14,
    color: '#FF6B00',
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  quickActionCard: {
    width: (width - 72) / 4,
    backgroundColor: '#1A1F3A',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  quickActionIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  quickActionText: {
    fontSize: 12,
    color: '#FFF',
    textAlign: 'center',
  },
  assetCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1A1F3A',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  assetLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  assetIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#FF6B0020',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  assetSymbol: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFF',
  },
  assetName: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  assetRight: {
    alignItems: 'flex-end',
  },
  assetValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFF',
  },
  assetChange: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  assetChangeText: {
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  marketStats: {
    flexDirection: 'row',
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#1A1F3A',
    borderRadius: 12,
    padding: 16,
  },
  statLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 8,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFF',
    marginBottom: 4,
  },
  statChange: {
    fontSize: 14,
    color: '#4CAF50',
    fontWeight: '600',
  },
});

export default DashboardScreen;