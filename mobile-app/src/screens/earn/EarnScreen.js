/**
 * TigerEx Mobile - Earn Screen
 * Complete earning opportunities and yield farming
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  FlatList,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

export default function EarnScreen({navigation}) {
  const [selectedCategory, setSelectedCategory] = useState('all');

  const earnProducts = [
    {
      id: '1',
      type: 'staking',
      asset: 'BTC',
      apy: '5.2%',
      duration: '30 days',
      minAmount: '0.001',
      totalStaked: '1,234 BTC',
      risk: 'Low',
      category: 'staking',
    },
    {
      id: '2',
      type: 'savings',
      asset: 'USDT',
      apy: '8.5%',
      duration: 'Flexible',
      minAmount: '10',
      totalStaked: '5.2M USDT',
      risk: 'Very Low',
      category: 'savings',
    },
    {
      id: '3',
      type: 'liquidity',
      asset: 'ETH/USDT',
      apy: '12.3%',
      duration: 'Flexible',
      minAmount: '100',
      totalStaked: '$2.1M',
      risk: 'Medium',
      category: 'defi',
    },
    {
      id: '4',
      type: 'dual',
      asset: 'BNB',
      apy: '15.8%',
      duration: '7 days',
      minAmount: '1',
      totalStaked: '45,678 BNB',
      risk: 'High',
      category: 'structured',
    },
    {
      id: '5',
      type: 'launchpool',
      asset: 'NEW',
      apy: '25.0%',
      duration: '14 days',
      minAmount: '100 USDT',
      totalStaked: '$890K',
      risk: 'High',
      category: 'launchpool',
    },
  ];

  const categories = [
    {key: 'all', label: 'All', count: earnProducts.length},
    {key: 'staking', label: 'Staking', count: 1},
    {key: 'savings', label: 'Savings', count: 1},
    {key: 'defi', label: 'DeFi', count: 1},
    {key: 'structured', label: 'Structured', count: 1},
    {key: 'launchpool', label: 'Launchpool', count: 1},
  ];

  const filteredProducts = earnProducts.filter(
    product => selectedCategory === 'all' || product.category === selectedCategory
  );

  const renderEarnProduct = ({item}) => (
    <TouchableOpacity style={styles.productCard}>
      <View style={styles.productHeader}>
        <View style={styles.productLeft}>
          <View style={styles.productTypeContainer}>
            <Text style={styles.productType}>{item.type.toUpperCase()}</Text>
            <View style={[styles.riskBadge, getRiskColor(item.risk)]}>
              <Text style={styles.riskText}>{item.risk}</Text>
            </View>
          </View>
          <Text style={styles.productAsset}>{item.asset}</Text>
        </View>
        <View style={styles.productRight}>
          <Text style={styles.productAPY}>{item.apy}</Text>
          <Text style={styles.apyLabel}>APY</Text>
        </View>
      </View>

      <View style={styles.productDetails}>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>Duration</Text>
          <Text style={styles.detailValue}>{item.duration}</Text>
        </View>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>Min Amount</Text>
          <Text style={styles.detailValue}>{item.minAmount}</Text>
        </View>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>Total Staked</Text>
          <Text style={styles.detailValue}>{item.totalStaked}</Text>
        </View>
      </View>

      <TouchableOpacity style={styles.subscribeButton}>
        <Text style={styles.subscribeButtonText}>Subscribe</Text>
      </TouchableOpacity>
    </TouchableOpacity>
  );

  const getRiskColor = risk => {
    switch (risk) {
      case 'Very Low':
        return {backgroundColor: '#e8f5e9'};
      case 'Low':
        return {backgroundColor: '#fff3e0'};
      case 'Medium':
        return {backgroundColor: '#fff8e1'};
      case 'High':
        return {backgroundColor: '#ffebee'};
      default:
        return {backgroundColor: '#f5f5f5'};
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Earn</Text>
        <TouchableOpacity>
          <Icon name="history" size={24} color="#333" />
        </TouchableOpacity>
      </View>

      {/* Total Earnings Card */}
      <View style={styles.earningsCard}>
        <View style={styles.earningsHeader}>
          <Text style={styles.earningsTitle}>Total Earnings</Text>
          <TouchableOpacity>
            <Icon name="eye-outline" size={20} color="#fff" />
          </TouchableOpacity>
        </View>
        <Text style={styles.earningsAmount}>$2,450.67</Text>
        <Text style={styles.earningsSubtext}>≈ 0.0567 BTC</Text>
        
        <View style={styles.earningsStats}>
          <View style={styles.earningStat}>
            <Text style={styles.earningStatValue}>$1,234.56</Text>
            <Text style={styles.earningStatLabel}>Yesterday</Text>
          </View>
          <View style={styles.earningStat}>
            <Text style={styles.earningStatValue}>$8,901.23</Text>
            <Text style={styles.earningStatLabel}>This Month</Text>
          </View>
          <View style={styles.earningStat}>
            <Text style={styles.earningStatValue}>12.5%</Text>
            <Text style={styles.earningStatLabel}>Avg APY</Text>
          </View>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity style={styles.quickAction}>
          <Icon name="chart-line" size={24} color="#4CAF50" />
          <Text style={styles.quickActionText}>Staking</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickAction}>
          <Icon name="piggy-bank" size={24} color="#2196F3" />
          <Text style={styles.quickActionText}>Savings</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickAction}>
          <Icon name="swap-horizontal" size={24} color="#FF9800" />
          <Text style={styles.quickActionText}>Liquidity</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickAction}>
          <Icon name="rocket-launch" size={24} color="#9C27B0" />
          <Text style={styles.quickActionText}>Launchpool</Text>
        </TouchableOpacity>
      </View>

      {/* Categories */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.categoriesContainer}>
        {categories.map(category => (
          <TouchableOpacity
            key={category.key}
            style={[
              styles.categoryChip,
              selectedCategory === category.key && styles.categoryChipActive,
            ]}
            onPress={() => setSelectedCategory(category.key)}>
            <Text
              style={[
                styles.categoryText,
                selectedCategory === category.key && styles.categoryTextActive,
              ]}>
              {category.label}
            </Text>
            <View
              style={[
                styles.categoryCount,
                selectedCategory === category.key && styles.categoryCountActive,
              ]}>
              <Text
                style={[
                  styles.categoryCountText,
                  selectedCategory === category.key && styles.categoryCountTextActive,
                ]}>
                {category.count}
              </Text>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Products List */}
      <FlatList
        data={filteredProducts}
        renderItem={renderEarnProduct}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.productsList}
        showsVerticalScrollIndicator={false}
      />

      {/* Bottom Info */}
      <View style={styles.bottomInfo}>
        <TouchableOpacity style={styles.infoButton}>
          <Icon name="information-outline" size={20} color="#2196F3" />
          <Text style={styles.infoText}>How does earning work?</Text>
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
  earningsCard: {
    backgroundColor: '#4CAF50',
    margin: 15,
    padding: 20,
    borderRadius: 12,
  },
  earningsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  earningsTitle: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.9,
  },
  earningsAmount: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  earningsSubtext: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.8,
    marginBottom: 20,
  },
  earningsStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  earningStat: {
    alignItems: 'center',
  },
  earningStatValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  earningStatLabel: {
    fontSize: 12,
    color: '#fff',
    opacity: 0.8,
    marginTop: 2,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#fff',
    marginHorizontal: 15,
    borderRadius: 8,
    paddingVertical: 15,
    marginBottom: 15,
  },
  quickAction: {
    alignItems: 'center',
  },
  quickActionText: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  categoriesContainer: {
    paddingHorizontal: 15,
    marginBottom: 15,
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  categoryChipActive: {
    backgroundColor: '#4CAF50',
    borderColor: '#4CAF50',
  },
  categoryText: {
    fontSize: 14,
    color: '#666',
    marginRight: 8,
  },
  categoryTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  categoryCount: {
    backgroundColor: '#f5f5f5',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  categoryCountActive: {
    backgroundColor: 'rgba(255,255,255,0.3)',
  },
  categoryCountText: {
    fontSize: 12,
    color: '#666',
  },
  categoryCountTextActive: {
    color: '#fff',
  },
  productsList: {
    paddingHorizontal: 15,
  },
  productCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
  },
  productHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  productLeft: {
    flex: 1,
  },
  productTypeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  productType: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginRight: 10,
  },
  riskBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  riskText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#666',
  },
  productAsset: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  productRight: {
    alignItems: 'flex-end',
  },
  productAPY: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  apyLabel: {
    fontSize: 12,
    color: '#666',
  },
  productDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  detailItem: {
    alignItems: 'center',
  },
  detailLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 3,
  },
  detailValue: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#333',
  },
  subscribeButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  subscribeButtonText: {
    color: '#fff',
    fontSize: 14,
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
    color: '#2196F3',
    marginLeft: 8,
  },
});