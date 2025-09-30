import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { 
  MagnifyingGlassIcon,
  FunnelIcon,
  ChatBubbleLeftRightIcon,
  ShieldCheckIcon,
  ClockIcon,
  CurrencyDollarIcon,
  UserIcon,
  StarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

// Components
import P2POrderCard from '../../components/p2p/P2POrderCard';
import P2POrderForm from '../../components/p2p/P2POrderForm';
import P2PTradeModal from '../../components/p2p/P2PTradeModal';
import P2PChat from '../../components/p2p/P2PChat';
import PaymentMethodSelector from '../../components/p2p/PaymentMethodSelector';
import P2PFilters from '../../components/p2p/P2PFilters';
import UserRating from '../../components/p2p/UserRating';

// Hooks
import { useAuth } from '../../hooks/useAuth';
import { useWebSocket } from '../../hooks/useWebSocket';

// Services
import { p2pService } from '../../services/p2pService';

// Types
import { P2POrder, P2PTrade, PaymentMethod } from '../../types/p2p';

const P2PTrading: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  // State
  const [activeTab, setActiveTab] = useState<'buy' | 'sell'>('buy');
  const [selectedCurrency, setSelectedCurrency] = useState('BTC');
  const [selectedFiat, setSelectedFiat] = useState('USD');
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [selectedTrade, setSelectedTrade] = useState<P2PTrade | null>(null);
  const [showTradeModal, setShowTradeModal] = useState(false);
  const [filters, setFilters] = useState({
    paymentMethods: [] as string[],
    minAmount: '',
    maxAmount: '',
    onlineOnly: false,
    verifiedOnly: false,
  });

  // WebSocket connection
  const { socket, isConnected } = useWebSocket('/p2p');

  // Queries
  const { data: p2pOrders, isLoading: ordersLoading, refetch: refetchOrders } = useQuery({
    queryKey: ['p2pOrders', activeTab, selectedCurrency, selectedFiat, filters],
    queryFn: () => p2pService.getOrders({
      type: activeTab === 'buy' ? 'sell' : 'buy', // Show opposite orders
      currency: selectedCurrency,
      fiatCurrency: selectedFiat,
      ...filters,
    }),
    refetchInterval: 10000,
  });

  const { data: myOrders } = useQuery({
    queryKey: ['myP2POrders', user?.id],
    queryFn: () => p2pService.getMyOrders(),
    enabled: !!user,
    refetchInterval: 15000,
  });

  const { data: myTrades } = useQuery({
    queryKey: ['myP2PTrades', user?.id],
    queryFn: () => p2pService.getMyTrades(),
    enabled: !!user,
    refetchInterval: 10000,
  });

  const { data: paymentMethods } = useQuery({
    queryKey: ['paymentMethods', user?.id],
    queryFn: () => p2pService.getPaymentMethods(),
    enabled: !!user,
  });

  const { data: currencies } = useQuery({
    queryKey: ['p2pCurrencies'],
    queryFn: () => p2pService.getSupportedCurrencies(),
  });

  const { data: fiatCurrencies } = useQuery({
    queryKey: ['fiatCurrencies'],
    queryFn: () => p2pService.getSupportedFiatCurrencies(),
  });

  // Mutations
  const createOrderMutation = useMutation({
    mutationFn: p2pService.createOrder,
    onSuccess: () => {
      toast.success('P2P order created successfully');
      setShowOrderForm(false);
      queryClient.invalidateQueries({ queryKey: ['myP2POrders'] });
      refetchOrders();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create P2P order');
    },
  });

  const createTradeMutation = useMutation({
    mutationFn: p2pService.createTrade,
    onSuccess: (trade) => {
      toast.success('Trade initiated successfully');
      setSelectedTrade(trade);
      setShowTradeModal(true);
      queryClient.invalidateQueries({ queryKey: ['myP2PTrades'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to initiate trade');
    },
  });

  const markPaymentSentMutation = useMutation({
    mutationFn: p2pService.markPaymentSent,
    onSuccess: () => {
      toast.success('Payment marked as sent');
      queryClient.invalidateQueries({ queryKey: ['myP2PTrades'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to mark payment as sent');
    },
  });

  const confirmPaymentMutation = useMutation({
    mutationFn: p2pService.confirmPayment,
    onSuccess: () => {
      toast.success('Payment confirmed, trade completed');
      queryClient.invalidateQueries({ queryKey: ['myP2PTrades'] });
      setShowTradeModal(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to confirm payment');
    },
  });

  const createDisputeMutation = useMutation({
    mutationFn: p2pService.createDispute,
    onSuccess: () => {
      toast.success('Dispute created, admin will review');
      queryClient.invalidateQueries({ queryKey: ['myP2PTrades'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create dispute');
    },
  });

  // WebSocket event handlers
  useEffect(() => {
    if (!socket || !isConnected) return;

    socket.emit('subscribe', { channel: 'p2p_orders' });

    socket.on('p2p_order_update', () => {
      refetchOrders();
    });

    if (user) {
      socket.emit('subscribe', { 
        channel: 'p2p_user_updates',
        userId: user.id 
      });

      socket.on('p2p_trade_update', () => {
        queryClient.invalidateQueries({ queryKey: ['myP2PTrades'] });
      });

      socket.on('p2p_message', (data) => {
        // Handle new chat messages
        queryClient.setQueryData(['p2pChat', data.tradeId], (old: any) => {
          return old ? [...old, data.message] : [data.message];
        });
      });
    }

    return () => {
      socket.emit('unsubscribe', { channel: 'p2p_orders' });
      if (user) {
        socket.emit('unsubscribe', { 
          channel: 'p2p_user_updates',
          userId: user.id 
        });
      }
    };
  }, [socket, isConnected, user, queryClient, refetchOrders]);

  // Handle trade initiation
  const handleInitiateTrade = useCallback((order: P2POrder, amount: number, paymentMethod: string) => {
    createTradeMutation.mutate({
      orderId: order.id,
      amount,
      paymentMethod,
    });
  }, [createTradeMutation]);

  // Handle order creation
  const handleCreateOrder = useCallback((orderData: any) => {
    createOrderMutation.mutate(orderData);
  }, [createOrderMutation]);

  // Filter orders based on search criteria
  const filteredOrders = p2pOrders?.filter((order: P2POrder) => {
    if (filters.minAmount && order.minAmount < parseFloat(filters.minAmount)) return false;
    if (filters.maxAmount && order.maxAmount > parseFloat(filters.maxAmount)) return false;
    if (filters.onlineOnly && !order.user.isOnline) return false;
    if (filters.verifiedOnly && !order.user.isVerified) return false;
    if (filters.paymentMethods.length > 0) {
      const orderPaymentMethods = order.paymentMethods.map(pm => pm.type);
      if (!filters.paymentMethods.some(pm => orderPaymentMethods.includes(pm))) return false;
    }
    return true;
  }) || [];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="border-b border-gray-800 bg-gray-900/95 backdrop-blur-sm sticky top-0 z-40">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <h1 className="text-2xl font-bold">P2P Trading</h1>
              
              <div className="flex items-center space-x-4">
                <select
                  value={selectedCurrency}
                  onChange={(e) => setSelectedCurrency(e.target.value)}
                  className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
                >
                  {currencies?.map((currency) => (
                    <option key={currency} value={currency}>{currency}</option>
                  ))}
                </select>
                
                <select
                  value={selectedFiat}
                  onChange={(e) => setSelectedFiat(e.target.value)}
                  className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
                >
                  {fiatCurrencies?.map((fiat) => (
                    <option key={fiat.code} value={fiat.code}>
                      {fiat.code} - {fiat.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowOrderForm(true)}
                className="bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Post Ad
              </button>
              
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

      <div className="flex">
        {/* Main Content */}
        <div className="flex-1">
          {/* Tabs and Filters */}
          <div className="border-b border-gray-800">
            <div className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => setActiveTab('buy')}
                    className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                      activeTab === 'buy'
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    Buy {selectedCurrency}
                  </button>
                  <button
                    onClick={() => setActiveTab('sell')}
                    className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                      activeTab === 'sell'
                        ? 'bg-red-500 text-white'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    Sell {selectedCurrency}
                  </button>
                </div>

                <P2PFilters
                  filters={filters}
                  onFiltersChange={setFilters}
                  paymentMethods={paymentMethods || []}
                />
              </div>
            </div>
          </div>

          {/* Orders List */}
          <div className="p-6">
            {ordersLoading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
              </div>
            ) : filteredOrders.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  No {activeTab === 'buy' ? 'sell' : 'buy'} orders available
                </div>
                <button
                  onClick={() => setShowOrderForm(true)}
                  className="bg-orange-500 hover:bg-orange-600 px-6 py-2 rounded-lg font-medium transition-colors"
                >
                  Create First Order
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Table Header */}
                <div className="grid grid-cols-12 gap-4 px-4 py-2 text-sm text-gray-400 border-b border-gray-800">
                  <div className="col-span-2">Advertiser</div>
                  <div className="col-span-2">Price</div>
                  <div className="col-span-2">Limit/Available</div>
                  <div className="col-span-3">Payment</div>
                  <div className="col-span-2">Trade</div>
                  <div className="col-span-1">Action</div>
                </div>

                {/* Orders */}
                {filteredOrders.map((order) => (
                  <P2POrderCard
                    key={order.id}
                    order={order}
                    onTrade={handleInitiateTrade}
                    userType={activeTab}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar - My Orders & Trades */}
        <div className="w-96 border-l border-gray-800 bg-gray-900/50">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold">My P2P Activity</h2>
            </div>

            {/* My Orders */}
            <div className="mb-8">
              <h3 className="text-md font-medium mb-4 flex items-center">
                <CurrencyDollarIcon className="w-5 h-5 mr-2" />
                My Orders ({myOrders?.length || 0})
              </h3>
              
              {myOrders?.length === 0 ? (
                <div className="text-center text-gray-400 py-6">
                  No active orders
                </div>
              ) : (
                <div className="space-y-3">
                  {myOrders?.slice(0, 3).map((order) => (
                    <div key={order.id} className="bg-gray-800 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="font-medium">{order.type.toUpperCase()} {order.currency}</div>
                          <div className="text-sm text-gray-400">
                            ${order.price} • {order.fiatCurrency}
                          </div>
                        </div>
                        <div className={`px-2 py-1 rounded text-xs ${
                          order.status === 'active' 
                            ? 'bg-green-900/30 text-green-400'
                            : 'bg-gray-700 text-gray-300'
                        }`}>
                          {order.status}
                        </div>
                      </div>
                      <div className="text-sm text-gray-400">
                        Available: {order.availableAmount} {order.currency}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* My Trades */}
            <div>
              <h3 className="text-md font-medium mb-4 flex items-center">
                <ChatBubbleLeftRightIcon className="w-5 h-5 mr-2" />
                Active Trades ({myTrades?.filter(t => t.status !== 'completed').length || 0})
              </h3>
              
              {myTrades?.filter(t => t.status !== 'completed').length === 0 ? (
                <div className="text-center text-gray-400 py-6">
                  No active trades
                </div>
              ) : (
                <div className="space-y-3">
                  {myTrades?.filter(t => t.status !== 'completed').map((trade) => (
                    <div key={trade.id} className="bg-gray-800 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="font-medium">
                            {trade.type.toUpperCase()} {trade.amount} {trade.currency}
                          </div>
                          <div className="text-sm text-gray-400">
                            with @{trade.counterparty.username}
                          </div>
                        </div>
                        <div className={`px-2 py-1 rounded text-xs ${
                          trade.status === 'payment_pending' 
                            ? 'bg-yellow-900/30 text-yellow-400'
                            : trade.status === 'payment_sent'
                            ? 'bg-blue-900/30 text-blue-400'
                            : 'bg-gray-700 text-gray-300'
                        }`}>
                          {trade.status.replace('_', ' ')}
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between mt-3">
                        <div className="text-sm text-gray-400">
                          ${trade.totalAmount} {trade.fiatCurrency}
                        </div>
                        <button
                          onClick={() => {
                            setSelectedTrade(trade);
                            setShowTradeModal(true);
                          }}
                          className="text-orange-400 hover:text-orange-300 text-sm"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Order Form Modal */}
      <AnimatePresence>
        {showOrderForm && (
          <P2POrderForm
            currencies={currencies || []}
            fiatCurrencies={fiatCurrencies || []}
            paymentMethods={paymentMethods || []}
            onSubmit={handleCreateOrder}
            onClose={() => setShowOrderForm(false)}
            loading={createOrderMutation.isPending}
          />
        )}
      </AnimatePresence>

      {/* Trade Modal */}
      <AnimatePresence>
        {showTradeModal && selectedTrade && (
          <P2PTradeModal
            trade={selectedTrade}
            onClose={() => {
              setShowTradeModal(false);
              setSelectedTrade(null);
            }}
            onMarkPaymentSent={() => markPaymentSentMutation.mutate(selectedTrade.id)}
            onConfirmPayment={() => confirmPaymentMutation.mutate(selectedTrade.id)}
            onCreateDispute={(reason: string) => 
              createDisputeMutation.mutate({ tradeId: selectedTrade.id, reason })
            }
            loading={{
              markPayment: markPaymentSentMutation.isPending,
              confirmPayment: confirmPaymentMutation.isPending,
              createDispute: createDisputeMutation.isPending,
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default P2PTrading;