/**
 * TigerEx Mobile App
 * @file TradFiMobile.tsx
 * @description React Native mobile component
 * @author TigerEx Development Team
 */
/TigerEx TradFi Mobile Interface
/CFD, Forex, ETF, Derivatives Trading for Mobile
*/

import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, TextInput, Alert } from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';
import { 
  TrendingUp, TrendingDown, Activity, Globe, Settings, 
  ArrowUp, ArrowDown, Wallet, Clock, Shield
} from 'lucide-react-native';

const { width } = Dimensions.get('window');

// TradFi Types
const INSTRUMENT_TYPES = {
  CFD: 'CFD',
  FOREX: 'Forex',
  ETF: 'ETF',
  STOCK_TOKEN: 'Stock',
  DERIVATIVE: 'Deriv',
  OPTION: 'Option',
  FUTURE: 'Future',
};

const TRADFI_INSTRUMENTS = [
  { symbol: 'BTC/USD', name: 'Bitcoin', type: 'CFD', price: 42500.00, change: 2.34, leverage: 100 },
  { symbol: 'ETH/USD', name: 'Ethereum', type: 'CFD', price: 2280.00, change: 1.56, leverage: 50 },
  { symbol: 'EUR/USD', name: 'Euro/Dollar', type: 'FOREX', price: 1.0845, change: 0.12, leverage: 30 },
  { symbol: 'GBP/USD', name: 'British Pound', type: 'FOREX', price: 1.2650, change: -0.08, leverage: 30 },
  { symbol: 'AAPL', name: 'Apple Inc', type: 'STOCK_TOKEN', price: 178.50, change: 1.23, leverage: 20 },
  { symbol: 'TSLA', name: 'Tesla Inc', type: 'STOCK_TOKEN', price: 245.20, change: -2.45, leverage: 20 },
  { symbol: 'SPY', name: 'S&P 500 ETF', type: 'ETF', price: 478.50, change: 0.45, leverage: 10 },
  { symbol: 'QQQ', name: 'Nasdaq ETF', type: 'ETF', price: 405.20, change: 0.78, leverage: 10 },
  { symbol: 'GLD', name: 'Gold ETF', type: 'ETF', price: 185.30, change: 0.34, leverage: 10 },
  { symbol: 'GOOGL', name: 'Alphabet', type: 'STOCK_TOKEN', price: 142.80, change: 0.89, leverage: 20 },
  { symbol: 'NVDA', name: 'NVIDIA', type: 'STOCK_TOKEN', price: 545.80, change: 3.45, leverage: 20 },
  { symbol: 'XAU/USD', name: 'Gold', type: 'DERIVATIVE', price: 2025.50, change: 0.56, leverage: 100 },
];

export default function TradFiMobile() {
  const [selectedInstrument, setSelectedInstrument] = useState(TRADFI_INSTRUMENTS[0]);
  const [orderSide, setOrderSide] = useState('buy');
  const [quantity, setQuantity] = useState('1');
  const [leverage, setLeverage] = useState(1);
  const [activeTab, setActiveTab] = useState('trade');

  const qty = parseFloat(quantity) || 0;
  const orderValue = selectedInstrument.price * qty * leverage;
  const margin = orderValue / leverage;
  const fee = orderValue * 0.001;

  const handleOpenPosition = () => {
    Alert.alert(
      'Position Opened',
      `${orderSide.toUpperCase()} ${qty} ${selectedInstrument.symbol} at ${selectedInstrument.price}`,
      [{ text: 'OK' }]
    );
  };

  return (
    <View style={{ flex: 1, backgroundColor: '#111827', padding: 16 }}>
      {/* Header */}
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
          <Globe size={32} color="#f59e0b" />
          <View>
            <Text style={{ color: 'white', fontSize: 20, fontWeight: 'bold' }}>TigerEx TradFi</Text>
            <Text style={{ color: '#9ca3af', fontSize: 12 }}>CFD, Forex, ETF</Text>
          </View>
        </View>
      </View>

      {/* Tabs */}
      <View style={{ flexDirection: 'row', borderBottomWidth: 1, borderBottomColor: '#374151', marginBottom: 16 }}>
        {['trade', 'positions'].map(tab => (
          <TouchableOpacity
            key={tab}
            onPress={() => setActiveTab(tab)}
            style={{ 
              paddingVertical: 12, 
              paddingHorizontal: 16,
              borderBottomWidth: activeTab === tab ? 2 : 0,
              borderBottomColor: activeTab === tab ? '#f59e0b' : 'transparent'
            }}
          >
            <Text style={{ color: activeTab === tab ? '#f59e0b' : '#9ca3af', textTransform: 'capitalize' }}>
              {tab}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Instrument Header */}
      <View style={{ backgroundColor: '#1f2937', borderRadius: 12, padding: 16, marginBottom: 16 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <View>
            <Text style={{ color: '#9ca3af', fontSize: 12 }}>{selectedInstrument.type}</Text>
            <Text style={{ color: 'white', fontSize: 24, fontWeight: 'bold' }}>{selectedInstrument.symbol}</Text>
            <Text style={{ color: '#9ca3af', fontSize: 14 }}>{selectedInstrument.name}</Text>
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={{ color: 'white', fontSize: 24, fontWeight: 'bold' }}>
              ${selectedInstrument.price.toLocaleString()}
            </Text>
            <Text style={{ 
              color: selectedInstrument.change >= 0 ? '#10b981' : '#ef4444',
              fontSize: 14 
            }}>
              {selectedInstrument.change >= 0 ? '+' : ''}{selectedInstrument.change}%
            </Text>
          </View>
        </View>
      </View>

      {/* Buy/Sell */}
      <View style={{ flexDirection: 'row', gap: 8, marginBottom: 16 }}>
        <TouchableOpacity
          onPress={() => setOrderSide('buy')}
          style={{ 
            flex: 1, 
            backgroundColor: orderSide === 'buy' ? '#10b981' : '#374151',
            paddingVertical: 14,
            borderRadius: 8,
            alignItems: 'center'
          }}
        >
          <Text style={{ color: 'white', fontWeight: 'bold', fontSize: 16 }}>BUY</Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setOrderSide('sell')}
          style={{ 
            flex: 1, 
            backgroundColor: orderSide === 'sell' ? '#ef4444' : '#374151',
            paddingVertical: 14,
            borderRadius: 8,
            alignItems: 'center'
          }}
        >
          <Text style={{ color: 'white', fontWeight: 'bold', fontSize: 16 }}>SELL</Text>
        </TouchableOpacity>
      </View>

      {/* Order Form */}
      <View style={{ backgroundColor: '#1f2937', borderRadius: 12, padding: 16, marginBottom: 16 }}>
        <Text style={{ color: '#9ca3af', fontSize: 12, marginBottom: 8 }}>Quantity</Text>
        <TextInput
          value={quantity}
          onChangeText={setQuantity}
          keyboardType="numeric"
          style={{ 
            backgroundColor: '#374151', 
            borderRadius: 8, 
            padding: 12, 
            color: 'white',
            fontSize: 18
          }}
        />

        <Text style={{ color: '#9ca3af', fontSize: 12, marginTop: 16, marginBottom: 8 }}>Leverage</Text>
        <View style={{ flexDirection: 'row', gap: 8 }}>
          {[1, 2, 5, 10, 20, 50].map(l => (
            <TouchableOpacity
              key={l}
              onPress={() => setLeverage(l)}
              style={{ 
                paddingVertical: 8, 
                paddingHorizontal: 16,
                backgroundColor: leverage === l ? '#f59e0b' : '#374151',
                borderRadius: 8
              }}
            >
              <Text style={{ color: leverage === l ? 'black' : 'white' }}>{l}x</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Summary */}
        <View style={{ marginTop: 16, paddingTop: 16, borderTopWidth: 1, borderTopColor: '#374151' }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 }}>
            <Text style={{ color: '#9ca3af' }}>Order Value</Text>
            <Text style={{ color: 'white' }}>${orderValue.toLocaleString()}</Text>
          </View>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 }}>
            <Text style={{ color: '#9ca3af' }}>Margin</Text>
            <Text style={{ color: 'white' }}>${margin.toFixed(2)}</Text>
          </View>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
            <Text style={{ color: '#9ca3af' }}>Fee</Text>
            <Text style={{ color: 'white' }}>${fee.toFixed(2)}</Text>
          </View>
        </View>
      </View>

      {/* Submit */}
      <TouchableOpacity
        onPress={handleOpenPosition}
        style={{ 
          backgroundColor: orderSide === 'buy' ? '#10b981' : '#ef4444',
          paddingVertical: 16,
          borderRadius: 12,
          alignItems: 'center'
        }}
      >
        <Text style={{ color: 'white', fontWeight: 'bold', fontSize: 18 }}>
          {orderSide.toUpperCase()} {selectedInstrument.symbol}
        </Text>
      </TouchableOpacity>

      {/* Warning */}
      <View style={{ 
        flexDirection: 'row', 
        alignItems: 'center', 
        gap: 8, 
        marginTop: 16,
        padding: 12,
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        borderRadius: 8
      }}>
        <Shield size={20} color="#f59e0b" />
        <Text style={{ color: '#9ca3af', fontSize: 12 }}>
          Leverage increases profit and loss. Trade responsibly.
        </Text>
      </View>

      {/* Instruments List */}
      <Text style={{ color: 'white', fontSize: 16, fontWeight: 'bold', marginTop: 24, marginBottom: 12 }}>
        Instruments
      </Text>
      <ScrollView showsVerticalScrollIndicator={false}>
        {TRADFI_INSTRUMENTS.map(inst => (
          <TouchableOpacity
            key={inst.symbol}
            onPress={() => setSelectedInstrument(inst)}
            style={{ 
              backgroundColor: selectedInstrument.symbol === inst.symbol ? '#374151' : '#1f2937',
              padding: 12,
              borderRadius: 8,
              marginBottom: 8,
              flexDirection: 'row',
              justifyContent: 'space-between'
            }}
          >
            <View>
              <Text style={{ color: 'white', fontWeight: 'bold' }}>{inst.symbol}</Text>
              <Text style={{ color: '#9ca3af', fontSize: 12 }}>{inst.name}</Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={{ color: 'white' }}>${inst.price.toLocaleString()}</Text>
              <Text style={{ 
                color: inst.change >= 0 ? '#10b981' : '#ef4444',
                fontSize: 12
              }}>
                {inst.change >= 0 ? '+' : ''}{inst.change}%
              </Text>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
}