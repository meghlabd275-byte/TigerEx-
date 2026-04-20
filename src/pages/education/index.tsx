/**
 * TigerEx React Component
 * @file index.tsx
 * @description React component for TigerEx
 * @author TigerEx Development Team
 */
import React, { useState } from 'react';
import { BookOpen, Play, CheckCircle, Clock, Star, Users, Search, Award, Video } from 'lucide-react';

export default function EducationPage() {
  const [search, setSearch] = useState('');

  const courses = [
    {
      id: 'crypto-101',
      title: 'Cryptocurrency Fundamentals',
      category: 'beginner',
      duration: 4,
      rating: 4.8,
      enrolled: 45000,
      lessons: 8,
      description: 'Learn the basics of cryptocurrency, blockchain technology, and digital assets'
    },
    {
      id: 'trading-101',
      title: 'Crypto Trading Basics',
      category: 'trading',
      duration: 6,
      rating: 4.9,
      enrolled: 32000,
      lessons: 12,
      description: 'Learn to trade cryptocurrencies with fundamental and technical analysis'
    },
    {
      id: 'defi-101',
      title: 'DeFi Masterclass',
      category: 'defi',
      duration: 8,
      rating: 4.7,
      enrolled: 18000,
      lessons: 16,
      description: 'Master decentralized finance: yield farming, lending, staking'
    },
    {
      id: 'security-101',
      title: 'Security Mastery',
      category: 'security',
      duration: 3,
      rating: 4.9,
      enrolled: 28000,
      lessons: 6,
      description: 'Protect your digital assets with advanced security'
    },
    {
      id: 'nft-101',
      title: 'NFT Essentials',
      category: 'nft',
      duration: 4,
      rating: 4.6,
      enrolled: 22000,
      lessons: 8,
      description: 'Learn about Non-Fungible Tokens: creation, trading, investment'
    },
    {
      id: 'advanced-trading',
      title: 'Advanced Trading Strategies',
      category: 'advanced',
      duration: 10,
      rating: 4.8,
      enrolled: 12000,
      lessons: 20,
      description: 'Master advanced techniques: derivatives, margin, algorithmic'
    }
  ];

  const categories = [
    { id: 'beginner', name: 'Beginner', color: 'bg-green-500/20 text-green-400' },
    { id: 'trading', name: 'Trading', color: 'bg-blue-500/20 text-blue-400' },
    { id: 'defi', name: 'DeFi', color: 'bg-purple-500/20 text-purple-400' },
    { id: 'security', name: 'Security', color: 'bg-red-500/20 text-red-400' },
    { id: 'nft', name: 'NFT', color: 'bg-orange-500/20 text-orange-400' },
    { id: 'advanced', name: 'Advanced', color: 'bg-yellow-500/20 text-yellow-400' }
  ];

  const getCategoryStyle = (cat: string) => {
    const c = categories.find(c => c.id === cat);
    return c ? c.color : 'bg-gray-500/20 text-gray-400';
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="bg-gradient-to-r from-yellow-600 to-orange-600 py-16">
        <div className="max-w-7xl mx-auto px-6">
          <h1 className="text-4xl font-bold flex items-center gap-3">
            <BookOpen className="w-10 h-10" />
            TigerEx Academy
          </h1>
          <p className="text-xl text-yellow-100 mt-3">Master cryptocurrency trading with comprehensive courses</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex gap-4 mb-8">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search courses..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800 p-6 rounded-xl">
            <BookOpen className="w-8 h-8 text-yellow-500 mb-2" />
            <p className="text-2xl font-bold">{courses.length}</p>
            <p className="text-gray-400">Courses</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <Users className="w-8 h-8 text-green-500 mb-2" />
            <p className="text-2xl font-bold">180K+</p>
            <p className="text-gray-400">Students</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <Award className="w-8 h-8 text-purple-500 mb-2" />
            <p className="text-2xl font-bold">4.8</p>
            <p className="text-gray-400">Avg Rating</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <Video className="w-8 h-8 text-blue-500 mb-2" />
            <p className="text-2xl font-bold">70+</p>
            <p className="text-gray-400">Hours Content</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <div key={course.id} className="bg-gray-800 rounded-xl overflow-hidden hover:ring-2 hover:ring-yellow-500 transition-all">
              <div className="h-32 bg-gradient-to-br from-yellow-600 to-orange-600 flex items-center justify-center">
                <BookOpen className="w-16 h-16 text-white/50" />
              </div>
              <div className="p-6">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-1 rounded text-xs ${getCategoryStyle(course.category)}`}>
                    {course.category}
                  </span>
                </div>
                <h3 className="text-xl font-bold mb-2">{course.title}</h3>
                <p className="text-gray-400 text-sm mb-4 line-clamp-2">{course.description}</p>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Star className="w-4 h-4 text-yellow-500" />
                    <span>{course.rating}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <span>{course.duration}h</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-gray-400" />
                    <span>{(course.enrolled / 1000).toFixed(0)}K</span>
                  </div>
                </div>
                <div className="mt-4 flex items-center gap-2 text-sm text-green-400">
                  <CheckCircle className="w-4 h-4" />
                  <span>{course.lessons} Lessons + Quiz</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}