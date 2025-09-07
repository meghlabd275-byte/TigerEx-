import React from 'react';

interface TradingChartProps {
  pair: string;
}

const TradingChart: React.FC<TradingChartProps> = ({ pair }) => {
  return (
    <div className="w-full h-full flex items-center justify-center bg-gray-900 rounded-lg">
      <div className="text-center">
        <div className="text-white text-lg font-medium mb-2">
          {pair} Trading Chart
        </div>
        <div className="text-gray-400 text-sm">
          Chart integration coming soon
        </div>
        <div className="mt-4 text-gray-500 text-xs">
          TradingView or custom chart component will be integrated here
        </div>
      </div>
    </div>
  );
};

export default TradingChart;
