import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const WalletScreen = ({ navigation }: any) => {
  const [refreshing, setRefreshing] = useState(false);
  const [hideBalance, setHideBalance] = useState(false);
  const [selectedWallet, setSelectedWallet] = useState('spot');

  const wallets = [
    { id: 'spot', name: 'Spot Wallet', balance: 125430.50, icon: 'wallet' },
    { id: 'funding', name: 'Funding Wallet', balance: 50000.00, icon: 'bank' },
    { id: 'futures', name: 'Futures Wallet', balance: 75000.00, icon: 'chart-line' },
    { id: 'earn', name: 'Earn Wallet', balance: 30000.00, icon: 'piggy-bank' },
  ];

  const assets = [
    { symbol: 'BTC', name: 'Bitcoin', balance: 2.5, value: 87500, price: 35000, change: 2.3 },
    { symbol: 'ETH', name: 'Ethereum', balance: 15.8, value: 31600, price: 2000, change: -1.2 },
    { symbol: 'USDT', name: 'Tether', balance: 5000, value: 5000, price: 1.0, change: 0.0 },
    { symbol: 'BNB', name: 'Binance Coin', balance: 8.2, value: 1330.5, price: 162.26, change: 4.5 },
  ];

  const onRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 2000);
  };

  const currentWallet = wallets.find(w => w.id === selectedWallet);

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#FF6B00" />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Wallet</Text>
        <TouchableOpacity onPress={() => setHideBalance(!hideBalance)}>
          <Icon
            name={hideBalance ? 'eye-off-outline' : 'eye-outline'}
            size={24}
            color="#FFF"
          />
        </TouchableOpacity>
      </View>

      {/* Wallet Selector */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.walletSelector}
        contentContainerStyle={styles.walletSelectorContent}
      >
        {wallets.map((wallet) => (
          <TouchableOpacity
            key={wallet.id}
            style={[
              styles.walletCard,
              selectedWallet === wallet.id && styles.walletCardActive,
            ]}
            onPress={() => setSelectedWallet(wallet.id)}
          >
            <Icon
              name={wallet.icon}
              size={24}
              color={selectedWallet === wallet.id ? '#FF6B00' : '#999'}
            />
            <Text style={styles.walletName}>{wallet.name}</Text>
            <Text style={styles.walletBalance}>
              {hideBalance ? '****' : `$${wallet.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Total Balance */}
      <View style={styles.totalBalanceCard}>
        <Text style={styles.totalBalanceLabel}>Total Balance</Text>
        <Text style={styles.totalBalanceValue}>
          {hideBalance ? '****' : `$${currentWallet?.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
        </Text>
        <Text style={styles.totalBalanceSubtext}>≈ {hideBalance ? '****' : '2.5 BTC'}</Text>
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Deposit')}
        >
          <View style={[styles.actionIcon, { backgroundColor: '#4CAF5020' }]}>
            <Icon name="plus-circle" size={28} color="#4CAF50" />
          </View>
          <Text style={styles.actionText}>Deposit</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Withdraw')}
        >
          <View style={[styles.actionIcon, { backgroundColor: '#F4433620' }]}>
            <Icon name="minus-circle" size={28} color="#F44336" />
          </View>
          <Text style={styles.actionText}>Withdraw</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Transfer')}
        >
          <View style={[styles.actionIcon, { backgroundColor: '#2196F320' }]}>
            <Icon name="swap-horizontal" size={28} color="#2196F3" />
          </View>
          <Text style={styles.actionText}>Transfer</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('History')}
        >
          <View style={[styles.actionIcon, { backgroundColor: '#FF980020' }]}>
            <Icon name="history" size={28} color="#FF9800" />
          </View>
          <Text style={styles.actionText}>History</Text>
        </TouchableOpacity>
      </View>

      {/* Assets List */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Assets</Text>
          <TouchableOpacity>
            <Text style={styles.seeAll}>See All</Text>
          </TouchableOpacity>
        </View>

        {assets.map((asset, index) => (
          <TouchableOpacity
            key={index}
            style={styles.assetCard}
            onPress={() => navigation.navigate('AssetDetail', { asset })}
          >
            <View style={styles.assetLeft}>
              <View style={styles.assetIcon}>
                <Icon name="bitcoin" size={32} color="#FF6B00" />
              </View>
              <View>
                <Text style={styles.assetSymbol}>{asset.symbol}</Text>
                <Text style={styles.assetName}>{asset.name}</Text>
              </View>
            </View>
            <View style={styles.assetRight}>
              <Text style={styles.assetBalance}>
                {hideBalance ? '****' : asset.balance.toFixed(4)}
              </Text>
              <Text style={styles.assetValue}>
                {hideBalance ? '****' : `$${asset.value.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
              </Text>
              <View style={styles.assetChange}>
                <Icon
                  name={asset.change >= 0 ? 'trending-up' : 'trending-down'}
                  size={14}
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

      {/* Recent Transactions */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Transactions</Text>
          <TouchableOpacity onPress={() => navigation.navigate('History')}>
            <Text style={styles.seeAll}>See All</Text>
          </TouchableOpacity>
        </View>

        {[
          { type: 'Deposit', asset: 'BTC', amount: 0.5, status: 'Completed', time: '2 hours ago' },
          { type: 'Withdraw', asset: 'ETH', amount: 2.0, status: 'Pending', time: '5 hours ago' },
          { type: 'Transfer', asset: 'USDT', amount: 1000, status: 'Completed', time: '1 day ago' },
        ].map((tx, index) => (
          <View key={index} style={styles.transactionCard}>
            <View style={styles.transactionLeft}>
              <View
                style={[
                  styles.transactionIcon,
                  {
                    backgroundColor:
                      tx.type === 'Deposit'
                        ? '#4CAF5020'
                        : tx.type === 'Withdraw'
                        ? '#F4433620'
                        : '#2196F320',
                  },
                ]}
              >
                <Icon
                  name={
                    tx.type === 'Deposit'
                      ? 'plus-circle'
                      : tx.type === 'Withdraw'
                      ? 'minus-circle'
                      : 'swap-horizontal'
                  }
                  size={24}
                  color={
                    tx.type === 'Deposit'
                      ? '#4CAF50'
                      : tx.type === 'Withdraw'
                      ? '#F44336'
                      : '#2196F3'
                  }
                />
              </View>
              <View>
                <Text style={styles.transactionType}>{tx.type}</Text>
                <Text style={styles.transactionTime}>{tx.time}</Text>
              </View>
            </View>
            <View style={styles.transactionRight}>
              <Text style={styles.transactionAmount}>
                {tx.type === 'Withdraw' ? '-' : '+'}{tx.amount} {tx.asset}
              </Text>
              <Text
                style={[
                  styles.transactionStatus,
                  {
                    color: tx.status === 'Completed' ? '#4CAF50' : '#FF9800',
                  },
                ]}
              >
                {tx.status}
              </Text>
            </View>
          </View>
        ))}
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
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFF',
  },
  walletSelector: {
    paddingHorizontal: 24,
    marginBottom: 24,
  },
  walletSelectorContent: {
    gap: 12,
  },
  walletCard: {
    backgroundColor: '#1A1F3A',
    borderRadius: 12,
    padding: 16,
    minWidth: 140,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  walletCardActive: {
    borderColor: '#FF6B00',
  },
  walletName: {
    fontSize: 12,
    color: '#999',
    marginTop: 8,
  },
  walletBalance: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFF',
    marginTop: 4,
  },
  totalBalanceCard: {
    backgroundColor: '#1A1F3A',
    borderRadius: 16,
    padding: 24,
    marginHorizontal: 24,
    marginBottom: 24,
    alignItems: 'center',
  },
  totalBalanceLabel: {
    fontSize: 14,
    color: '#999',
    marginBottom: 8,
  },
  totalBalanceValue: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#FFF',
    marginBottom: 4,
  },
  totalBalanceSubtext: {
    fontSize: 14,
    color: '#666',
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 24,
    marginBottom: 24,
  },
  actionButton: {
    alignItems: 'center',
  },
  actionIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  actionText: {
    fontSize: 12,
    color: '#FFF',
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
  assetBalance: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFF',
  },
  assetValue: {
    fontSize: 14,
    color: '#999',
    marginTop: 2,
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
  transactionCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1A1F3A',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  transactionLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  transactionIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  transactionType: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFF',
  },
  transactionTime: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  transactionRight: {
    alignItems: 'flex-end',
  },
  transactionAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFF',
  },
  transactionStatus: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 2,
  },
});

export default WalletScreen;