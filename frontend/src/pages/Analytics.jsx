import React, { useState } from 'react'

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('week')
  
  // Mock data - in real app this would come from API
  const stats = {
    studySessions: 24,
    problemsSolved: 156,
    averageScore: 87,
    totalStudyTime: '42h 30m',
    streak: 7,
    documentsRead: 12
  }

  const subjectProgress = [
    { subject: 'Mathematics', progress: 85, color: 'bg-blue-500' },
    { subject: 'Physics', progress: 72, color: 'bg-purple-500' },
    { subject: 'Chemistry', progress: 91, color: 'bg-green-500' },
    { subject: 'Biology', progress: 68, color: 'bg-orange-500' }
  ]

  const recentActivity = [
    { date: '2024-01-15', activity: 'Completed Calculus Quiz', score: '92%', type: 'quiz' },
    { date: '2024-01-14', activity: 'Studied Organic Chemistry', duration: '2h 15m', type: 'study' },
    { date: '2024-01-14', activity: 'Solved 15 Physics Problems', score: '87%', type: 'practice' },
    { date: '2024-01-13', activity: 'Read Chapter 5: Thermodynamics', duration: '1h 45m', type: 'reading' }
  ]

  const getActivityIcon = (type) => {
    switch(type) {
      case 'quiz': return '📋'
      case 'study': return '📚'
      case 'practice': return '🧠'
      case 'reading': return '📖'
      default: return '📊'
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Learning Analytics 📊</h1>
        <p className="text-gray-600">Track your progress and identify areas for improvement</p>
      </div>

      {/* Time Range Selector */}
      <div className="mb-8">
        <div className="flex space-x-2">
          {['week', 'month', 'semester'].map(range => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                timeRange === range
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {range.charAt(0).toUpperCase() + range.slice(1)}
            </button>
          ))}
        </div>
      </div>
      
      {/* Stats Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-lg text-center">
          <div className="text-3xl mb-2">📚</div>
          <h3 className="text-2xl font-bold text-blue-600">{stats.studySessions}</h3>
          <p className="text-gray-600">Study Sessions</p>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-lg text-center">
          <div className="text-3xl mb-2">🧠</div>
          <h3 className="text-2xl font-bold text-green-600">{stats.problemsSolved}</h3>
          <p className="text-gray-600">Problems Solved</p>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-lg text-center">
          <div className="text-3xl mb-2">🎯</div>
          <h3 className="text-2xl font-bold text-purple-600">{stats.averageScore}%</h3>
          <p className="text-gray-600">Average Score</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg text-center">
          <div className="text-3xl mb-2">⏱️</div>
          <h3 className="text-2xl font-bold text-orange-600">{stats.totalStudyTime}</h3>
          <p className="text-gray-600">Study Time</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg text-center">
          <div className="text-3xl mb-2">🔥</div>
          <h3 className="text-2xl font-bold text-red-600">{stats.streak}</h3>
          <p className="text-gray-600">Day Streak</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg text-center">
          <div className="text-3xl mb-2">📄</div>
          <h3 className="text-2xl font-bold text-indigo-600">{stats.documentsRead}</h3>
          <p className="text-gray-600">Documents Read</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8 mb-8">
        {/* Subject Progress */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-6">Subject Progress</h2>
          <div className="space-y-4">
            {subjectProgress.map((subject, index) => (
              <div key={index}>
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-gray-700">{subject.subject}</span>
                  <span className="text-sm text-gray-500">{subject.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`${subject.color} h-3 rounded-full transition-all duration-500`}
                    style={{ width: `${subject.progress}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Weekly Performance Chart */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-6">Weekly Performance</h2>
          <div className="h-48 flex items-end justify-between space-x-2">
            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => {
              const height = Math.random() * 80 + 20 // Mock data
              return (
                <div key={day} className="flex flex-col items-center flex-1">
                  <div
                    className="bg-blue-500 rounded-t w-full transition-all duration-500 hover:bg-blue-600"
                    style={{ height: `${height}%` }}
                  ></div>
                  <span className="text-xs text-gray-600 mt-2">{day}</span>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-6">Recent Activity</h2>
        <div className="space-y-4">
          {recentActivity.map((activity, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <div className="flex items-center space-x-4">
                <div className="text-2xl">{getActivityIcon(activity.type)}</div>
                <div>
                  <h3 className="font-medium text-gray-800">{activity.activity}</h3>
                  <p className="text-sm text-gray-500">{activity.date}</p>
                </div>
              </div>
              <div className="text-right">
                {activity.score && (
                  <span className="text-green-600 font-semibold">{activity.score}</span>
                )}
                {activity.duration && (
                  <span className="text-blue-600 font-semibold">{activity.duration}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Insights */}
      <div className="mt-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl text-white p-8">
        <h2 className="text-2xl font-bold mb-4">AI Insights 🤖</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold mb-2">📈 Strengths</h3>
            <ul className="text-sm space-y-1">
              <li>• Excellent performance in Chemistry (91%)</li>
              <li>• Consistent 7-day study streak</li>
              <li>• Strong problem-solving skills</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">🎯 Areas to Improve</h3>
            <ul className="text-sm space-y-1">
              <li>• Focus more on Biology concepts</li>
              <li>• Increase Physics practice time</li>
              <li>• Review thermodynamics fundamentals</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics