import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  BarChart3,
  Wallet,
  ArrowUpDown,
  Star,
  Search,
  RefreshCw,
  AlertTriangle,
  Target,
  Zap,
  Shield,
} from 'lucide-react';

interface FuturesContract {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  contractType: 'USD-M' | 'COIN-M';
  price: number;
  change24h: number;
  volume24h: number;
  openInterest: number;
  fundingRate: number;
  nextFundingTime: string;
  maxLeverage: number;
}

interface FuturesPosition {
  id: string;
  symbol: string;
  side: 'long' | 'short';
  size: number;
  entryPrice: number;
  markPrice: number;
  leverage: number;
  margin: number;
  unrealizedPnl: number;
  roe: number;
  liquidationPrice: number;
  marginRatio: number;
}

interface FuturesOrder {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  type:
    | 'market'
    | 'limit'
    | 'stop'
    | 'take_profit'
    | 'stop_market'
    | 'take_profit_market';
  quantity: number;
  price?: number;
  stopPrice?: number;
  filled: number;
  status: 'pending' | 'filled' | 'cancelled' | 'partially_filled';
  reduceOnly: boolean;
  timeInForce: 'GTC' | 'IOC' | 'FOK';
  createdAt: string;
}

const FuturesTradingPage: React.FC = () => {
  const [selectedContract, setSelectedContract] =
    useState<FuturesContract | null>(null);
  const [contracts, setContracts] = useState<FuturesContract[]>([]);
  const [positions, setPositions] = useState<FuturesPosition[]>([]);
  const [orders, setOrders] = useState<FuturesOrder[]>([]);
  const [orderType, setOrderType] = useState<
    'market' | 'limit' | 'stop' | 'take_profit'
  >('limit');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [orderQuantity, setOrderQuantity] = useState('');
  const [orderPrice, setOrderPrice] = useState('');
  const [stopPrice, setStopPrice] = useState('');
  const [leverage, setLeverage] = useState(10);
  const [marginType, setMarginType] = useState<'cross' | 'isolated'>('cross');
  const [reduceOnly, setReduceOnly] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [favorites, setFavorites] = useState<string[]>([]);

  useEffect(() => {
    // Mock futures contracts data
    const mockContracts: FuturesContract[] = [
      {
        symbol: 'BTCUSDT',
        baseAsset: 'BTC',
        quoteAsset: 'USDT',
        contractType: 'USD-M',
        price: 45234.56,
        change24h: 2.34,
        volume24h: 2345678901.23,
        openInterest: 1234567.89,
        fundingRate: 0.0001,
        nextFundingTime: '2024-01-15T16:00:00Z',
        maxLeverage: 125,
      },
      {
        symbol: 'ETHUSDT',
        baseAsset: 'ETH',
        quoteAsset: 'USDT',
        contractType: 'USD-M',
        price: 2834.12,
        change24h: -1.23,
        volume24h: 1876543210.45,
        openInterest: 987654.32,
        fundingRate: -0.0002,
        nextFundingTime: '2024-01-15T16:00:00Z',
        maxLeverage: 100,
      },
      {
        symbol: 'BTCUSD_PERP',
        baseAsset: 'BTC',
        quoteAsset: 'USD',
        contractType: 'COIN-M',
        price: 45234.56,
        change24h: 2.34,
        volume24h: 567890123.45,
        openInterest: 456789.12,
        fundingRate: 0.0003,
        nextFundingTime: '2024-01-15T16:00:00Z',
        maxLeverage: 125,
      },
      {
        symbol: 'ADAUSDT',
        baseAsset: 'ADA',
        quoteAsset: 'USDT',
        contractType: 'USD-M',
        price: 0.4567,
        change24h: 5.67,
        volume24h: 234567890.12,
        openInterest: 123456.78,
        fundingRate: 0.0001,
        nextFundingTime: '2024-01-15T16:00:00Z',
        maxLeverage: 75,
      },
    ];

    const mockPositions: FuturesPosition[] = [
      {
        id: 'pos-001',
        symbol: 'BTCUSDT',
        side: 'long',
        size: 0.5,
        entryPrice: 44500.0,
        markPrice: 45234.56,
        leverage: 10,
        margin: 2225.0,
        unrealizedPnl: 367.28,
        roe: 16.51,
        liquidationPrice: 40050.0,
        marginRatio: 0.15,
      },
      {
        id: 'pos-002',
        symbol: 'ETHUSDT',
        side: 'short',
        size: 2.0,
        entryPrice: 2900.0,
        markPrice: 2834.12,
        leverage: 5,
        margin: 1160.0,
        unrealizedPnl: 131.76,
        roe: 11.36,
        liquidationPrice: 3480.0,
        marginRatio: 0.08,
      },
    ];

    const mockOrders: FuturesOrder[] = [
      {
        id: 'order-001',
        symbol: 'BTCUSDT',
        side: 'buy',
        type: 'limit',
        quantity: 0.1,
        price: 44000.0,
        filled: 0,
        status: 'pending',
        reduceOnly: false,
        timeInForce: 'GTC',
        createdAt: '2024-01-15T14:30:00Z',
      },
      {
        id: 'order-002',
        symbol: 'ETHUSDT',
        side: 'sell',
        type: 'stop',
        quantity: 1.0,
        stopPrice: 2750.0,
        filled: 0,
        status: 'pending',
        reduceOnly: true,
        timeInForce: 'GTC',
        createdAt: '2024-01-15T14:25:00Z',
      },
    ];

    setContracts(mockContracts);
    setSelectedContract(mockContracts[0]);
    setPositions(mockPositions);
    setOrders(mockOrders);
  }, []);

  const handlePlaceOrder = () => {
    if (!selectedContract || !orderQuantity) return;

    const newOrder: FuturesOrder = {
      id: `order-${Date.now()}`,
      symbol: selectedContract.symbol,
      side: orderSide,
      type: orderType,
      quantity: parseFloat(orderQuantity),
      price: orderType === 'limit' ? parseFloat(orderPrice) : undefined,
      stopPrice:
        orderType === 'stop' || orderType === 'take_profit'
          ? parseFloat(stopPrice)
          : undefined,
      filled: 0,
      status: 'pending',
      reduceOnly: reduceOnly,
      timeInForce: 'GTC',
      createdAt: new Date().toISOString(),
    };

    setOrders((prev) => [newOrder, ...prev]);
    setOrderQuantity('');
    setOrderPrice('');
    setStopPrice('');
    alert(`${orderSide.toUpperCase()} ${orderType} order placed successfully!`);
  };

  const handleClosePosition = (positionId: string) => {
    setPositions((prev) => prev.filter((pos) => pos.id !== positionId));
    alert(`Position ${positionId} closed successfully`);
  };

  const handleCancelOrder = (orderId: string) => {
    setOrders((prev) =>
      prev.map((order) =>
        order.id === orderId
          ? { ...order, status: 'cancelled' as const }
          : order
      )
    );
  };

  const handleAdjustLeverage = (symbol: string, newLeverage: number) => {
    setPositions((prev) =>
      prev.map((pos) =>
        pos.symbol === symbol ? { ...pos, leverage: newLeverage } : pos
      )
    );
    alert(`Leverage for ${symbol} adjusted to ${newLeverage}x`);
  };

  const toggleFavorite = (symbol: string) => {
    setFavorites((prev) =>
      prev.includes(symbol)
        ? prev.filter((s) => s !== symbol)
        : [...prev, symbol]
    );
  };

  const filteredContracts = contracts.filter(
    (contract) =>
      contract.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contract.baseAsset.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contract.quoteAsset.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getChangeColor = (change: number) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const getPnlColor = (pnl: number) => {
    return pnl >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const getOrderStatusColor = (status: string) => {
    switch (status) {
      case 'filled':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'partially_filled':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const getMarginRatioColor = (ratio: number) => {
    if (ratio < 0.1) return 'text-green-600';
    if (ratio < 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const totalUnrealizedPnl = positions.reduce(
    (sum, pos) => sum + pos.unrealizedPnl,
    0
  );
  const totalMargin = positions.reduce((sum, pos) => sum + pos.margin, 0);

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Futures Trading</h1>
          <p className="text-gray-600 mt-2">
            Trade cryptocurrency futures with up to 125x leverage
          </p>
        </div>

        {/* Account Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Wallet className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold text-blue-600">
                    $12,345.67
                  </div>
                  <div className="text-sm text-gray-600">Futures Balance</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Target className="h-5 w-5 text-purple-600" />
                <div>
                  <div className="text-2xl font-bold text-purple-600">
                    ${totalMargin.toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-600">Total Margin</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-green-600" />
                <div>
                  <div
                    className={`text-2xl font-bold ${getPnlColor(totalUnrealizedPnl)}`}
                  >
                    {totalUnrealizedPnl >= 0 ? '+' : ''}$
                    {totalUnrealizedPnl.toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-600">Unrealized PnL</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-orange-600" />
                <div>
                  <div className="text-2xl font-bold text-orange-600">
                    {positions.length}
                  </div>
                  <div className="text-sm text-gray-600">Open Positions</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-12 gap-4 h-[calc(100vh-300px)]">
          {/* Contracts Panel */}
          <div className="col-span-3">
            <Card className="h-full">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Futures Contracts</CardTitle>
                  <Button size="sm" variant="outline">
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search contracts..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 h-8"
                  />
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="space-y-1 max-h-[600px] overflow-y-auto">
                  {filteredContracts.map((contract) => (
                    <div
                      key={contract.symbol}
                      className={`p-3 cursor-pointer hover:bg-gray-50 border-l-2 ${
                        selectedContract?.symbol === contract.symbol
                          ? 'border-l-blue-500 bg-blue-50'
                          : 'border-l-transparent'
                      }`}
                      onClick={() => setSelectedContract(contract)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleFavorite(contract.symbol);
                            }}
                            className={`${
                              favorites.includes(contract.symbol)
                                ? 'text-yellow-500'
                                : 'text-gray-400'
                            }`}
                          >
                            <Star className="h-4 w-4" />
                          </button>
                          <div>
                            <div className="font-semibold text-sm">
                              {contract.symbol}
                            </div>
                            <div className="text-xs text-gray-500">
                              {contract.contractType} • {contract.maxLeverage}x
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold text-sm">
                            ${contract.price.toLocaleString()}
                          </div>
                          <div
                            className={`text-xs ${getChangeColor(contract.change24h)}`}
                          >
                            {contract.change24h >= 0 ? '+' : ''}
                            {contract.change24h.toFixed(2)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Trading Area */}
          <div className="col-span-6 space-y-4">
            {/* Price Header */}
            {selectedContract && (
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <h2 className="text-2xl font-bold">
                        {selectedContract.symbol}
                      </h2>
                      <Badge variant="outline">
                        {selectedContract.contractType}
                      </Badge>
                      <div className="text-3xl font-bold">
                        ${selectedContract.price.toLocaleString()}
                      </div>
                      <div
                        className={`flex items-center space-x-1 ${getChangeColor(selectedContract.change24h)}`}
                      >
                        {selectedContract.change24h >= 0 ? (
                          <TrendingUp className="h-5 w-5" />
                        ) : (
                          <TrendingDown className="h-5 w-5" />
                        )}
                        <span className="font-semibold">
                          {selectedContract.change24h >= 0 ? '+' : ''}
                          {selectedContract.change24h.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-6 text-sm">
                      <div>
                        <div className="text-gray-500">24h Volume</div>
                        <div className="font-semibold">
                          ${(selectedContract.volume24h / 1000000).toFixed(1)}M
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-500">Open Interest</div>
                        <div className="font-semibold">
                          ${(selectedContract.openInterest / 1000).toFixed(1)}K
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-500">Funding Rate</div>
                        <div
                          className={`font-semibold ${getChangeColor(selectedContract.fundingRate)}`}
                        >
                          {(selectedContract.fundingRate * 100).toFixed(4)}%
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Chart Placeholder */}
            <Card className="flex-1">
              <CardContent className="p-4 h-96">
                <div className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <div className="text-gray-500">Advanced Futures Chart</div>
                    <div className="text-sm text-gray-400">
                      Real-time price action and indicators
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Positions and Orders */}
            <Tabs defaultValue="positions" className="space-y-4">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="positions">
                  Positions ({positions.length})
                </TabsTrigger>
                <TabsTrigger value="orders">
                  Orders (
                  {
                    orders.filter(
                      (o) => o.status !== 'filled' && o.status !== 'cancelled'
                    ).length
                  }
                  )
                </TabsTrigger>
              </TabsList>

              <TabsContent value="positions">
                <Card>
                  <CardContent className="p-0">
                    <div className="space-y-2">
                      {positions.map((position) => (
                        <div
                          key={position.id}
                          className="p-4 border-b last:border-b-0 hover:bg-gray-50"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                              <Badge
                                className={
                                  position.side === 'long'
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-red-100 text-red-800'
                                }
                              >
                                {position.side.toUpperCase()}
                              </Badge>
                              <div>
                                <div className="font-semibold">
                                  {position.symbol}
                                </div>
                                <div className="text-sm text-gray-600">
                                  Size: {position.size} • {position.leverage}x
                                </div>
                              </div>
                            </div>

                            <div className="flex items-center space-x-6 text-sm">
                              <div className="text-center">
                                <div className="text-gray-500">Entry Price</div>
                                <div className="font-semibold">
                                  ${position.entryPrice.toFixed(2)}
                                </div>
                              </div>
                              <div className="text-center">
                                <div className="text-gray-500">Mark Price</div>
                                <div className="font-semibold">
                                  ${position.markPrice.toFixed(2)}
                                </div>
                              </div>
                              <div className="text-center">
                                <div className="text-gray-500">PnL</div>
                                <div
                                  className={`font-semibold ${getPnlColor(position.unrealizedPnl)}`}
                                >
                                  {position.unrealizedPnl >= 0 ? '+' : ''}$
                                  {position.unrealizedPnl.toFixed(2)}
                                </div>
                              </div>
                              <div className="text-center">
                                <div className="text-gray-500">ROE</div>
                                <div
                                  className={`font-semibold ${getPnlColor(position.roe)}`}
                                >
                                  {position.roe >= 0 ? '+' : ''}
                                  {position.roe.toFixed(2)}%
                                </div>
                              </div>
                              <div className="text-center">
                                <div className="text-gray-500">
                                  Margin Ratio
                                </div>
                                <div
                                  className={`font-semibold ${getMarginRatioColor(position.marginRatio)}`}
                                >
                                  {(position.marginRatio * 100).toFixed(2)}%
                                </div>
                              </div>
                            </div>

                            <div className="flex space-x-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() =>
                                  handleAdjustLeverage(
                                    position.symbol,
                                    position.leverage === 10 ? 20 : 10
                                  )
                                }
                              >
                                Adjust Leverage
                              </Button>
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => handleClosePosition(position.id)}
                              >
                                Close
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                      {positions.length === 0 && (
                        <div className="p-8 text-center text-gray-500">
                          No open positions
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="orders">
                <Card>
                  <CardContent className="p-0">
                    <div className="space-y-2">
                      {orders
                        .filter(
                          (order) =>
                            order.status !== 'filled' &&
                            order.status !== 'cancelled'
                        )
                        .map((order) => (
                          <div
                            key={order.id}
                            className="p-4 border-b last:border-b-0 hover:bg-gray-50"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-4">
                                <Badge
                                  className={
                                    order.side === 'buy'
                                      ? 'bg-green-100 text-green-800'
                                      : 'bg-red-100 text-red-800'
                                  }
                                >
                                  {order.side.toUpperCase()}
                                </Badge>
                                <div>
                                  <div className="font-semibold">
                                    {order.symbol}
                                  </div>
                                  <div className="text-sm text-gray-600">
                                    {order.type} • {order.quantity} •{' '}
                                    {order.reduceOnly ? 'Reduce Only' : 'Open'}
                                  </div>
                                </div>
                              </div>

                              <div className="flex items-center space-x-6 text-sm">
                                <div className="text-center">
                                  <div className="text-gray-500">Quantity</div>
                                  <div className="font-semibold">
                                    {order.quantity}
                                  </div>
                                </div>
                                {order.price && (
                                  <div className="text-center">
                                    <div className="text-gray-500">Price</div>
                                    <div className="font-semibold">
                                      ${order.price.toFixed(2)}
                                    </div>
                                  </div>
                                )}
                                {order.stopPrice && (
                                  <div className="text-center">
                                    <div className="text-gray-500">
                                      Stop Price
                                    </div>
                                    <div className="font-semibold">
                                      ${order.stopPrice.toFixed(2)}
                                    </div>
                                  </div>
                                )}
                                <div className="text-center">
                                  <Badge
                                    className={getOrderStatusColor(
                                      order.status
                                    )}
                                  >
                                    {order.status.replace('_', ' ')}
                                  </Badge>
                                </div>
                              </div>

                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleCancelOrder(order.id)}
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        ))}
                      {orders.filter(
                        (order) =>
                          order.status !== 'filled' &&
                          order.status !== 'cancelled'
                      ).length === 0 && (
                        <div className="p-8 text-center text-gray-500">
                          No open orders
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Trading Panel */}
          <div className="col-span-3 space-y-4">
            {/* Order Form */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Place Order</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Tabs
                  value={orderSide}
                  onValueChange={(value) =>
                    setOrderSide(value as 'buy' | 'sell')
                  }
                >
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="buy" className="text-green-600">
                      Long
                    </TabsTrigger>
                    <TabsTrigger value="sell" className="text-red-600">
                      Short
                    </TabsTrigger>
                  </TabsList>
                </Tabs>

                <Select
                  value={orderType}
                  onValueChange={(value) => setOrderType(value as any)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="market">Market</SelectItem>
                    <SelectItem value="limit">Limit</SelectItem>
                    <SelectItem value="stop">Stop</SelectItem>
                    <SelectItem value="take_profit">Take Profit</SelectItem>
                  </SelectContent>
                </Select>

                {(orderType === 'limit' ||
                  orderType === 'stop' ||
                  orderType === 'take_profit') && (
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Price (USDT)
                    </label>
                    <Input
                      type="number"
                      placeholder="0.00"
                      value={orderPrice}
                      onChange={(e) => setOrderPrice(e.target.value)}
                    />
                  </div>
                )}

                {(orderType === 'stop' || orderType === 'take_profit') && (
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Stop Price (USDT)
                    </label>
                    <Input
                      type="number"
                      placeholder="0.00"
                      value={stopPrice}
                      onChange={(e) => setStopPrice(e.target.value)}
                    />
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium mb-1">
                    Quantity ({selectedContract?.baseAsset})
                  </label>
                  <Input
                    type="number"
                    placeholder="0.00"
                    value={orderQuantity}
                    onChange={(e) => setOrderQuantity(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">
                    Leverage: {leverage}x
                  </label>
                  <input
                    type="range"
                    min="1"
                    max={selectedContract?.maxLeverage || 125}
                    value={leverage}
                    onChange={(e) => setLeverage(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>1x</span>
                    <span>{selectedContract?.maxLeverage || 125}x</span>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={reduceOnly}
                      onChange={(e) => setReduceOnly(e.target.checked)}
                    />
                    <span className="text-sm">Reduce Only</span>
                  </label>
                </div>

                <div className="text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>Margin Required:</span>
                    <span>
                      {orderQuantity && orderPrice
                        ? `${((parseFloat(orderQuantity) * parseFloat(orderPrice)) / leverage).toFixed(2)} USDT`
                        : '0.00 USDT'}
                    </span>
                  </div>
                </div>

                <Button
                  className={`w-full ${
                    orderSide === 'buy'
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-red-600 hover:bg-red-700'
                  }`}
                  onClick={handlePlaceOrder}
                  disabled={
                    !orderQuantity ||
                    ((orderType === 'limit' ||
                      orderType === 'stop' ||
                      orderType === 'take_profit') &&
                      !orderPrice)
                  }
                >
                  {orderSide === 'buy' ? 'Open Long' : 'Open Short'}{' '}
                  {selectedContract?.baseAsset}
                </Button>
              </CardContent>
            </Card>

            {/* Account Info */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center">
                  <Wallet className="h-5 w-5 mr-2" />
                  Account Info
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Available Balance</span>
                  <span className="font-semibold">$12,345.67</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Margin</span>
                  <span className="font-semibold">
                    ${totalMargin.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Unrealized PnL</span>
                  <span
                    className={`font-semibold ${getPnlColor(totalUnrealizedPnl)}`}
                  >
                    {totalUnrealizedPnl >= 0 ? '+' : ''}$
                    {totalUnrealizedPnl.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Margin Mode</span>
                  <Select
                    value={marginType}
                    onValueChange={(value) => setMarginType(value as any)}
                  >
                    <SelectTrigger className="w-24 h-6">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="cross">Cross</SelectItem>
                      <SelectItem value="isolated">Isolated</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button variant="outline" className="w-full">
                  <ArrowUpDown className="h-4 w-4 mr-2" />
                  Transfer
                </Button>
              </CardContent>
            </Card>

            {/* Risk Warning */}
            <Card className="border-orange-200 bg-orange-50">
              <CardContent className="p-4">
                <div className="flex items-start space-x-2">
                  <AlertTriangle className="h-5 w-5 text-orange-600 mt-0.5" />
                  <div className="text-sm text-orange-800">
                    <div className="font-semibold mb-1">Risk Warning</div>
                    <div>
                      Futures trading involves substantial risk of loss. Only
                      trade with funds you can afford to lose.
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FuturesTradingPage;
