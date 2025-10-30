const API_BASE_URL = 'http://localhost:8000/api'

// Chat endpoints with QUERY VALIDATION
export const chatAPI = {
  /**
   * Send message to chat endpoint
   * Backend expects 'query' field (from chat_routes.py ChatRequest model)
   */
  sendMessage: async (message, context = null) => {
    try {
      const res = await fetch(`${API_BASE_URL}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: message,  // ✅ CHANGED: 'query' instead of 'message'
          context: context
        })
      })

      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.message || 'Failed to send message')
      }

      const data = await res.json()

      // Check if response contains the AI reply
      if (data.response) {
        return {
          success: true,
          error: false,
          response: data.response,
          isRejected: false
        }
      }

      // Handle validation rejection (if backend implements it)
      if (!data.success) {
        return {
          success: false,
          error: true,
          message: data.message || 'This assistant only answers study-related questions.',
          details: data.details,
          validation: data.validation,
          isRejected: true
        }
      }

      // Fallback for unexpected response format
      return {
        success: true,
        error: false,
        response: data.response || JSON.stringify(data),
        isRejected: false
      }
    } catch (error) {
      console.error('Chat error:', error)
      return {
        success: false,
        error: true,
        message: error.message || 'Failed to send message',
        isRejected: false
      }
    }
  },

  /**
   * Validate a query before sending (optional pre-check)
   */
  validateQuery: async (query) => {
    try {
      const res = await fetch(`${API_BASE_URL}/chat/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })

      if (!res.ok) throw new Error('Validation failed')
      return await res.json()
    } catch (error) {
      console.error('Validation error:', error)
      return {
        valid: false,
        reason: 'Validation service unavailable'
      }
    }
  },

  /**
   * Check chat service health
   */
  checkHealth: async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/chat/health`, {
        method: 'GET'
      })
      if (!res.ok) throw new Error('Health check failed')
      return await res.json()
    } catch (error) {
      console.error('Health check error:', error)
      return { status: 'unhealthy', error: error.message }
    }
  },

  /**
   * Summarize text using chat endpoint
   */
  summarizeText: async (text) => {
    try {
      const res = await fetch(`${API_BASE_URL}/chat/summarize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })
      if (!res.ok) throw new Error('Failed to summarize')
      return await res.json()
    } catch (error) {
      console.error('Summarization error:', error)
      throw error
    }
  }
}

// Document endpoints
export const documentAPI = {
  uploadDocument: async (file, userId) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${userId}`
        }
      })
      if (!res.ok) throw new Error('Failed to upload document')
      return await res.json()
    } catch (error) {
      console.error('Upload error:', error)
      throw error
    }
  },

  getDocuments: async (userId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/documents/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${userId}`
        }
      })
      if (!res.ok) throw new Error('Failed to fetch documents')
      return await res.json()
    } catch (error) {
      console.error('Fetch documents error:', error)
      throw error
    }
  },

  deleteDocument: async (documentId, userId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${userId}`
        }
      })
      if (!res.ok) throw new Error('Failed to delete document')
      return await res.json()
    } catch (error) {
      console.error('Delete error:', error)
      throw error
    }
  }
}

// Summarization endpoints
export const summarizationAPI = {
  summarizeDocument: async (documentId, userId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/summarize/document/${documentId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userId}`
        }
      })
      if (!res.ok) throw new Error('Failed to summarize document')
      return await res.json()
    } catch (error) {
      console.error('Document summarization error:', error)
      throw error
    }
  },

  summarizeImage: async (imageFile, userId) => {
    try {
      const formData = new FormData()
      formData.append('file', imageFile)

      const res = await fetch(`${API_BASE_URL}/summarize/image`, {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${userId}`
        }
      })
      if (!res.ok) throw new Error('Failed to analyze image')
      return await res.json()
    } catch (error) {
      console.error('Image analysis error:', error)
      throw error
    }
  },

  transcribeAudio: async (audioFile, userId) => {
    try {
      const formData = new FormData()
      formData.append('file', audioFile)

      const res = await fetch(`${API_BASE_URL}/summarize/audio`, {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${userId}`
        }
      })
      if (!res.ok) throw new Error('Failed to transcribe audio')
      return await res.json()
    } catch (error) {
      console.error('Audio transcription error:', error)
      throw error
    }
  },

  solveProblem: async (problemText, problemType, userId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/summarize/solve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userId}`
        },
        body: JSON.stringify({
          problem: problemText,
          type: problemType
        })
      })
      if (!res.ok) throw new Error('Failed to solve problem')
      return await res.json()
    } catch (error) {
      console.error('Problem solving error:', error)
      throw error
    }
  }
}

// Auth endpoints
export const authAPI = {
  login: async (email, password) => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      if (!res.ok) throw new Error('Login failed')
      return await res.json()
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  },

  register: async (email, password, name) => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name })
      })
      if (!res.ok) throw new Error('Registration failed')
      return await res.json()
    } catch (error) {
      console.error('Registration error:', error)
      throw error
    }
  }
}