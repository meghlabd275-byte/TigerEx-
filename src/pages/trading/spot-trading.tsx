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
  Clock,
  Wallet,
  ArrowUpDown,
  Star,
  Search,
  Filter,
  RefreshCw,
} from 'lucide-react';

interface TradingPair {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  price: number;
  change24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
}

interface OrderBookEntry {
  price: number;
  quantity: number;
  total: number;
}

interface Trade {
  id: string;
  price: number;
  quantity: number;
  time: string;
  side: 'buy' | 'sell';
}

interface UserOrder {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop-loss' | 'take-profit';
  quantity: number;
  price?: number;
  filled: number;
  status: 'pending' | 'filled' | 'cancelled' | 'partially_filled';
  createdAt: string;
}

const SpotTradingPage: React.FC = () => {
  const [selectedPair, setSelectedPair] = useState<TradingPair | null>(null);
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [orderBook, setOrderBook] = useState<{
    bids: OrderBookEntry[];
    asks: OrderBookEntry[];
  }>({ bids: [], asks: [] });
  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [userOrders, setUserOrders] = useState<UserOrder[]>([]);
  const [orderType, setOrderType] = useState<'market' | 'limit'>('limit');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [orderQuantity, setOrderQuantity] = useState('');
  const [orderPrice, setOrderPrice] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [favorites, setFavorites] = useState<string[]>([]);

  useEffect(() => {
    // Mock trading pairs data
    const mockPairs: TradingPair[] = [
      {
        symbol: 'BTCUSDT',
        baseAsset: 'BTC',
        quoteAsset: 'USDT',
        price: 45234.56,
        change24h: 2.34,
        volume24h: 1234567.89,
        high24h: 46000.0,
        low24h: 44500.0,
      },
      {
        symbol: 'ETHUSDT',
        baseAsset: 'ETH',
        quoteAsset: 'USDT',
        price: 2834.12,
        change24h: -1.23,
        volume24h: 987654.32,
        high24h: 2900.0,
        low24h: 2800.0,
      },
      {
        symbol: 'ADAUSDT',
        baseAsset: 'ADA',
        quoteAsset: 'USDT',
        price: 0.4567,
        change24h: 5.67,
        volume24h: 456789.12,
        high24h: 0.48,
        low24h: 0.43,
      },
    ];

    const mockOrderBook = {
      bids: [
        { price: 45230.0, quantity: 0.5234, total: 23678.12 },
        { price: 45225.0, quantity: 1.2345, total: 55823.45 },
        { price: 45220.0, quantity: 0.8765, total: 39645.23 },
        { price: 45215.0, quantity: 2.1234, total: 96012.34 },
        { price: 45210.0, quantity: 0.6789, total: 30698.45 },
      ],
      asks: [
        { price: 45235.0, quantity: 0.4321, total: 19543.21 },
        { price: 45240.0, quantity: 0.9876, total: 44678.9 },
        { price: 45245.0, quantity: 1.5432, total: 69823.45 },
        { price: 45250.0, quantity: 0.7654, total: 34634.56 },
        { price: 45255.0, quantity: 1.2109, total: 54789.12 },
      ],
    };

    const mockTrades: Trade[] = [
      {
        id: '1',
        price: 45234.56,
        quantity: 0.1234,
        time: '14:32:15',
        side: 'buy',
      },
      {
        id: '2',
        price: 45232.1,
        quantity: 0.5678,
        time: '14:32:10',
        side: 'sell',
      },
      {
        id: '3',
        price: 45235.0,
        quantity: 0.2345,
        time: '14:32:05',
        side: 'buy',
      },
      {
        id: '4',
        price: 45230.5,
        quantity: 0.8901,
        time: '14:32:00',
        side: 'sell',
      },
      {
        id: '5',
        price: 45236.78,
        quantity: 0.3456,
        time: '14:31:55',
        side: 'buy',
      },
    ];

    const mockUserOrders: UserOrder[] = [
      {
        id: 'order-1',
        symbol: 'BTCUSDT',
        side: 'buy',
        type: 'limit',
        quantity: 0.5,
        price: 45000.0,
        filled: 0.2,
        status: 'partially_filled',
        createdAt: '2024-01-15T14:30:00Z',
      },
      {
        id: 'order-2',
        symbol: 'ETHUSDT',
        side: 'sell',
        type: 'limit',
        quantity: 2.0,
        price: 2850.0,
        filled: 0,
        status: 'pending',
        createdAt: '2024-01-15T14:25:00Z',
      },
    ];

    setTradingPairs(mockPairs);
    setSelectedPair(mockPairs[0]);
    setOrderBook(mockOrderBook);
    setRecentTrades(mockTrades);
    setUserOrders(mockUserOrders);
  }, []);

  const handlePlaceOrder = () => {
    if (!selectedPair || !orderQuantity) return;

    const newOrder: UserOrder = {
      id: `order-${Date.now()}`,
      symbol: selectedPair.symbol,
      side: orderSide,
      type: orderType,
      quantity: parseFloat(orderQuantity),
      price: orderType === 'limit' ? parseFloat(orderPrice) : undefined,
      filled: 0,
      status: 'pending',
      createdAt: new Date().toISOString(),
    };

    setUserOrders((prev) => [newOrder, ...prev]);
    setOrderQuantity('');
    setOrderPrice('');
    alert(`${orderSide.toUpperCase()} order placed successfully!`);
  };

  const handleCancelOrder = (orderId: string) => {
    setUserOrders((prev) =>
      prev.map((order) =>
        order.id === orderId
          ? { ...order, status: 'cancelled' as const }
          : order
      )
    );
  };

  const toggleFavorite = (symbol: string) => {
    setFavorites((prev) =>
      prev.includes(symbol)
        ? prev.filter((s) => s !== symbol)
        : [...prev, symbol]
    );
  };

  const filteredPairs = tradingPairs.filter(
    (pair) =>
      pair.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      pair.baseAsset.toLowerCase().includes(searchTerm.toLowerCase()) ||
      pair.quoteAsset.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getChangeColor = (change: number) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600';
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

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Spot Trading</h1>
          <p className="text-gray-600 mt-2">
            Trade cryptocurrencies with zero fees
          </p>
        </div>

        <div className="grid grid-cols-12 gap-4 h-[calc(100vh-200px)]">
          {/* Trading Pairs Panel */}
          <div className="col-span-3">
            <Card className="h-full">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Markets</CardTitle>
                  <Button size="sm" variant="outline">
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search pairs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 h-8"
                  />
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="space-y-1 max-h-[600px] overflow-y-auto">
                  {filteredPairs.map((pair) => (
                    <div
                      key={pair.symbol}
                      className={`p-3 cursor-pointer hover:bg-gray-50 border-l-2 ${
                        selectedPair?.symbol === pair.symbol
                          ? 'border-l-blue-500 bg-blue-50'
                          : 'border-l-transparent'
                      }`}
                      onClick={() => setSelectedPair(pair)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleFavorite(pair.symbol);
                            }}
                            className={`${
                              favorites.includes(pair.symbol)
                                ? 'text-yellow-500'
                                : 'text-gray-400'
                            }`}
                          >
                            <Star className="h-4 w-4" />
                          </button>
                          <div>
                            <div className="font-semibold text-sm">
                              {pair.symbol}
                            </div>
                            <div className="text-xs text-gray-500">
                              Vol: {pair.volume24h.toLocaleString()}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold text-sm">
                            ${pair.price.toLocaleString()}
                          </div>
                          <div
                            className={`text-xs ${getChangeColor(pair.change24h)}`}
                          >
                            {pair.change24h >= 0 ? '+' : ''}
                            {pair.change24h.toFixed(2)}%
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
            {selectedPair && (
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <h2 className="text-2xl font-bold">
                        {selectedPair.symbol}
                      </h2>
                      <div className="text-3xl font-bold">
                        ${selectedPair.price.toLocaleString()}
                      </div>
                      <div
                        className={`flex items-center space-x-1 ${getChangeColor(selectedPair.change24h)}`}
                      >
                        {selectedPair.change24h >= 0 ? (
                          <TrendingUp className="h-5 w-5" />
                        ) : (
                          <TrendingDown className="h-5 w-5" />
                        )}
                        <span className="font-semibold">
                          {selectedPair.change24h >= 0 ? '+' : ''}
                          {selectedPair.change24h.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-6 text-sm">
                      <div>
                        <div className="text-gray-500">24h High</div>
                        <div className="font-semibold">
                          ${selectedPair.high24h.toLocaleString()}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-500">24h Low</div>
                        <div className="font-semibold">
                          ${selectedPair.low24h.toLocaleString()}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-500">24h Volume</div>
                        <div className="font-semibold">
                          {selectedPair.volume24h.toLocaleString()}
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
                    <div className="text-gray-500">TradingView Chart</div>
                    <div className="text-sm text-gray-400">
                      Advanced charting tools coming soon
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Order Book and Recent Trades */}
            <div className="grid grid-cols-2 gap-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">Order Book</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="space-y-2">
                    {/* Asks */}
                    <div className="space-y-1">
                      {orderBook.asks.reverse().map((ask, index) => (
                        <div
                          key={index}
                          className="flex justify-between text-sm px-4 py-1 hover:bg-red-50"
                        >
                          <span className="text-red-600">
                            {ask.price.toFixed(2)}
                          </span>
                          <span>{ask.quantity.toFixed(4)}</span>
                          <span className="text-gray-500">
                            {ask.total.toFixed(2)}
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Spread */}
                    <div className="px-4 py-2 bg-gray-100 text-center">
                      <span className="text-sm font-semibold">
                        Spread: $
                        {(
                          orderBook.asks[0]?.price - orderBook.bids[0]?.price
                        ).toFixed(2)}
                      </span>
                    </div>

                    {/* Bids */}
                    <div className="space-y-1">
                      {orderBook.bids.map((bid, index) => (
                        <div
                          key={index}
                          className="flex justify-between text-sm px-4 py-1 hover:bg-green-50"
                        >
                          <span className="text-green-600">
                            {bid.price.toFixed(2)}
                          </span>
                          <span>{bid.quantity.toFixed(4)}</span>
                          <span className="text-gray-500">
                            {bid.total.toFixed(2)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">Recent Trades</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="space-y-1">
                    {recentTrades.map((trade) => (
                      <div
                        key={trade.id}
                        className="flex justify-between text-sm px-4 py-2 hover:bg-gray-50"
                      >
                        <span
                          className={
                            trade.side === 'buy'
                              ? 'text-green-600'
                              : 'text-red-600'
                          }
                        >
                          {trade.price.toFixed(2)}
                        </span>
                        <span>{trade.quantity.toFixed(4)}</span>
                        <span className="text-gray-500">{trade.time}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
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
                      Buy
                    </TabsTrigger>
                    <TabsTrigger value="sell" className="text-red-600">
                      Sell
                    </TabsTrigger>
                  </TabsList>
                </Tabs>

                <Select
                  value={orderType}
                  onValueChange={(value) =>
                    setOrderType(value as 'market' | 'limit')
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="market">Market Order</SelectItem>
                    <SelectItem value="limit">Limit Order</SelectItem>
                  </SelectContent>
                </Select>

                {orderType === 'limit' && (
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

                <div>
                  <label className="block text-sm font-medium mb-1">
                    Quantity ({selectedPair?.baseAsset})
                  </label>
                  <Input
                    type="number"
                    placeholder="0.00"
                    value={orderQuantity}
                    onChange={(e) => setOrderQuantity(e.target.value)}
                  />
                </div>

                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setOrderQuantity('0.25')}
                  >
                    25%
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setOrderQuantity('0.50')}
                  >
                    50%
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setOrderQuantity('0.75')}
                  >
                    75%
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setOrderQuantity('1.00')}
                  >
                    100%
                  </Button>
                </div>

                <div className="text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>Total:</span>
                    <span>
                      {orderQuantity && orderPrice
                        ? `${(parseFloat(orderQuantity) * parseFloat(orderPrice)).toFixed(2)} USDT`
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
                    !orderQuantity || (orderType === 'limit' && !orderPrice)
                  }
                >
                  {orderSide === 'buy' ? 'Buy' : 'Sell'}{' '}
                  {selectedPair?.baseAsset}
                </Button>
              </CardContent>
            </Card>

            {/* Account Balance */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center">
                  <Wallet className="h-5 w-5 mr-2" />
                  Account Balance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">USDT</span>
                  <span className="font-semibold">12,345.67</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">BTC</span>
                  <span className="font-semibold">0.5234</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">ETH</span>
                  <span className="font-semibold">2.8901</span>
                </div>
                <Button variant="outline" className="w-full">
                  <ArrowUpDown className="h-4 w-4 mr-2" />
                  Transfer
                </Button>
              </CardContent>
            </Card>

            {/* Open Orders */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Open Orders</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {userOrders
                    .filter(
                      (order) =>
                        order.status !== 'filled' &&
                        order.status !== 'cancelled'
                    )
                    .map((order) => (
                      <div
                        key={order.id}
                        className="p-3 border-b last:border-b-0"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <Badge
                              className={
                                order.side === 'buy'
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-red-100 text-red-800'
                              }
                            >
                              {order.side.toUpperCase()}
                            </Badge>
                            <span className="text-sm font-medium">
                              {order.symbol}
                            </span>
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleCancelOrder(order.id)}
                          >
                            Cancel
                          </Button>
                        </div>
                        <div className="text-xs text-gray-600 space-y-1">
                          <div>
                            Qty: {order.quantity} / Filled: {order.filled}
                          </div>
                          {order.price && (
                            <div>Price: ${order.price.toFixed(2)}</div>
                          )}
                          <div>
                            Status:
                            <Badge
                              className={`ml-1 ${getOrderStatusColor(order.status)}`}
                            >
                              {order.status.replace('_', ' ')}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    ))}
                  {userOrders.filter(
                    (order) =>
                      order.status !== 'filled' && order.status !== 'cancelled'
                  ).length === 0 && (
                    <div className="p-4 text-center text-gray-500">
                      No open orders
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpotTradingPage;
