import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { 
  ChartBarIcon, 
  ArrowUpIcon, 
  ArrowDownIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ScaleIcon
} from '@heroicons/react/24/outline';

// Components
import TradingChart from '../../components/trading/TradingChart';
import OrderBook from '../../components/trading/OrderBook';
import TradeHistory from '../../components/trading/TradeHistory';
import OrderForm from '../../components/trading/OrderForm';
import OpenOrders from '../../components/trading/OpenOrders';
import MarketSelector from '../../components/trading/MarketSelector';
import PriceDisplay from '../../components/trading/PriceDisplay';

// Hooks
import { useWebSocket } from '../../hooks/useWebSocket';
import { useAuth } from '../../hooks/useAuth';
import { useTradingPair } from '../../hooks/useTradingPair';

// Services
import { tradingService } from '../../services/tradingService';
import { marketDataService } from '../../services/marketDataService';

// Types
import { TradingPair, OrderBook as OrderBookType, Trade, Order } from '../../types/trading';

const SpotTrading: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  // State
  const [selectedPair, setSelectedPair] = useState<string>('BTCUSDT');
  const [chartTimeframe, setChartTimeframe] = useState<string>('1h');
  const [activeOrderTab, setActiveOrderTab] = useState<'open' | 'history' | 'trades'>('open');

  // Custom hooks
  const { 
    currentPrice, 
    priceChange, 
    priceChangePercent, 
    volume24h, 
    high24h, 
    low24h 
  } = useTradingPair(selectedPair);

  // WebSocket connection for real-time data
  const { socket, isConnected } = useWebSocket('/trading');

  // Queries
  const { data: orderBook, isLoading: orderBookLoading } = useQuery({
    queryKey: ['orderBook', selectedPair],
    queryFn: () => marketDataService.getOrderBook(selectedPair),
    refetchInterval: 1000,
  });

  const { data: recentTrades, isLoading: tradesLoading } = useQuery({
    queryKey: ['recentTrades', selectedPair],
    queryFn: () => marketDataService.getRecentTrades(selectedPair),
    refetchInterval: 2000,
  });

  const { data: userOrders, isLoading: ordersLoading } = useQuery({
    queryKey: ['userOrders', user?.id],
    queryFn: () => tradingService.getUserOrders(),
    enabled: !!user,
    refetchInterval: 5000,
  });

  const { data: userTrades, isLoading: userTradesLoading } = useQuery({
    queryKey: ['userTrades', user?.id],
    queryFn: () => tradingService.getUserTrades(),
    enabled: !!user,
    refetchInterval: 10000,
  });

  const { data: balances } = useQuery({
    queryKey: ['balances', user?.id],
    queryFn: () => tradingService.getBalances(),
    enabled: !!user,
    refetchInterval: 5000,
  });

  // Mutations
  const placeOrderMutation = useMutation({
    mutationFn: tradingService.placeOrder,
    onSuccess: () => {
      toast.success('Order placed successfully');
      queryClient.invalidateQueries({ queryKey: ['userOrders'] });
      queryClient.invalidateQueries({ queryKey: ['balances'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to place order');
    },
  });

  const cancelOrderMutation = useMutation({
    mutationFn: tradingService.cancelOrder,
    onSuccess: () => {
      toast.success('Order cancelled successfully');
      queryClient.invalidateQueries({ queryKey: ['userOrders'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to cancel order');
    },
  });

  // WebSocket event handlers
  useEffect(() => {
    if (!socket || !isConnected) return;

    // Subscribe to market data updates
    socket.emit('subscribe', {
      channel: 'orderbook',
      symbol: selectedPair,
    });

    socket.emit('subscribe', {
      channel: 'trades',
      symbol: selectedPair,
    });

    socket.emit('subscribe', {
      channel: 'ticker',
      symbol: selectedPair,
    });

    // Handle real-time updates
    socket.on('orderbook_update', (data) => {
      queryClient.setQueryData(['orderBook', selectedPair], data);
    });

    socket.on('trade_update', (data) => {
      queryClient.setQueryData(['recentTrades', selectedPair], (old: Trade[] = []) => {
        return [data, ...old.slice(0, 49)]; // Keep last 50 trades
      });
    });

    socket.on('ticker_update', (data) => {
      // Update price display
      queryClient.setQueryData(['ticker', selectedPair], data);
    });

    // User-specific updates
    if (user) {
      socket.emit('subscribe', {
        channel: 'user_orders',
        userId: user.id,
      });

      socket.on('order_update', () => {
        queryClient.invalidateQueries({ queryKey: ['userOrders'] });
      });

      socket.on('balance_update', () => {
        queryClient.invalidateQueries({ queryKey: ['balances'] });
      });
    }

    return () => {
      socket.emit('unsubscribe', {
        channel: 'orderbook',
        symbol: selectedPair,
      });
      socket.emit('unsubscribe', {
        channel: 'trades',
        symbol: selectedPair,
      });
      socket.emit('unsubscribe', {
        channel: 'ticker',
        symbol: selectedPair,
      });
      if (user) {
        socket.emit('unsubscribe', {
          channel: 'user_orders',
          userId: user.id,
        });
      }
    };
  }, [socket, isConnected, selectedPair, user, queryClient]);

  // Handle order placement
  const handlePlaceOrder = useCallback((orderData: any) => {
    placeOrderMutation.mutate({
      ...orderData,
      symbol: selectedPair,
    });
  }, [placeOrderMutation, selectedPair]);

  // Handle order cancellation
  const handleCancelOrder = useCallback((orderId: string) => {
    cancelOrderMutation.mutate(orderId);
  }, [cancelOrderMutation]);

  // Memoized components for performance
  const memoizedChart = useMemo(() => (
    <TradingChart
      symbol={selectedPair}
      timeframe={chartTimeframe}
      onTimeframeChange={setChartTimeframe}
    />
  ), [selectedPair, chartTimeframe]);

  const memoizedOrderBook = useMemo(() => (
    <OrderBook
      data={orderBook}
      loading={orderBookLoading}
      onPriceClick={(price) => {
        // Auto-fill price in order form
        const event = new CustomEvent('autofillPrice', { detail: { price } });
        window.dispatchEvent(event);
      }}
    />
  ), [orderBook, orderBookLoading]);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header with Market Info */}
      <div className="border-b border-gray-800 bg-gray-900/95 backdrop-blur-sm sticky top-0 z-40">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <MarketSelector
                selectedPair={selectedPair}
                onPairChange={setSelectedPair}
              />
              
              <PriceDisplay
                price={currentPrice}
                change={priceChange}
                changePercent={priceChangePercent}
                className="text-2xl font-bold"
              />
              
              <div className="flex items-center space-x-4 text-sm text-gray-400">
                <div className="flex items-center space-x-1">
                  <ChartBarIcon className="w-4 h-4" />
                  <span>24h Vol: {volume24h?.toLocaleString()} {selectedPair.replace('USDT', '')}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <ArrowUpIcon className="w-4 h-4 text-green-500" />
                  <span>24h High: ${high24h?.toLocaleString()}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <ArrowDownIcon className="w-4 h-4 text-red-500" />
                  <span>24h Low: ${low24h?.toLocaleString()}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs ${
                isConnected ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-400' : 'bg-red-400'
                }`} />
                <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Trading Interface */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* Left Panel - Chart */}
        <div className="flex-1 flex flex-col border-r border-gray-800">
          <div className="flex-1 p-4">
            {memoizedChart}
          </div>
        </div>

        {/* Right Panel - Order Book & Trading */}
        <div className="w-80 flex flex-col border-r border-gray-800">
          {/* Order Book */}
          <div className="flex-1 border-b border-gray-800">
            {memoizedOrderBook}
          </div>

          {/* Recent Trades */}
          <div className="h-64">
            <TradeHistory
              data={recentTrades}
              loading={tradesLoading}
            />
          </div>
        </div>

        {/* Trading Panel */}
        <div className="w-80 flex flex-col">
          {/* Order Form */}
          <div className="border-b border-gray-800">
            <OrderForm
              symbol={selectedPair}
              balances={balances}
              onPlaceOrder={handlePlaceOrder}
              loading={placeOrderMutation.isPending}
            />
          </div>

          {/* User Orders & Trades */}
          <div className="flex-1 flex flex-col">
            <div className="border-b border-gray-800">
              <div className="flex">
                {[
                  { key: 'open', label: 'Open Orders', count: userOrders?.filter(o => o.status === 'open').length },
                  { key: 'history', label: 'Order History', count: userOrders?.length },
                  { key: 'trades', label: 'Trade History', count: userTrades?.length },
                ].map(({ key, label, count }) => (
                  <button
                    key={key}
                    onClick={() => setActiveOrderTab(key as any)}
                    className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                      activeOrderTab === key
                        ? 'border-orange-500 text-orange-500'
                        : 'border-transparent text-gray-400 hover:text-gray-300'
                    }`}
                  >
                    {label}
                    {count !== undefined && (
                      <span className="ml-2 px-2 py-0.5 bg-gray-700 rounded-full text-xs">
                        {count}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex-1 overflow-hidden">
              {activeOrderTab === 'open' && (
                <OpenOrders
                  orders={userOrders?.filter(o => o.status === 'open') || []}
                  loading={ordersLoading}
                  onCancelOrder={handleCancelOrder}
                  cancelLoading={cancelOrderMutation.isPending}
                />
              )}
              
              {activeOrderTab === 'history' && (
                <OpenOrders
                  orders={userOrders || []}
                  loading={ordersLoading}
                  showAll
                />
              )}
              
              {activeOrderTab === 'trades' && (
                <TradeHistory
                  data={userTrades}
                  loading={userTradesLoading}
                  showUserTrades
                />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Status Bar */}
      <div className="border-t border-gray-800 bg-gray-900/95 backdrop-blur-sm">
        <div className="px-4 py-2 flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center space-x-4">
            <span>TigerEx Spot Trading</span>
            <span>•</span>
            <span>Fee: 0.1%</span>
            <span>•</span>
            <span>24h Volume: ${volume24h?.toLocaleString()}</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <span>Server Time: {new Date().toLocaleTimeString()}</span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span>Live</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpotTrading;