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

import React, { useState } from 'react';
import { TrendingUp, Users, MessageCircle, Share2, Bookmark } from 'lucide-react';

interface Post {
  id: string;
  author: string;
  authorAvatar: string;
  time: string;
  content: string;
  likes: number;
  comments: number;
  shares: number;
  trending?: boolean;
}

const DiscoverFeed: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'discover' | 'following' | 'campaign' | 'news' | 'announcements' | 'hot'>('discover');

  const tabs = [
    { id: 'discover', label: 'Discover' },
    { id: 'following', label: 'Following' },
    { id: 'campaign', label: 'Campaign', badge: true },
    { id: 'news', label: 'News' },
    { id: 'announcements', label: 'Announcements' },
    { id: 'hot', label: 'Hot' },
  ];

  const posts: Post[] = [
    {
      id: '1',
      author: 'Trend user',
      authorAvatar: '👤',
      time: '1h',
      content: 'Market analysis: BTC showing strong support at $120k level. Expecting bullish momentum to continue...',
      likes: 234,
      comments: 45,
      shares: 12,
      trending: true,
    },
  ];

  return (
    <div className="bg-white dark:bg-gray-900 min-h-screen">
      {/* Tabs Navigation */}
      <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 z-10">
        <div className="flex overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`relative px-4 py-3 whitespace-nowrap font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-gray-900 dark:text-white border-b-2 border-yellow-400'
                  : 'text-gray-500 dark:text-gray-400'
              }`}
            >
              {tab.label}
              {tab.badge && (
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-yellow-400 rounded-full"></span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Feed Content */}
      <div className="max-w-2xl mx-auto">
        {posts.map((post) => (
          <div
            key={post.id}
            className="border-b border-gray-200 dark:border-gray-800 p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50"
          >
            {/* Post Header */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-xl">
                  {post.authorAvatar}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900 dark:text-white">
                      {post.author}
                    </span>
                    {post.trending && (
                      <span className="flex items-center gap-1 text-xs bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 px-2 py-0.5 rounded-full">
                        <TrendingUp className="w-3 h-3" />
                        Trending
                      </span>
                    )}
                  </div>
                  <span className="text-sm text-gray-500 dark:text-gray-400">{post.time}</span>
                </div>
              </div>
              <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                </svg>
              </button>
            </div>

            {/* Post Content */}
            <p className="text-gray-900 dark:text-white mb-4">{post.content}</p>

            {/* Post Actions */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <button className="flex items-center gap-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                  <MessageCircle className="w-5 h-5" />
                  <span className="text-sm">{post.comments}</span>
                </button>
                <button className="flex items-center gap-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                  <Share2 className="w-5 h-5" />
                  <span className="text-sm">{post.shares}</span>
                </button>
              </div>
              <button className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                <Bookmark className="w-5 h-5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DiscoverFeed;