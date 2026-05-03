/**
 * TigerEx Frontend - Page Component
 * @file advanced-trading.tsx
 * @description React page component
 * @author TigerEx Development Team
 */

import React, { useState } from 'react';
import TradingViewChart from '../components/trading/TradingViewChart';
import AdvancedOrderForm from '../components/trading/AdvancedOrderForm';
import OrderBookDisplay from '../components/trading/OrderBookDisplay';
import MarketTradesHistory from '../components/trading/MarketTradesHistory';
import OrdersPositionsPanel from '../components/trading/OrdersPositionsPanel';
import BottomNavigation from '../components/layout/BottomNavigation';

const AdvancedTradingPage: React.FC = () => {
  const [activeBottomTab, setActiveBottomTab] = useState('trade');
  const [tradingPair] = useState('BTC/USDT');
  const [currentPrice] = useState(120442.8);

  return (
    <div className="min-h-screen bg-gray-950 text-white pb-16">
      {/* Desktop Layout */}
      <div className="hidden lg:grid lg:grid-cols-12 lg:gap-2 p-2 h-screen">
        {/* Left Panel - Order Book */}
        <div className="lg:col-span-2 bg-gray-900 rounded-lg overflow-hidden">
          <OrderBookDisplay />
        </div>

        {/* Center Panel - Chart */}
        <div className="lg:col-span-6 flex flex-col gap-2">
          <div className="flex-1 bg-gray-900 rounded-lg overflow-hidden">
            <TradingViewChart />
          </div>
          <div className="h-64 bg-gray-900 rounded-lg overflow-hidden">
            <OrdersPositionsPanel />
          </div>
        </div>

        {/* Right Panel - Order Form & Trades */}
        <div className="lg:col-span-4 flex flex-col gap-2">
          <div className="flex-1 bg-gray-900 rounded-lg overflow-hidden">
            <AdvancedOrderForm
              tradingPair={tradingPair}
              currentPrice={currentPrice}
            />
          </div>
          <div className="h-80 bg-gray-900 rounded-lg overflow-hidden">
            <MarketTradesHistory />
          </div>
        </div>
      </div>

      {/* Mobile Layout */}
      <div className="lg:hidden">
        {/* Chart Section */}
        <div className="h-96 bg-gray-900">
          <TradingViewChart />
        </div>

        {/* Order Form Section */}
        <div className="bg-gray-900 mt-2">
          <AdvancedOrderForm
            tradingPair={tradingPair}
            currentPrice={currentPrice}
          />
        </div>

        {/* Order Book & Trades Tabs */}
        <div className="mt-2 bg-gray-900">
          <div className="flex border-b border-gray-800">
            <button className="flex-1 py-3 text-center font-semibold border-b-2 border-yellow-400">
              Order Book
            </button>
            <button className="flex-1 py-3 text-center text-gray-400">
              Trades
            </button>
          </div>
          <div className="h-96">
            <OrderBookDisplay />
          </div>
        </div>

        {/* Orders & Positions */}
        <div className="mt-2 bg-gray-900">
          <OrdersPositionsPanel />
        </div>
      </div>

      {/* Bottom Navigation */}
      <BottomNavigation
        activeTab={activeBottomTab}
        onTabChange={setActiveBottomTab}
      />
    </div>
  );
};

export default AdvancedTradingPage;// TigerEx Wallet API
export const WalletAPI = { create: (auth: string) => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }) };
