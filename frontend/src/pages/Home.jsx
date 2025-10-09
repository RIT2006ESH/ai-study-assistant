import React from 'react'
import { Link } from 'react-router-dom'

const Home = () => {
  const features = [
    {
      title: 'AI Chat Assistant',
      description: 'Get instant answers and explanations for any topic',
      icon: '🤖',
      link: '/study',
      color: 'bg-blue-500'
    },
    {
      title: 'Document Library',
      description: 'Upload PDFs, docs and get AI-powered summaries',
      icon: '📑',
      link: '/library',
      color: 'bg-green-500'
    },
    {
      title: 'Practice Problems',
      description: 'Solve math, science problems with step-by-step help',
      icon: '🧩',
      link: '/practice',
      color: 'bg-purple-500'
    },
    {
      title: 'Progress Analytics',
      description: 'Track your learning journey and identify weak areas',
      icon: '📈',
      link: '/analytics',
      color: 'bg-orange-500'
    }
  ]

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-800 mb-4">
          Welcome to AI Study Assistant 🎓
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Transform your learning experience with AI-powered tools designed to help you study smarter, not harder
        </p>
      </header>
      
      <div className="grid md:grid-cols-2 gap-8 mb-12">
        {features.map((feature, index) => (
          <Link
            key={index}
            to={feature.link}
            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 overflow-hidden"
          >
            <div className={`${feature.color} h-2`}></div>
            <div className="p-8">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-2xl font-bold text-gray-800 mb-3 group-hover:text-blue-600 transition-colors">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-lg leading-relaxed">
                {feature.description}
              </p>
              <div className="mt-4 text-blue-500 font-semibold group-hover:text-blue-700">
                Get Started →
              </div>
            </div>
          </Link>
        ))}
      </div>

      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl text-white p-8 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to boost your learning?</h2>
        <p className="text-xl mb-6">Join thousands of students already using AI to excel in their studies</p>
        <Link
          to="/study"
          className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-block"
        >
          Start Learning Now
        </Link>
      </div>
    </div>
  )
}

export default Home