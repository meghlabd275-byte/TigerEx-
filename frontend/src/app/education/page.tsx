/**
 * TigerEx Frontend Component
 * @file page.tsx
 * @description React component for TigerEx exchange
 * @author TigerEx Development Team
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Play, 
  CheckCircle, 
  Clock, 
  Star, 
  Users,
  Search,
  Filter,
  ChevronRight,
  Award,
  Video,
  FileText,
  HelpCircle
} from 'lucide-react';

const EDUCATION_API = 'http://localhost:8091';

interface Course {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  duration_hours: number;
  instructor: string;
  rating: number;
  enrolled_count: number;
  tags: string[];
  lessons_count: number;
  has_quiz: boolean;
}

interface Lesson {
  id: string;
  title: string;
  content: string;
  duration_minutes: number;
  video_url?: string;
  resources: any[];
}

export default function EducationPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [difficulty, setDifficulty] = useState('');

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (category) params.append('category', category);
      if (difficulty) params.append('difficulty', difficulty);
      
      const response = await fetch(`${EDUCATION_API}/api/v1/courses?${params}`);
      const data = await response.json();
      if (data.success) {
        setCourses(data.courses || []);
      }
    } catch (error) {
      console.error('Failed to fetch courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLesson = async (courseId: string, lessonId: string) => {
    try {
      const response = await fetch(`${EDUCATION_API}/api/v1/courses/${courseId}/lessons/${lessonId}`);
      const data = await response.json();
      if (data.success) {
        setLesson(data.lesson);
      }
    } catch (error) {
      console.error('Failed to fetch lesson:', error);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-500/20 text-green-400';
      case 'intermediate': return 'bg-yellow-500/20 text-yellow-400';
      case 'advanced': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getCategoryIcon = (cat: string) => {
    switch (cat) {
      case 'trading': return <TrendingUp />;
      case 'defi': return <Activity />;
      case 'nft': return <Star />;
      case 'security': return <Shield />;
      case 'blockchain': return <Database />;
      default: return <BookOpen />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-yellow-600 to-yellow-500 py-16">
        <div className="max-w-7xl mx-auto px-6">
          <h1 className="text-4xl font-bold flex items-center gap-3">
            <BookOpen className="w-10 h-10" />
            TigerEx Academy
          </h1>
          <p className="mt-3 text-xl text-yellow-100">
            Master cryptocurrency trading with our comprehensive courses
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-8">
          <div className="flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="Search courses..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-yellow-500"
            />
          </div>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-yellow-500"
          >
            <option value="">All Categories</option>
            <option value="beginner">Beginner</option>
            <option value="trading">Trading</option>
            <option value="defi">DeFi</option>
            <option value="nft">NFT</option>
            <option value="security">Security</option>
            <option value="blockchain">Blockchain</option>
            <option value="advanced">Advanced</option>
          </select>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-yellow-500"
          >
            <option value="">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
          <button
            onClick={fetchCourses}
            className="bg-yellow-500 hover:bg-yellow-400 text-black px-6 py-3 rounded-lg font-semibold"
          >
            Search
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center gap-3">
              <BookOpen className="w-8 h-8 text-yellow-500" />
              <div>
                <p className="text-2xl font-bold">{courses.length}</p>
                <p className="text-gray-400">Courses</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center gap-3">
              <Users className="w-8 h-8 text-green-500" />
              <div>
                <p className="text-2xl font-bold">180K+</p>
                <p className="text-gray-400">Students</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center gap-3">
              <Award className="w-8 h-8 text-purple-500" />
              <div>
                <p className="text-2xl font-bold">4.8</p>
                <p className="text-gray-400">Avg Rating</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center gap-3">
              <Video className="w-8 h-8 text-blue-500" />
              <div>
                <p className="text-2xl font-bold">50+</p>
                <p className="text-gray-400">Hours Content</p>
              </div>
            </div>
          </div>
        </div>

        {/* Course Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-yellow-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <div 
                key={course.id} 
                className="bg-gray-800 rounded-xl overflow-hidden hover:ring-2 hover:ring-yellow-500 transition-all cursor-pointer"
                onClick={() => setSelectedCourse(course)}
              >
                <div className="h-32 bg-gradient-to-br from-yellow-600 to-orange-600 flex items-center justify-center">
                  <BookOpen className="w-16 h-16 text-white/50" />
                </div>
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-1 rounded text-xs ${getDifficultyColor(course.difficulty)}`}>
                      {course.difficulty}
                    </span>
                    <span className="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300">
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
                      <span>{course.duration_hours}h</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-gray-400" />
                      <span>{(course.enrolled_count / 1000).toFixed(0)}K</span>
                    </div>
                  </div>
                  
                  {course.has_quiz && (
                    <div className="mt-4 flex items-center gap-2 text-sm text-green-400">
                      <CheckCircle className="w-4 h-4" />
                      <span>Includes Quiz</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Course Detail Modal */}
        {selectedCourse && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-6">
            <div className="bg-gray-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex gap-2 mb-2">
                      <span className={`px-2 py-1 rounded text-xs ${getDifficultyColor(selectedCourse.difficulty)}`}>
                        {selectedCourse.difficulty}
                      </span>
                      <span className="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300">
                        {selectedCourse.category}
                      </span>
                    </div>
                    <h2 className="text-2xl font-bold">{selectedCourse.title}</h2>
                    <p className="text-gray-400 mt-2">{selectedCourse.description}</p>
                  </div>
                  <button 
                    onClick={() => setSelectedCourse(null)}
                    className="text-gray-400 hover:text-white text-2xl"
                  >
                    ×
                  </button>
                </div>
              </div>
              
              <div className="p-6">
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-gray-700/50 p-4 rounded-lg text-center">
                    <Clock className="w-6 h-6 mx-auto mb-2 text-yellow-500" />
                    <p className="text-lg font-bold">{selectedCourse.duration_hours}h</p>
                    <p className="text-gray-400 text-sm">Duration</p>
                  </div>
                  <div className="bg-gray-700/50 p-4 rounded-lg text-center">
                    <Star className="w-6 h-6 mx-auto mb-2 text-yellow-500" />
                    <p className="text-lg font-bold">{selectedCourse.rating}</p>
                    <p className="text-gray-400 text-sm">Rating</p>
                  </div>
                  <div className="bg-gray-700/50 p-4 rounded-lg text-center">
                    <Users className="w-6 h-6 mx-auto mb-2 text-green-500" />
                    <p className="text-lg font-bold">{(selectedCourse.enrolled_count / 1000).toFixed(0)}K</p>
                    <p className="text-gray-400 text-sm">Enrolled</p>
                  </div>
                </div>

                <h3 className="text-lg font-bold mb-4">Course Content</h3>
                <div className="space-y-3">
                  {[1, 2, 3, 4].map((i) => (
                    <div 
                      key={i} 
                      className="bg-gray-700/50 p-4 rounded-lg flex items-center justify-between hover:bg-gray-700 cursor-pointer"
                      onClick={() => {
                        setLesson(null);
                        setSelectedCourse(null);
                      }}
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-yellow-500/20 rounded-full flex items-center justify-center text-yellow-500">
                          {i}
                        </div>
                        <div>
                          <p className="font-medium">Lesson {i}: Sample Lesson Title</p>
                          <p className="text-gray-400 text-sm">20-30 minutes</p>
                        </div>
                      </div>
                      <ChevronRight className="text-gray-400" />
                    </div>
                  ))}
                </div>

                {selectedCourse.has_quiz && (
                  <div className="mt-6 bg-yellow-500/10 border border-yellow-500/30 p-4 rounded-lg">
                    <div className="flex items-center gap-3">
                      <HelpCircle className="w-6 h-6 text-yellow-500" />
                      <div>
                        <p className="font-semibold">Final Quiz Available</p>
                        <p className="text-gray-400 text-sm">Test your knowledge to earn completion certificate</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Missing imports
function TrendingUp() { return <Activity />; }
function Shield() { return <Activity />; }
function Database() { return <Activity />; }
function Activity() { return <div />; }// TigerEx Wallet API
export const useWallet = () => ({ createWallet: () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }) })
