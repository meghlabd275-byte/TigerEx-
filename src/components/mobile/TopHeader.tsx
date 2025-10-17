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

import React from 'react';
import { ArrowLeft, QrCode, Headphones, MoreHorizontal } from 'lucide-react';

interface TopHeaderProps {
  title?: string;
  showBackButton?: boolean;
  onBack?: () => void;
  rightActions?: React.ReactNode;
}

const TopHeader: React.FC<TopHeaderProps> = ({
  title,
  showBackButton = false,
  onBack,
  rightActions
}) => {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-50">
      {/* Left Side */}
      <div className="flex items-center">
        {showBackButton && (
          <button
            onClick={onBack}
            className="p-2 -ml-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-700" />
          </button>
        )}
        {title && (
          <h1 className="text-lg font-semibold text-gray-900 ml-2">
            {title}
          </h1>
        )}
      </div>

      {/* Right Side */}
      <div className="flex items-center space-x-2">
        {rightActions || (
          <>
            <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
              <QrCode className="w-5 h-5 text-gray-700" />
            </button>
            <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
              <Headphones className="w-5 h-5 text-gray-700" />
            </button>
            <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
              <MoreHorizontal className="w-5 h-5 text-gray-700" />
            </button>
          </>
        )}
      </div>
    </header>
  );
};

export default TopHeader;