/**
 * TigerEx Margin Trading Page  
 * @file margin.tsx
 * @description Professional margin/isolated trading interface
 * @author TigerEx Development Team
 */
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  Zap,
  BarChart3,
  Settings,
  Star,
  Wallet,
  Search,
  Lock,
  Unlock,
  AlertTriangle,
  ArrowUpDown,
} from 'lucide-react';

// TigerEx Brand Colors
const TIGEREX_COLORS = {
  primary: '#F0B90B',
  background: '#0B0E14',
  card: '#1C2128',
  cardHover: '#252D38',
  text: '#EAECE4',
  textSecondary: '#8B929E',
  green: '#00C087',
  red: '#F6465D',
  border: '#2A303C',
  gold: '#F0B90B',
};

// Margin pair interface
interface MarginPair {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  lastPrice: number;
  priceChangePercent: number;
  marginBorrowable: boolean;
  maxBorrowLimit: number;
  currentBorrowed: number;
  interestRate: number;
  liquidationPrice: number;
  marginRatio: number;
}

interface MarginOrder {
  id: string;
  side: 'BUY' | 'SELL';
  type: 'MARKET' | 'LIMIT';
  price: number;
  quantity: number;
  status: string;
  time: Date;
}

// Generate mock margin pairs
const generateMockPairs = (): MarginPair[] => [
  { symbol: 'BTC/USDT', baseAsset: 'BTC', quoteAsset: 'USDT', lastPrice: 67842.50, priceChangePercent: 1.88, marginBorrowable: true, maxBorrowLimit: 50000, currentBorrowed: 2340.50, interestRate: 0.0003, liquidationPrice: 33250.00, marginRatio: 2.85 },
  { symbol: 'ETH/USDT', baseAsset: 'ETH', quoteAsset: 'USDT', lastPrice: 3456.25, priceChangePercent: -1.31, marginBorrowable: true, maxBorrowLimit: 25000, currentBorrowed: 1250.00, interestRate: 0.0004, liquidationPrice: 1650.00, marginRatio: 2.45 },
  { symbol: 'BNB/USDT', baseAsset: 'BNB', quoteAsset: 'USDT', lastPrice: 598.40, priceChangePercent: 2.14, marginBorrowable: true, maxBorrowLimit: 5000, currentBorrowed: 450.00, interestRate: 0.0005, liquidationPrice: 285.00, marginRatio: 2.15 },
  { symbol: 'SOL/USDT', baseAsset: 'SOL', quoteAsset: 'USDT', lastPrice: 185.60, priceChangePercent: -1.69, marginBorrowable: true, maxBorrowLimit: 3000, currentBorrowed: 180.00, interestRate: 0.0005, liquidationPrice: 88.50, marginRatio: 1.95 },
  { symbol: 'XRP/USDT', baseAsset: 'XRP', quoteAsset: 'USDT', priceChangePercent: 2.44, lastPrice: 0.5245, marginBorrowable: true, maxBorrowLimit: 2000, currentBorrowed: 85.00, interestRate: 0.0006, liquidationPrice: 0.25, marginRatio: 2.25 },
  { symbol: 'ADA/USDT', baseAsset: 'ADA', quoteAsset: 'USDT', priceChangePercent: -1.84, lastPrice: 0.4525, marginBorrowable: true, maxBorrowLimit: 1500, currentBorrowed: 62.00, interestRate: 0.0006, liquidationPrice: 0.215, marginRatio: 2.05 },
  { symbol: 'LINK/USDT', baseAsset: 'LINK', quoteAsset: 'USDT', priceChangePercent: 2.41, lastPrice: 14.85, marginBorrowable: true, maxBorrowLimit: 2000, currentBorrowed: 95.00, interestRate: 0.0005, liquidationPrice: 7.05, marginRatio: 2.35 },
  { symbol: 'DOGE/USDT', baseAsset: 'DOGE', quoteAsset: 'USDT', priceChangePercent: 3.04, lastPrice: 0.1525, marginBorrowable: true, maxBorrowLimit: 1000, currentBorrowed: 45.00, interestRate: 0.0007, liquidationPrice: 0.072, marginRatio: 1.85 },
];

const formatPrice = (num: number, precision: number = 2): string => {
  return num.toLocaleString('en-US', { minimumFractionDigits: precision, maximumFractionDigits: precision });
};

const formatNumber = (num: number): string => {
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  return num.toFixed(2);
};

const MarginTradingPage: React.FC = () => {
  const [selectedPair, setSelectedPair] = useState<MarginPair | null>(null);
  const [pairs, setPairs] = useState<MarginPair[]>([]);
  const [orders, setOrders] = useState<MarginOrder[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  const [orderSide, setOrderSide] = useState<'BUY' | 'SELL'>('BUY');
  const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT'>('LIMIT');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  
  const [activeTab, setActiveTab] = useState('order');
  const [placingOrder, setPlacingOrder] = useState(false);
  const [borrowAmount, setBorrowAmount] = useState('');
  const [showBorrowModal, setShowBorrowModal] = useState(false);
  
  useEffect(() => {
    const marginPairs = generateMockPairs();
    setPairs(marginPairs);
    setSelectedPair(marginPairs[0]);
  }, []);

  useEffect(() => {
    if (selectedPair) {
      setPrice(selectedPair.lastPrice.toString());
    }
  }, [selectedPair]);

  const placeOrder = async () => {
    if (!selectedPair || !quantity) return;
    setPlacingOrder(true);
    
    const newOrder: MarginOrder = {
      id: `order-${Date.now()}`,
      side: orderSide,
      type: orderType,
      price: parseFloat(price),
      quantity: parseFloat(quantity),
      status: orderType === 'MARKET' ? 'FILLED' : 'PENDING',
      time: new Date(),
    };
    
    setOrders([newOrder, ...orders]);
    setQuantity('');
    setPlacingOrder(false);
  };

  const borrow = () => {
    if (!selectedPair || !borrowAmount) return;
    alert(`Borrowed ${borrowAmount} ${selectedPair.quoteAsset}`);
    setBorrowAmount('');
    setShowBorrowModal(false);
  };

  const calculateLiquidationPrice = (): string => {
    if (!selectedPair) return '0';
    if (orderSide === 'SELL') {
      return formatPrice(selectedPair.liquidationPrice);
    }
    return formatPrice(selectedPair.lastPrice * 0.85);
  };

  return (
    <div className="flex h-screen bg-[#0B0E14] text-[#EAECE4]" style={{ backgroundColor: TIGEREX_COLORS.background }}>
      {/* Left - Margin Pairs */}
      <div className="w-72 border-r border-[#2A3000]" style={{ borderColor: TIGEREX_COLORS.border }}>
        <div className="p-3 border-b border-[#2A3000]" style={{ borderColor: TIGEREX_COLORS.border }}>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search pairs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-[#1C2128] border border-[#2A3000] rounded-lg text-sm text-white"
            />
          </div>
        </div>
        <ScrollArea className="h-[calc(100vh-64px)]">
          {pairs.map((pair) => (
            <div
              key={pair.symbol}
              onClick={() => setSelectedPair(pair)}
              className={`p-3 cursor-pointer border-b border-[#2A3000] hover:bg-[#252D38] ${
                selectedPair?.symbol === pair.symbol ? 'bg-[#252D38]' : ''
              }`}
            >
              <div className="flex justify-between mb-1">
                <span className="font-semibold text-white">{pair.symbol}</span>
                <Badge variant={pair.marginBorrowable ? 'default' : 'destructive'} className="text-xs">
                  {pair.marginBorrowable ? 'Isolated' : 'Suspended'}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-white">${formatPrice(pair.lastPrice)}</span>
                <span className={pair.priceChangePercent >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {pair.priceChangePercent >= 0 ? '+' : ''}{pair.priceChangePercent.toFixed(2)}%
                </span>
              </div>
            </div>
          ))}
        </ScrollArea>
      </div>

      {/* Center - Info */}
      <div className="flex-1 flex flex-col">
        <div className="p-3 border-b border-[#2A3000]" style={{ borderColor: TIGEREX_COLORS.border }}>
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-bold text-white">{selectedPair?.symbol}</h2>
            <span className="text-2xl font-bold text-white">${formatPrice(selectedPair?.lastPrice || 0)}</span>
            <span className={`text-sm ${(selectedPair?.priceChangePercent || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {(selectedPair?.priceChangePercent || 0) >= 0 ? '+' : ''}{selectedPair?.priceChangePercent?.toFixed(2)}%
            </span>
          </div>
        </div>
        
        <div className="flex-1 p-4 flex items-center justify-center">
          <div className="text-center">
            <Activity className="w-24 h-24 mx-auto mb-4 text-gray-600" />
            <p className="text-gray-500">Margin Trading Chart</p>
          </div>
        </div>

        {/* Margin Info */}
        <div className="border-t border-[#2A3000] p-4" style={{ borderColor: TIGEREX_COLORS.border }}>
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-xs text-gray-500">Borrowable</div>
              <div className="text-lg font-bold text-[#F0B90B]">${formatNumber(selectedPair?.maxBorrowLimit || 0)}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500">Borrowed</div>
              <div className="text-lg font-bold text-white">${formatNumber(selectedPair?.currentBorrowed || 0)}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500">Interest Rate</div>
              <div className="text-lg font-bold text-white">{((selectedPair?.interestRate || 0) * 100).toFixed(4)}%</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500">Margin Ratio</div>
              <div className={`text-lg font-bold ${(selectedPair?.marginRatio || 0) < 1.5 ? 'text-red-400' : 'text-green-400'}`}>
                {selectedPair?.marginRatio?.toFixed(2)}
              </div>
            </div>
          </div>
          
          <button
            onClick={() => setShowBorrowModal(true)}
            className="w-full mt-4 py-3 bg-[#F0B90B] text-black rounded-lg font-semibold hover:bg-[#E5A809]"
          >
            <Lock className="w-4 h-4 inline mr-2" />
            Borrow More
          </button>
        </div>
      </div>

      {/* Right - Trading */}
      <div className="w-80 border-l border-[#2A3000]" style={{ borderColor: TIGEREX_COLORS.border }}>
        <div className="border-b border-[#2A3000]" style={{ borderColor: TIGEREX_COLORS.border }}>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="w-full bg-transparent">
              <TabsTrigger value="order" className="flex-1">Order</TabsTrigger>
              <TabsTrigger value="history" className="flex-1">History</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {activeTab === 'order' && (
          <div className="p-4 space-y-4">
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setOrderSide('BUY')}
                className={`py-3 rounded-lg font-semibold ${orderSide === 'BUY' ? 'bg-green-500 text-black' : 'bg-[#1C2128] text-gray-400'}`}
              >
                Buy/Long
              </button>
              <button
                onClick={() => setOrderSide('SELL')}
                className={`py-3 rounded-lg font-semibold ${orderSide === 'SELL' ? 'bg-red-500 text-white' : 'bg-[#1C2128] text-gray-400'}`}
              >
                Sell/Short
              </button>
            </div>

            <div className="grid grid-cols-2 gap-1">
              {['MARKET', 'LIMIT'].map((type) => (
                <button
                  key={type}
                  onClick={() => setOrderType(type as any)}
                  className={`py-2 rounded text-sm ${orderType === type ? 'bg-[#F0B90B] text-black' : 'bg-[#1C2128] text-gray-400'}`}
                >
                  {type}
                </button>
              ))}
            </div>

            {orderType === 'LIMIT' && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">Price</label>
                <input
                  type="number"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  className="w-full px-3 py-3 bg-[#1C2128] border border-[#2A3000] rounded-lg text-white"
                />
              </div>
            )}

            <div>
              <label className="block text-sm text-gray-400 mb-2">Amount</label>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="0.0000"
                className="w-full px-3 py-3 bg-[#1C2128] border border-[#2A3000] rounded-lg text-white"
              />
            </div>

            <div className="p-3 bg-[#1C2128] rounded-lg">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Est. Liquidation</span>
                <span className="text-red-400">${calculateLiquidationPrice()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Value</span>
                <span className="text-white">${(parseFloat(quantity || '0') * parseFloat(price || '0')).toFixed(2)}</span>
              </div>
            </div>

            <button
              onClick={placeOrder}
              disabled={placingOrder || !quantity}
              className={`w-full py-4 rounded-lg font-bold text-lg ${
                orderSide === 'BUY' ? 'bg-green-500 hover:bg-green-600 text-black' : 'bg-red-500 hover:bg-red-600 text-white'
              }`}
            >
              {placingOrder ? 'Processing...' : `${orderSide === 'BUY' ? 'Buy' : 'Sell'} ${selectedPair?.baseAsset}`}
            </button>
          </div>
        )}

        {activeTab === 'history' && (
          <ScrollArea className="flex-1 p-4">
            {orders.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No orders</p>
              </div>
            ) : (
              orders.map((order) => (
                <div key={order.id} className="p-3 bg-[#1C2128] rounded-lg mb-2">
                  <div className="flex justify-between">
                    <span className="font-semibold">{order.side}</span>
                    <Badge variant={order.status === 'FILLED' ? 'default' : 'destructive'}>
                      {order.status}
                    </Badge>
                  </div>
                  <div className="text-sm text-gray-400">
                    {order.type} @ ${order.price} x {order.quantity}
                  </div>
                </div>
              ))
            )}
          </ScrollArea>
        )}
      </div>
    </div>
  );
};

export default MarginTradingPage;
