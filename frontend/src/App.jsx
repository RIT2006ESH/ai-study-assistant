import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Home from './pages/Home'
import Study from './pages/Study'
import Practice from './pages/Practice'
import Library from './pages/Library'
import Analytics from './pages/Analytics'

function Navigation() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', name: 'Home', icon: '🏠' },
    { path: '/study', name: 'Study', icon: '📚' },
    { path: '/practice', name: 'Practice', icon: '🧠' },
    { path: '/library', name: 'Library', icon: '📖' },
    { path: '/analytics', name: 'Analytics', icon: '📊' }
  ]

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="text-xl font-bold">AI Study Assistant</Link>
          <div className="flex space-x-4">
            {navItems.map(item => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === item.path
                    ? 'bg-blue-700 text-white'
                    : 'text-blue-100 hover:bg-blue-500'
                }`}
              >
                <span className="mr-1">{item.icon}</span>
                {item.name}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/study" element={<Study />} />
          <Route path="/practice" element={<Practice />} />
          <Route path="/library" element={<Library />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App