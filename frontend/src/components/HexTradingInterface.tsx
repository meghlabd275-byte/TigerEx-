import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  TrendingUp, 
  TrendingDown, 
  ArrowUpDown, 
  Zap, 
  Shield, 
  DollarSign,
  Clock,
  Activity,
  BarChart3,
  Settings
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

interface PriceQuote {
  cex: {
    price: number;
    liquidity: number;
    fees: number;
    executionTime: number;
  };
  dex: {
    price: number;
    liquidity: number;
    fees: number;
    executionTime: number;
    gasCost: number;
  };
  bestPrice: number;
  bestVenue: 'cex' | 'dex';
  savings: number;
}

interface Trade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit';
  quantity: number;
  price: number;
  status: 'pending' | 'filled' | 'cancelled';
  venue: 'cex' | 'dex' | 'hybrid';
  timestamp: string;
  fees: number;
}

const HexTradingInterface: React.FC = () => {
  const [selectedPair, setSelectedPair] = useState<TradingPair>({
    symbol: 'BTC/USDT',
    baseAsset: 'BTC',
    quoteAsset: 'USDT',
    price: 50000,
    change24h: 2.5,
    volume24h: 1250000000,
    high24h: 51200,
    low24h: 48800
  });

  const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [quantity, setQuantity] = useState<string>('');
  const [price, setPrice] = useState<string>('');
  const [hexMode, setHexMode] = useState<boolean>(true);
  const [venue, setVenue] = useState<'cex' | 'dex' | 'hybrid'>('hybrid');
  const [slippage, setSlippage] = useState<number>(0.5);
  
  const [priceQuote, setPriceQuote] = useState<PriceQuote | null>(null);
  const [orderBook, setOrderBook] = useState<{
    bids: OrderBookEntry[];
    asks: OrderBookEntry[];
  }>({
    bids: [
      { price: 49950, quantity: 1.5, total: 74925 },
      { price: 49900, quantity: 2.0, total: 99800 },
      { price: 49850, quantity: 1.2, total: 59820 }
    ],
    asks: [
      { price: 50050, quantity: 1.8, total: 90090 },
      { price: 50100, quantity: 2.2, total: 110220 },
      { price: 50150, quantity: 1.0, total: 50150 }
    ]
  });

  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Fetch price quotes from both CEX and DEX
  const fetchPriceQuote = useCallback(async () => {
    if (!quantity || parseFloat(quantity) <= 0) return;

    try {
      const response = await fetch(`/api/v1/price/${selectedPair.symbol}?side=${side}&quantity=${quantity}`);
      const data = await response.json();
      
      if (data.success) {
        setPriceQuote(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch price quote:', error);
    }
  }, [selectedPair.symbol, side, quantity]);

  // Execute trade
  const executeTrade = async () => {
    if (!quantity || parseFloat(quantity) <= 0) return;

    setIsLoading(true);
    try {
      const tradeRequest = {
        user_id: 'user123', // Replace with actual user ID
        symbol: selectedPair.symbol,
        side,
        order_type: orderType,
        quantity: parseFloat(quantity),
        price: orderType === 'limit' ? parseFloat(price) : undefined,
        exchange_type: venue,
        slippage_tolerance: slippage
      };

      const response = await fetch('/api/v1/trade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tradeRequest)
      });

      const data = await response.json();
      
      if (data.success) {
        // Add to recent trades
        const newTrade: Trade = {
          id: data.data.order_id,
          symbol: selectedPair.symbol,
          side,
          type: orderType,
          quantity: parseFloat(quantity),
          price: data.data.price,
          status: data.data.status,
          venue: data.data.exchange,
          timestamp: new Date().toISOString(),
          fees: data.data.fees
        };
        
        setRecentTrades(prev => [newTrade, ...prev.slice(0, 9)]);
        
        // Reset form
        setQuantity('');
        setPrice('');
      }
    } catch (error) {
      console.error('Trade execution failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Update price quotes when parameters change
  useEffect(() => {
    const timer = setTimeout(fetchPriceQuote, 500);
    return () => clearTimeout(timer);
  }, [fetchPriceQuote]);

  // Real-time price updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/prices');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data[selectedPair.symbol]) {
        setSelectedPair(prev => ({
          ...prev,
          price: data[selectedPair.symbol].price,
          change24h: data[selectedPair.symbol].change
        }));
      }
    };

    return () => ws.close();
  }, [selectedPair.symbol]);

  const formatCurrency = (value: number, decimals: number = 2) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  };

  const formatNumber = (value: number, decimals: number = 8) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              TigerEx Hex Trading
            </h1>
            <Badge variant={hexMode ? "default" : "secondary"} className="flex items-center space-x-1">
              <Zap className="w-3 h-3" />
              <span>{hexMode ? 'CEX+DEX' : 'CEX Only'}</span>
            </Badge>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Hex Mode</span>
              <Switch checked={hexMode} onCheckedChange={setHexMode} />
            </div>
            <Button variant="outline" size="sm">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>

        {/* Price Header */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {selectedPair.symbol}
                  </h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {selectedPair.baseAsset} / {selectedPair.quoteAsset}
                  </p>
                </div>
                
                <div>
                  <div className="text-3xl font-bold text-gray-900 dark:text-white">
                    {formatCurrency(selectedPair.price)}
                  </div>
                  <div className={`flex items-center space-x-1 ${
                    selectedPair.change24h >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {selectedPair.change24h >= 0 ? (
                      <TrendingUp className="w-4 h-4" />
                    ) : (
                      <TrendingDown className="w-4 h-4" />
                    )}
                    <span>{selectedPair.change24h >= 0 ? '+' : ''}{selectedPair.change24h.toFixed(2)}%</span>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-6 text-right">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">24h High</p>
                  <p className="font-semibold">{formatCurrency(selectedPair.high24h)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">24h Low</p>
                  <p className="font-semibold">{formatCurrency(selectedPair.low24h)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">24h Volume</p>
                  <p className="font-semibold">{formatCurrency(selectedPair.volume24h, 0)}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Trading Panel */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <ArrowUpDown className="w-5 h-5" />
                  <span>Place Order</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                
                {/* Order Type Tabs */}
                <Tabs value={orderType} onValueChange={(value) => setOrderType(value as 'market' | 'limit')}>
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="market">Market</TabsTrigger>
                    <TabsTrigger value="limit">Limit</TabsTrigger>
                  </TabsList>
                </Tabs>

                {/* Buy/Sell Toggle */}
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    variant={side === 'buy' ? 'default' : 'outline'}
                    className={side === 'buy' ? 'bg-green-600 hover:bg-green-700' : ''}
                    onClick={() => setSide('buy')}
                  >
                    Buy
                  </Button>
                  <Button
                    variant={side === 'sell' ? 'default' : 'outline'}
                    className={side === 'sell' ? 'bg-red-600 hover:bg-red-700' : ''}
                    onClick={() => setSide('sell')}
                  >
                    Sell
                  </Button>
                </div>

                {/* Venue Selection (Hex Mode) */}
                {hexMode && (
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Execution Venue
                    </label>
                    <Select value={venue} onValueChange={(value) => setVenue(value as 'cex' | 'dex' | 'hybrid')}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hybrid">
                          <div className="flex items-center space-x-2">
                            <Zap className="w-4 h-4" />
                            <span>Best Price (Hybrid)</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="cex">
                          <div className="flex items-center space-x-2">
                            <Activity className="w-4 h-4" />
                            <span>CEX Only</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="dex">
                          <div className="flex items-center space-x-2">
                            <Shield className="w-4 h-4" />
                            <span>DEX Only</span>
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* Price Input (Limit Orders) */}
                {orderType === 'limit' && (
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Price ({selectedPair.quoteAsset})
                    </label>
                    <Input
                      type="number"
                      placeholder="0.00"
                      value={price}
                      onChange={(e) => setPrice(e.target.value)}
                    />
                  </div>
                )}

                {/* Quantity Input */}
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Quantity ({selectedPair.baseAsset})
                  </label>
                  <Input
                    type="number"
                    placeholder="0.00"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                  />
                </div>

                {/* Slippage Tolerance */}
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Slippage Tolerance (%)
                  </label>
                  <Select value={slippage.toString()} onValueChange={(value) => setSlippage(parseFloat(value))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0.1">0.1%</SelectItem>
                      <SelectItem value="0.5">0.5%</SelectItem>
                      <SelectItem value="1.0">1.0%</SelectItem>
                      <SelectItem value="3.0">3.0%</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Price Quote Display */}
                {priceQuote && hexMode && (
                  <Alert>
                    <DollarSign className="h-4 w-4" />
                    <AlertDescription>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>CEX Price:</span>
                          <span>{formatCurrency(priceQuote.cex.price)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>DEX Price:</span>
                          <span>{formatCurrency(priceQuote.dex.price)}</span>
                        </div>
                        <div className="flex justify-between font-semibold text-green-600">
                          <span>Best Price:</span>
                          <span>{formatCurrency(priceQuote.bestPrice)} ({priceQuote.bestVenue.toUpperCase()})</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Savings:</span>
                          <span>{formatCurrency(priceQuote.savings)}</span>
                        </div>
                      </div>
                    </AlertDescription>
                  </Alert>
                )}

                {/* Total */}
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Total</span>
                    <span className="font-semibold">
                      {quantity && (orderType === 'market' ? selectedPair.price : parseFloat(price || '0')) 
                        ? formatCurrency(parseFloat(quantity || '0') * (orderType === 'market' ? selectedPair.price : parseFloat(price || '0')))
                        : formatCurrency(0)
                      }
                    </span>
                  </div>
                </div>

                {/* Execute Button */}
                <Button
                  className={`w-full ${
                    side === 'buy' 
                      ? 'bg-green-600 hover:bg-green-700' 
                      : 'bg-red-600 hover:bg-red-700'
                  }`}
                  onClick={executeTrade}
                  disabled={isLoading || !quantity || parseFloat(quantity) <= 0}
                >
                  {isLoading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Processing...</span>
                    </div>
                  ) : (
                    `${side === 'buy' ? 'Buy' : 'Sell'} ${selectedPair.baseAsset}`
                  )}
                </Button>

              </CardContent>
            </Card>
          </div>

          {/* Order Book */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5" />
                  <span>Order Book</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  
                  {/* Asks */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                      Asks (Sell Orders)
                    </h4>
                    <div className="space-y-1">
                      {orderBook.asks.slice().reverse().map((ask, index) => (
                        <div key={index} className="flex justify-between text-sm">
                          <span className="text-red-600">{formatNumber(ask.price, 2)}</span>
                          <span className="text-gray-600">{formatNumber(ask.quantity, 4)}</span>
                          <span className="text-gray-500">{formatNumber(ask.total, 2)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Current Price */}
                  <div className="py-2 border-t border-b border-gray-200 dark:border-gray-700">
                    <div className="text-center">
                      <span className="text-lg font-bold text-gray-900 dark:text-white">
                        {formatCurrency(selectedPair.price)}
                      </span>
                    </div>
                  </div>

                  {/* Bids */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                      Bids (Buy Orders)
                    </h4>
                    <div className="space-y-1">
                      {orderBook.bids.map((bid, index) => (
                        <div key={index} className="flex justify-between text-sm">
                          <span className="text-green-600">{formatNumber(bid.price, 2)}</span>
                          <span className="text-gray-600">{formatNumber(bid.quantity, 4)}</span>
                          <span className="text-gray-500">{formatNumber(bid.total, 2)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Trades */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="w-5 h-5" />
                  <span>Recent Trades</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {recentTrades.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">No recent trades</p>
                  ) : (
                    recentTrades.map((trade) => (
                      <div key={trade.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Badge variant={trade.side === 'buy' ? 'default' : 'destructive'}>
                            {trade.side.toUpperCase()}
                          </Badge>
                          <div>
                            <p className="font-medium">{trade.symbol}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {formatNumber(trade.quantity, 4)} @ {formatCurrency(trade.price)}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant={
                            trade.status === 'filled' ? 'default' :
                            trade.status === 'pending' ? 'secondary' : 'destructive'
                          }>
                            {trade.status}
                          </Badge>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            {trade.venue.toUpperCase()}
                          </p>
                        </div>
                      </div>
                    ))
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

export default HexTradingInterface;