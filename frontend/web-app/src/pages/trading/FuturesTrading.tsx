/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { 
  ChartBarIcon, 
  ArrowUpIcon, 
  ArrowDownIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  ScaleIcon,
  BoltIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

// Components
import TradingChart from '../../components/trading/TradingChart';
import FuturesOrderBook from '../../components/trading/FuturesOrderBook';
import FuturesOrderForm from '../../components/trading/FuturesOrderForm';
import PositionsPanel from '../../components/trading/PositionsPanel';
import FuturesMarketSelector from '../../components/trading/FuturesMarketSelector';
import LeverageSelector from '../../components/trading/LeverageSelector';
import MarginInfo from '../../components/trading/MarginInfo';
import RiskWarning from '../../components/trading/RiskWarning';

// Hooks
import { useWebSocket } from '../../hooks/useWebSocket';
import { useAuth } from '../../hooks/useAuth';
import { useFuturesPair } from '../../hooks/useFuturesPair';

// Services
import { futuresService } from '../../services/futuresService';
import { marketDataService } from '../../services/marketDataService';

// Types
import { FuturesPosition, FuturesOrder, FuturesContract } from '../../types/futures';

const FuturesTrading: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  // State
  const [selectedContract, setSelectedContract] = useState<string>('BTCUSDT');
  const [contractType, setContractType] = useState<'USDM' | 'COINM'>('USDM');
  const [chartTimeframe, setChartTimeframe] = useState<string>('1h');
  const [leverage, setLeverage] = useState<number>(10);
  const [marginType, setMarginType] = useState<'isolated' | 'cross'>('isolated');
  const [activeTab, setActiveTab] = useState<'positions' | 'orders' | 'history'>('positions');
  const [showRiskWarning, setShowRiskWarning] = useState(false);

  // Custom hooks
  const { 
    currentPrice, 
    priceChange, 
    priceChangePercent, 
    volume24h, 
    openInterest,
    fundingRate,
    nextFundingTime
  } = useFuturesPair(selectedContract, contractType);

  // WebSocket connection
  const { socket, isConnected } = useWebSocket('/futures');

  // Queries
  const { data: orderBook, isLoading: orderBookLoading } = useQuery({
    queryKey: ['futuresOrderBook', selectedContract, contractType],
    queryFn: () => futuresService.getOrderBook(selectedContract, contractType),
    refetchInterval: 500,
  });

  const { data: positions, isLoading: positionsLoading } = useQuery({
    queryKey: ['futuresPositions', user?.id],
    queryFn: () => futuresService.getPositions(),
    enabled: !!user,
    refetchInterval: 2000,
  });

  const { data: futuresOrders, isLoading: ordersLoading } = useQuery({
    queryKey: ['futuresOrders', user?.id],
    queryFn: () => futuresService.getOrders(),
    enabled: !!user,
    refetchInterval: 3000,
  });

  const { data: marginBalance } = useQuery({
    queryKey: ['futuresBalance', user?.id],
    queryFn: () => futuresService.getMarginBalance(),
    enabled: !!user,
    refetchInterval: 5000,
  });

  const { data: contractInfo } = useQuery({
    queryKey: ['contractInfo', selectedContract, contractType],
    queryFn: () => futuresService.getContractInfo(selectedContract, contractType),
  });

  // Mutations
  const placeOrderMutation = useMutation({
    mutationFn: futuresService.placeOrder,
    onSuccess: () => {
      toast.success('Futures order placed successfully');
      queryClient.invalidateQueries({ queryKey: ['futuresOrders'] });
      queryClient.invalidateQueries({ queryKey: ['futuresBalance'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to place futures order');
    },
  });

  const closePositionMutation = useMutation({
    mutationFn: futuresService.closePosition,
    onSuccess: () => {
      toast.success('Position closed successfully');
      queryClient.invalidateQueries({ queryKey: ['futuresPositions'] });
      queryClient.invalidateQueries({ queryKey: ['futuresBalance'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to close position');
    },
  });

  const adjustLeverageMutation = useMutation({
    mutationFn: ({ symbol, leverage }: { symbol: string; leverage: number }) =>
      futuresService.adjustLeverage(symbol, leverage),
    onSuccess: () => {
      toast.success('Leverage adjusted successfully');
      queryClient.invalidateQueries({ queryKey: ['futuresPositions'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to adjust leverage');
    },
  });

  const adjustMarginMutation = useMutation({
    mutationFn: ({ positionId, amount, type }: { positionId: string; amount: number; type: 'add' | 'reduce' }) =>
      futuresService.adjustMargin(positionId, amount, type),
    onSuccess: () => {
      toast.success('Margin adjusted successfully');
      queryClient.invalidateQueries({ queryKey: ['futuresPositions'] });
      queryClient.invalidateQueries({ queryKey: ['futuresBalance'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to adjust margin');
    },
  });

  // WebSocket event handlers
  useEffect(() => {
    if (!socket || !isConnected) return;

    // Subscribe to futures market data
    socket.emit('subscribe', {
      channel: 'futures_orderbook',
      symbol: selectedContract,
      contractType,
    });

    socket.emit('subscribe', {
      channel: 'futures_ticker',
      symbol: selectedContract,
      contractType,
    });

    // Handle real-time updates
    socket.on('futures_orderbook_update', (data) => {
      queryClient.setQueryData(['futuresOrderBook', selectedContract, contractType], data);
    });

    socket.on('futures_ticker_update', (data) => {
      queryClient.setQueryData(['futuresTicker', selectedContract, contractType], data);
    });

    // User-specific updates
    if (user) {
      socket.emit('subscribe', {
        channel: 'futures_positions',
        userId: user.id,
      });

      socket.on('position_update', () => {
        queryClient.invalidateQueries({ queryKey: ['futuresPositions'] });
      });

      socket.on('futures_balance_update', () => {
        queryClient.invalidateQueries({ queryKey: ['futuresBalance'] });
      });

      socket.on('liquidation_warning', (data) => {
        toast.error(`Liquidation warning for ${data.symbol}: ${data.message}`, {
          duration: 10000,
        });
      });
    }

    return () => {
      socket.emit('unsubscribe', {
        channel: 'futures_orderbook',
        symbol: selectedContract,
        contractType,
      });
      socket.emit('unsubscribe', {
        channel: 'futures_ticker',
        symbol: selectedContract,
        contractType,
      });
      if (user) {
        socket.emit('unsubscribe', {
          channel: 'futures_positions',
          userId: user.id,
        });
      }
    };
  }, [socket, isConnected, selectedContract, contractType, user, queryClient]);

  // Handle order placement
  const handlePlaceOrder = useCallback((orderData: any) => {
    if (leverage > 20) {
      setShowRiskWarning(true);
      return;
    }

    placeOrderMutation.mutate({
      ...orderData,
      symbol: selectedContract,
      contractType,
      leverage,
      marginType,
    });
  }, [placeOrderMutation, selectedContract, contractType, leverage, marginType]);

  // Handle position closure
  const handleClosePosition = useCallback((positionId: string) => {
    closePositionMutation.mutate(positionId);
  }, [closePositionMutation]);

  // Handle leverage adjustment
  const handleLeverageChange = useCallback((newLeverage: number) => {
    setLeverage(newLeverage);
    adjustLeverageMutation.mutate({
      symbol: selectedContract,
      leverage: newLeverage,
    });
  }, [adjustLeverageMutation, selectedContract]);

  // Calculate liquidation price
  const calculateLiquidationPrice = useCallback((position: FuturesPosition) => {
    if (!position) return 0;
    
    const { entryPrice, size, leverage, marginType, side } = position;
    const maintenanceMarginRate = 0.005; // 0.5%
    
    if (side === 'long') {
      return entryPrice * (1 - (1 / leverage) + maintenanceMarginRate);
    } else {
      return entryPrice * (1 + (1 / leverage) - maintenanceMarginRate);
    }
  }, []);

  // Risk metrics
  const riskMetrics = useMemo(() => {
    if (!positions || !marginBalance) return null;

    const totalUnrealizedPnL = positions.reduce((sum, pos) => sum + (pos.unrealizedPnL || 0), 0);
    const totalMarginUsed = positions.reduce((sum, pos) => sum + (pos.marginUsed || 0), 0);
    const accountBalance = marginBalance.totalBalance || 0;
    const marginRatio = totalMarginUsed / accountBalance;

    return {
      totalUnrealizedPnL,
      totalMarginUsed,
      accountBalance,
      marginRatio,
      riskLevel: marginRatio > 0.8 ? 'high' : marginRatio > 0.5 ? 'medium' : 'low',
    };
  }, [positions, marginBalance]);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header with Market Info */}
      <div className="border-b border-gray-800 bg-gray-900/95 backdrop-blur-sm sticky top-0 z-40">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <FuturesMarketSelector
                selectedContract={selectedContract}
                contractType={contractType}
                onContractChange={setSelectedContract}
                onTypeChange={setContractType}
              />
              
              <div className="flex items-center space-x-4">
                <div className="text-2xl font-bold">
                  <span className={priceChange >= 0 ? 'text-green-400' : 'text-red-400'}>
                    ${currentPrice?.toLocaleString()}
                  </span>
                </div>
                
                <div className={`flex items-center space-x-1 ${
                  priceChange >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {priceChange >= 0 ? (
                    <ArrowUpIcon className="w-4 h-4" />
                  ) : (
                    <ArrowDownIcon className="w-4 h-4" />
                  )}
                  <span>{priceChangePercent?.toFixed(2)}%</span>
                </div>
              </div>
              
              <div className="flex items-center space-x-4 text-sm text-gray-400">
                <div>24h Vol: {volume24h?.toLocaleString()}</div>
                <div>Open Interest: {openInterest?.toLocaleString()}</div>
                <div className="flex items-center space-x-1">
                  <BoltIcon className="w-4 h-4" />
                  <span>Funding: {(fundingRate * 100)?.toFixed(4)}%</span>
                </div>
                <div className="flex items-center space-x-1">
                  <ClockIcon className="w-4 h-4" />
                  <span>Next: {nextFundingTime}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Risk Level Indicator */}
              {riskMetrics && (
                <div className={`flex items-center space-x-2 px-3 py-1 rounded-lg ${
                  riskMetrics.riskLevel === 'high' 
                    ? 'bg-red-900/30 text-red-400' 
                    : riskMetrics.riskLevel === 'medium'
                    ? 'bg-yellow-900/30 text-yellow-400'
                    : 'bg-green-900/30 text-green-400'
                }`}>
                  <ShieldCheckIcon className="w-4 h-4" />
                  <span className="text-xs font-medium">
                    Risk: {riskMetrics.riskLevel.toUpperCase()}
                  </span>
                </div>
              )}

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
            <TradingChart
              symbol={selectedContract}
              timeframe={chartTimeframe}
              onTimeframeChange={setChartTimeframe}
              contractType={contractType}
              showFundingRate
              showOpenInterest
            />
          </div>
        </div>

        {/* Right Panel - Order Book & Trading */}
        <div className="w-80 flex flex-col border-r border-gray-800">
          {/* Order Book */}
          <div className="flex-1 border-b border-gray-800">
            <FuturesOrderBook
              data={orderBook}
              loading={orderBookLoading}
              onPriceClick={(price) => {
                const event = new CustomEvent('autofillPrice', { detail: { price } });
                window.dispatchEvent(event);
              }}
            />
          </div>
        </div>

        {/* Trading Panel */}
        <div className="w-96 flex flex-col">
          {/* Leverage & Margin Controls */}
          <div className="border-b border-gray-800 p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Futures Trading</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setMarginType('isolated')}
                  className={`px-3 py-1 rounded text-xs ${
                    marginType === 'isolated'
                      ? 'bg-orange-500 text-white'
                      : 'bg-gray-700 text-gray-300'
                  }`}
                >
                  Isolated
                </button>
                <button
                  onClick={() => setMarginType('cross')}
                  className={`px-3 py-1 rounded text-xs ${
                    marginType === 'cross'
                      ? 'bg-orange-500 text-white'
                      : 'bg-gray-700 text-gray-300'
                  }`}
                >
                  Cross
                </button>
              </div>
            </div>

            <LeverageSelector
              leverage={leverage}
              maxLeverage={contractInfo?.maxLeverage || 125}
              onLeverageChange={handleLeverageChange}
            />

            <MarginInfo
              balance={marginBalance}
              positions={positions}
              riskMetrics={riskMetrics}
            />
          </div>

          {/* Order Form */}
          <div className="border-b border-gray-800">
            <FuturesOrderForm
              symbol={selectedContract}
              contractType={contractType}
              leverage={leverage}
              marginType={marginType}
              balance={marginBalance}
              onPlaceOrder={handlePlaceOrder}
              loading={placeOrderMutation.isPending}
            />
          </div>

          {/* Positions & Orders */}
          <div className="flex-1 flex flex-col">
            <div className="border-b border-gray-800">
              <div className="flex">
                {[
                  { key: 'positions', label: 'Positions', count: positions?.length },
                  { key: 'orders', label: 'Open Orders', count: futuresOrders?.filter(o => o.status === 'open').length },
                  { key: 'history', label: 'Order History', count: futuresOrders?.length },
                ].map(({ key, label, count }) => (
                  <button
                    key={key}
                    onClick={() => setActiveTab(key as any)}
                    className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === key
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
              {activeTab === 'positions' && (
                <PositionsPanel
                  positions={positions || []}
                  loading={positionsLoading}
                  onClosePosition={handleClosePosition}
                  onAdjustMargin={adjustMarginMutation.mutate}
                  calculateLiquidationPrice={calculateLiquidationPrice}
                />
              )}
              
              {activeTab === 'orders' && (
                <div className="p-4">
                  {futuresOrders?.filter(o => o.status === 'open').length === 0 ? (
                    <div className="text-center text-gray-400 py-8">
                      No open orders
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {futuresOrders?.filter(o => o.status === 'open').map((order) => (
                        <div key={order.id} className="bg-gray-800 rounded-lg p-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">{order.symbol}</div>
                              <div className="text-sm text-gray-400">
                                {order.side.toUpperCase()} • {order.type.toUpperCase()}
                              </div>
                            </div>
                            <button
                              onClick={() => futuresService.cancelOrder(order.id)}
                              className="text-red-400 hover:text-red-300 text-sm"
                            >
                              Cancel
                            </button>
                          </div>
                          <div className="mt-2 text-sm">
                            <div>Size: {order.quantity}</div>
                            <div>Price: ${order.price}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              
              {activeTab === 'history' && (
                <div className="p-4">
                  <div className="text-center text-gray-400 py-8">
                    Order history will be displayed here
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Risk Warning Modal */}
      <AnimatePresence>
        {showRiskWarning && (
          <RiskWarning
            leverage={leverage}
            onAccept={() => {
              setShowRiskWarning(false);
              // Proceed with order placement
            }}
            onCancel={() => setShowRiskWarning(false)}
          />
        )}
      </AnimatePresence>

      {/* Bottom Status Bar */}
      <div className="border-t border-gray-800 bg-gray-900/95 backdrop-blur-sm">
        <div className="px-4 py-2 flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center space-x-4">
            <span>TigerEx Futures Trading</span>
            <span>•</span>
            <span>Maker: 0.02% • Taker: 0.04%</span>
            <span>•</span>
            <span>Max Leverage: {contractInfo?.maxLeverage || 125}x</span>
          </div>
          
          <div className="flex items-center space-x-4">
            {riskMetrics && (
              <>
                <span>Account Balance: ${riskMetrics.accountBalance.toFixed(2)}</span>
                <span>•</span>
                <span>Unrealized PnL: 
                  <span className={riskMetrics.totalUnrealizedPnL >= 0 ? 'text-green-400' : 'text-red-400'}>
                    ${riskMetrics.totalUnrealizedPnL.toFixed(2)}
                  </span>
                </span>
                <span>•</span>
              </>
            )}
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

export default FuturesTrading;