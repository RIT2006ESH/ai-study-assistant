import React, { useState } from 'react'

const Practice = () => {
  const [selectedSubject, setSelectedSubject] = useState(null)
  const [currentProblem, setCurrentProblem] = useState(null)
  const [userAnswer, setUserAnswer] = useState('')
  const [showSolution, setShowSolution] = useState(false)

  const subjects = [
    {
      id: 'math',
      name: 'Mathematics',
      icon: '🔢',
      color: 'bg-blue-500',
      topics: ['Algebra', 'Calculus', 'Geometry', 'Statistics'],
      problems: [
        {
          question: 'Solve for x: 2x + 5 = 13',
          answer: 'x = 4',
          solution: 'Subtract 5 from both sides: 2x = 8\nDivide by 2: x = 4'
        }
      ]
    },
    {
      id: 'physics',
      name: 'Physics',
      icon: '⚛️',
      color: 'bg-purple-500',
      topics: ['Mechanics', 'Thermodynamics', 'Electromagnetism', 'Optics'],
      problems: [
        {
          question: 'A ball is thrown upward with initial velocity 20 m/s. What is its maximum height?',
          answer: '20.4 m',
          solution: 'Using v² = u² + 2as\nAt max height, v = 0\n0 = 20² + 2(-9.8)h\nh = 400/(2×9.8) = 20.4 m'
        }
      ]
    },
    {
      id: 'chemistry',
      name: 'Chemistry',
      icon: '⚗️',
      color: 'bg-green-500',
      topics: ['Organic', 'Inorganic', 'Physical', 'Analytical'],
      problems: [
        {
          question: 'Balance the equation: H₂ + O₂ → H₂O',
          answer: '2H₂ + O₂ → 2H₂O',
          solution: 'Count atoms on each side:\nLeft: 2H, 2O\nRight: 2H, 1O\nAdd coefficient 2 to H₂O: 2H₂ + O₂ → 2H₂O'
        }
      ]
    },
    {
      id: 'biology',
      name: 'Biology',
      icon: '🧬',
      color: 'bg-orange-500',
      topics: ['Cell Biology', 'Genetics', 'Evolution', 'Ecology'],
      problems: [
        {
          question: 'What is the powerhouse of the cell?',
          answer: 'Mitochondria',
          solution: 'Mitochondria are called the powerhouse of the cell because they produce ATP (energy) through cellular respiration.'
        }
      ]
    }
  ]

  const startPractice = (subject) => {
    setSelectedSubject(subject)
    setCurrentProblem(subject.problems[0])
    setUserAnswer('')
    setShowSolution(false)
  }

  const checkAnswer = () => {
    setShowSolution(true)
  }

  const nextProblem = () => {
    // In a real app, you'd fetch the next problem
    setUserAnswer('')
    setShowSolution(false)
  }

  if (selectedSubject && currentProblem) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="mb-6">
          <button
            onClick={() => setSelectedSubject(null)}
            className="text-blue-500 hover:text-blue-700 mb-4"
          >
            ← Back to Subjects
          </button>
          <h1 className="text-3xl font-bold text-gray-800">
            {selectedSubject.icon} {selectedSubject.name} Practice
          </h1>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Problem 1</h2>
            <div className="bg-gray-50 p-6 rounded-lg">
              <p className="text-lg text-gray-700">{currentProblem.question}</p>
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Answer:
            </label>
            <textarea
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
              placeholder="Enter your answer here..."
            />
          </div>

          <div className="flex space-x-4 mb-6">
            <button
              onClick={checkAnswer}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
            >
              Check Answer
            </button>
            <button
              onClick={nextProblem}
              className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600"
            >
              Next Problem
            </button>
          </div>

          {showSolution && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Solution:</h3>
              <div className="bg-green-50 p-4 rounded-lg mb-4">
                <p className="font-medium text-green-800">Correct Answer: {currentProblem.answer}</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-blue-800 whitespace-pre-line">{currentProblem.solution}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Practice Problems 🧠</h1>
        <p className="text-gray-600">Choose a subject and start practicing with AI-powered step-by-step solutions</p>
      </div>
      
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {subjects.map(subject => (
          <div key={subject.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
            <div className={`${subject.color} h-2`}></div>
            <div className="p-6">
              <div className="text-4xl mb-4 text-center">{subject.icon}</div>
              <h3 className="text-xl font-bold text-gray-800 mb-3 text-center">
                {subject.name}
              </h3>
              
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">Topics covered:</p>
                <div className="flex flex-wrap gap-1">
                  {subject.topics.map((topic, index) => (
                    <span key={index} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
              
              <button
                onClick={() => startPractice(subject)}
                className={`w-full ${subject.color} text-white py-3 rounded-lg hover:opacity-90 transition-opacity font-medium`}
              >
                Start Practice
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl text-white p-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Need Help with a Specific Problem?</h2>
        <p className="text-lg mb-6">Upload your homework or ask our AI tutor directly!</p>
        <div className="flex justify-center space-x-4">
          <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100">
            Upload Problem
          </button>
          <button className="bg-transparent border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600">
            Ask AI Tutor
          </button>
        </div>
      </div>
    </div>
  )
}

export default Practice