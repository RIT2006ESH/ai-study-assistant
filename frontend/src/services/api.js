const API_BASE_URL = 'http://localhost:8000/api'

// Chat endpoints
export const chatAPI = {
  sendMessage: async (message) => {
    try {
      const res = await fetch(`${API_BASE_URL}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      })
      if (!res.ok) throw new Error('Failed to send message')
      return await res.json()
    } catch (error) {
      console.error('Chat error:', error)
      throw error
    }
  },

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

// Auth endpoints (if needed)
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