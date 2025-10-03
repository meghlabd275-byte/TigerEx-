/**
 * TigerEx Mobile - P2P Trading Screen
 * Peer-to-peer trading marketplace
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  FlatList,
  TextInput,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

export default function P2PScreen({navigation}) {
  const [selectedTab, setSelectedTab] = useState('buy');
  const [selectedAsset, setSelectedAsset] = useState('USDT');
  const [selectedPayment, setSelectedPayment] = useState('all');
  const [amount, setAmount] = useState('');

  const p2pOffers = [
    {
      id: '1',
      type: 'sell',
      merchant: 'CryptoKing',
      rating: 4.9,
      trades: 1234,
      price: '1.002',
      available: '50,000',
      limit: '100-10,000',
      payment: ['Bank Transfer', 'PayPal'],
      completion: '15 min',
      verified: true,
    },
    {
      id: '2',
      type: 'sell',
      merchant: 'TradeMaster',
      rating: 4.8,
      trades: 856,
      price: '1.001',
      available: '25,000',
      limit: '500-5,000',
      payment: ['Wise', 'Revolut'],
      completion: '10 min',
      verified: true,
    },
    {
      id: '3',
      type: 'sell',
      merchant: 'QuickTrade',
      rating: 4.7,
      trades: 432,
      price: '1.003',
      available: '75,000',
      limit: '200-15,000',
      payment: ['Bank Transfer', 'Cash App'],
      completion: '20 min',
      verified: false,
    },
  ];

  const assets = ['USDT', 'BTC', 'ETH', 'BNB', 'USDC'];
  const paymentMethods = ['all', 'Bank Transfer', 'PayPal', 'Wise', 'Cash App'];

  const renderP2POffer = ({item}) => (
    <View style={styles.offerCard}>
      <View style={styles.offerHeader}>
        <View style={styles.merchantInfo}>
          <View style={styles.merchantName}>
            <Text style={styles.merchantText}>{item.merchant}</Text>
            {item.verified && (
              <Icon name="check-decagram" size={16} color="#4CAF50" />
            )}
          </View>
          <View style={styles.merchantStats}>
            <Icon name="star" size={12} color="#FFD700" />
            <Text style={styles.ratingText}>{item.rating}</Text>
            <Text style={styles.tradesText}>({item.trades} trades)</Text>
          </View>
        </View>
        <View style={styles.priceInfo}>
          <Text style={styles.priceText}>${item.price}</Text>
          <Text style={styles.priceLabel}>per {selectedAsset}</Text>
        </View>
      </View>

      <View style={styles.offerDetails}>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Available:</Text>
          <Text style={styles.detailValue}>{item.available} {selectedAsset}</Text>
        </View>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Limit:</Text>
          <Text style={styles.detailValue}>${item.limit}</Text>
        </View>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Payment:</Text>
          <View style={styles.paymentMethods}>
            {item.payment.map((method, index) => (
              <View key={index} style={styles.paymentBadge}>
                <Text style={styles.paymentText}>{method}</Text>
              </View>
            ))}
          </View>
        </View>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Completion:</Text>
          <Text style={styles.detailValue}>{item.completion}</Text>
        </View>
      </View>

      <TouchableOpacity
        style={[
          styles.tradeButton,
          selectedTab === 'buy' ? styles.buyButton : styles.sellButton,
        ]}
        onPress={() => handleTrade(item)}>
        <Text style={styles.tradeButtonText}>
          {selectedTab === 'buy' ? 'Buy' : 'Sell'} {selectedAsset}
        </Text>
      </TouchableOpacity>
    </View>
  );

  const handleTrade = (offer) => {
    Alert.alert(
      'P2P Trade',
      `${selectedTab === 'buy' ? 'Buy' : 'Sell'} ${selectedAsset} with ${offer.merchant}?`,
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Continue',
          onPress: () => Alert.alert('Success', 'Trade initiated successfully!'),
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>P2P Trading</Text>
        <TouchableOpacity>
          <Icon name="history" size={24} color="#333" />
        </TouchableOpacity>
      </View>

      {/* Buy/Sell Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'buy' && styles.buyTab]}
          onPress={() => setSelectedTab('buy')}>
          <Text
            style={[
              styles.tabText,
              selectedTab === 'buy' && styles.buyTabText,
            ]}>
            Buy
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'sell' && styles.sellTab]}
          onPress={() => setSelectedTab('sell')}>
          <Text
            style={[
              styles.tabText,
              selectedTab === 'sell' && styles.sellTabText,
            ]}>
            Sell
          </Text>
        </TouchableOpacity>
      </View>

      {/* Filters */}
      <View style={styles.filtersContainer}>
        {/* Asset Selection */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.assetFilter}>
          {assets.map(asset => (
            <TouchableOpacity
              key={asset}
              style={[
                styles.assetButton,
                selectedAsset === asset && styles.assetButtonActive,
              ]}
              onPress={() => setSelectedAsset(asset)}>
              <Text
                style={[
                  styles.assetText,
                  selectedAsset === asset && styles.assetTextActive,
                ]}>
                {asset}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Payment Method Filter */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.paymentFilter}>
          {paymentMethods.map(method => (
            <TouchableOpacity
              key={method}
              style={[
                styles.paymentButton,
                selectedPayment === method && styles.paymentButtonActive,
              ]}
              onPress={() => setSelectedPayment(method)}>
              <Text
                style={[
                  styles.paymentButtonText,
                  selectedPayment === method && styles.paymentButtonTextActive,
                ]}>
                {method === 'all' ? 'All Payments' : method}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Amount Input */}
        <View style={styles.amountContainer}>
          <Text style={styles.amountLabel}>Amount (USD)</Text>
          <TextInput
            style={styles.amountInput}
            placeholder="Enter amount..."
            value={amount}
            onChangeText={setAmount}
            keyboardType="decimal-pad"
            placeholderTextColor="#999"
          />
        </View>
      </View>

      {/* Market Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>24h Volume</Text>
          <Text style={styles.statValue}>$12.5M</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Active Orders</Text>
          <Text style={styles.statValue}>1,234</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Avg Price</Text>
          <Text style={styles.statValue}>$1.002</Text>
        </View>
      </View>

      {/* Offers List */}
      <FlatList
        data={p2pOffers}
        renderItem={renderP2POffer}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.offersList}
        showsVerticalScrollIndicator={false}
      />

      {/* Create Order Button */}
      <TouchableOpacity style={styles.createOrderButton}>
        <Icon name="plus" size={20} color="#fff" />
        <Text style={styles.createOrderText}>Create Order</Text>
      </TouchableOpacity>

      {/* Bottom Info */}
      <View style={styles.bottomInfo}>
        <TouchableOpacity style={styles.infoButton}>
          <Icon name="shield-check" size={20} color="#4CAF50" />
          <Text style={styles.infoText}>Secure P2P Trading</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#fff',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    marginHorizontal: 15,
    marginTop: 15,
    borderRadius: 8,
    padding: 5,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 6,
  },
  buyTab: {
    backgroundColor: '#4CAF50',
  },
  sellTab: {
    backgroundColor: '#f44336',
  },
  tabText: {
    fontSize: 14,
    color: '#666',
  },
  buyTabText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  sellTabText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  filtersContainer: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 15,
    borderRadius: 8,
  },
  assetFilter: {
    marginBottom: 15,
  },
  assetButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f5f5f5',
    marginRight: 10,
  },
  assetButtonActive: {
    backgroundColor: '#4CAF50',
  },
  assetText: {
    fontSize: 14,
    color: '#666',
  },
  assetTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  paymentFilter: {
    marginBottom: 15,
  },
  paymentButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
    backgroundColor: '#f5f5f5',
    marginRight: 8,
  },
  paymentButtonActive: {
    backgroundColor: '#2196F3',
  },
  paymentButtonText: {
    fontSize: 12,
    color: '#666',
  },
  paymentButtonTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  amountContainer: {
    marginBottom: 10,
  },
  amountLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  amountInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 16,
    color: '#333',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#fff',
    marginHorizontal: 15,
    marginBottom: 15,
    paddingVertical: 15,
    borderRadius: 8,
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  offersList: {
    paddingHorizontal: 15,
  },
  offerCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
  },
  offerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  merchantInfo: {
    flex: 1,
  },
  merchantName: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  merchantText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginRight: 5,
  },
  merchantStats: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ratingText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 3,
    marginRight: 5,
  },
  tradesText: {
    fontSize: 12,
    color: '#999',
  },
  priceInfo: {
    alignItems: 'flex-end',
  },
  priceText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  priceLabel: {
    fontSize: 12,
    color: '#666',
  },
  offerDetails: {
    marginBottom: 15,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 13,
    color: '#666',
  },
  detailValue: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#333',
  },
  paymentMethods: {
    flexDirection: 'row',
    gap: 5,
  },
  paymentBadge: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  paymentText: {
    fontSize: 10,
    color: '#2196F3',
    fontWeight: 'bold',
  },
  tradeButton: {
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  buyButton: {
    backgroundColor: '#4CAF50',
  },
  sellButton: {
    backgroundColor: '#f44336',
  },
  tradeButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  createOrderButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2196F3',
    marginHorizontal: 15,
    marginVertical: 10,
    paddingVertical: 15,
    borderRadius: 8,
    gap: 8,
  },
  createOrderText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  bottomInfo: {
    padding: 15,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  infoButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  infoText: {
    fontSize: 14,
    color: '#4CAF50',
    marginLeft: 8,
    fontWeight: 'bold',
  },
});