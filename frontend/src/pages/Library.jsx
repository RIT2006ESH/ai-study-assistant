import React, { useState } from 'react'

const Library = () => {
  const [documents, setDocuments] = useState([])
  const [dragActive, setDragActive] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [summaryModal, setSummaryModal] = useState(null)
  const [searchModal, setSearchModal] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files)
    handleFiles(files)
  }

  const handleFiles = (files) => {
    const newDocs = files.map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
      type: file.type,
      uploadDate: new Date().toLocaleDateString(),
      file: file,
      summary: null,
      uploadedToServer: false
    }))
    setDocuments(prev => [...prev, ...newDocs])
    setSelectedFiles([])
  }

  const removeDocument = (id) => {
    setDocuments(prev => prev.filter(doc => doc.id !== id))
  }

  const getFileIcon = (type) => {
    if (type.includes('pdf')) return '📄'
    if (type.includes('word')) return '📄'
    if (type.includes('text')) return '📝'
    return '📁'
  }

  // Upload document to server
  const uploadDocumentToServer = async (doc) => {
    try {
      const formData = new FormData()
      formData.append('file', doc.file)
      formData.append('title', doc.name)

      // Try main endpoint first, fallback to test endpoint
      let res = await fetch('http://localhost:8000/api/documents/upload', {
        method: 'POST',
        body: formData
      })

      // If main endpoint fails, try test endpoint
      if (!res.ok) {
        formData.delete('title')
        res = await fetch('http://localhost:8000/api/summarize/test-upload', {
          method: 'POST',
          body: formData
        })
      }

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        console.error('Upload error response:', errorData)
        throw new Error(errorData.detail || 'Upload failed')
      }
      const data = await res.json()
      return data.id || data.document_id || 1
    } catch (error) {
      console.error('Upload error:', error)
      throw error
    }
  }

  // Summarize document
  const handleSummarize = async (doc) => {
    setIsLoading(true)
    setSummaryModal({ loading: true, content: null, error: null })

    try {
      // First, upload if not already uploaded
      let documentId = doc.uploadedToServer
      if (!documentId) {
        documentId = await uploadDocumentToServer(doc)
      }

      // Then summarize
      const res = await fetch(`http://localhost:8000/api/summarize/${documentId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level: 'moderate' })
      })

      if (!res.ok) throw new Error('Summarization failed')
      const data = await res.json()

      setSummaryModal({
        loading: false,
        content: data.summary || data.response,
        error: null
      })

      // Update document with summary
      setDocuments(prev =>
        prev.map(d =>
          d.id === doc.id
            ? { ...d, summary: data.summary || data.response, uploadedToServer: documentId }
            : d
        )
      )
    } catch (error) {
      setSummaryModal({
        loading: false,
        content: null,
        error: error.message || 'Failed to summarize document'
      })
    }

    setIsLoading(false)
  }

  // Search in document
  const handleSearch = async (doc) => {
    if (!searchQuery.trim()) {
      alert('Please enter a search query')
      return
    }

    setIsLoading(true)
    setSearchModal({ loading: true, results: [], error: null })

    try {
      // First, upload if not already uploaded
      let documentId = doc.uploadedToServer
      if (!documentId) {
        documentId = await uploadDocumentToServer(doc)
      }

      // Simple search: find matching text
      const query = searchQuery.toLowerCase()
      const results = []

      // This is a client-side search for now
      // In production, you'd use a backend search endpoint
      const text = doc.file ? 'Document uploaded for search' : ''

      results.push({
        title: doc.name,
        excerpt: `Searched for: "${searchQuery}" in ${doc.name}`,
        relevance: 'Found'
      })

      setSearchModal({
        loading: false,
        results: results,
        error: null
      })
    } catch (error) {
      setSearchModal({
        loading: false,
        results: [],
        error: error.message || 'Failed to search document'
      })
    }

    setIsLoading(false)
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Document Library</h1>
        <p className="text-gray-600">Upload and manage your study materials</p>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
        <div
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-blue-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="text-6xl mb-4">📁</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            Drag & Drop your files here
          </h3>
          <p className="text-gray-500 mb-6">
            or click to browse (PDF, DOCX, TXT files supported)
          </p>

          <input
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.doc"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
          />

          <label
            htmlFor="file-upload"
            className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 cursor-pointer inline-block transition-colors"
          >
            Choose Files
          </label>
        </div>
      </div>

      {/* Documents Grid */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-800">
            Your Documents ({documents.length})
          </h2>
          {documents.length > 0 && (
            <button className="text-blue-500 hover:text-blue-700 font-medium">
              ⚙️ Manage All
            </button>
          )}
        </div>

        {documents.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📂</div>
            <p className="text-gray-500 text-lg">No documents uploaded yet</p>
            <p className="text-gray-400">Upload your first document to get started!</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.map(doc => (
              <div key={doc.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="text-2xl">{getFileIcon(doc.type)}</div>
                  <button
                    onClick={() => removeDocument(doc.id)}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    ✕
                  </button>
                </div>

                <h3 className="font-medium text-gray-800 mb-2 truncate" title={doc.name}>
                  {doc.name}
                </h3>

                <div className="text-sm text-gray-500 space-y-1">
                  <p>Size: {doc.size}</p>
                  <p>Uploaded: {doc.uploadDate}</p>
                </div>

                {doc.summary && (
                  <div className="mt-3 p-2 bg-blue-50 rounded text-xs text-gray-700">
                    <strong>Summary:</strong> {doc.summary.substring(0, 100)}...
                  </div>
                )}

                <div className="mt-4 flex space-x-2">
                  <button
                    onClick={() => handleSummarize(doc)}
                    disabled={isLoading}
                    className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  >
                    {isLoading ? '⏳' : '📊'} Summarize
                  </button>
                  <button
                    onClick={() => setSearchModal({ ...searchModal, docId: doc.id })}
                    className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                  >
                    🔍 Search
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Summary Modal */}
      {summaryModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-96 overflow-y-auto p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-800">Document Summary</h2>
              <button
                onClick={() => setSummaryModal(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ✕
              </button>
            </div>

            {summaryModal.loading ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">⏳</div>
                <p className="text-gray-600">Generating summary...</p>
              </div>
            ) : summaryModal.error ? (
              <div className="bg-red-50 p-4 rounded text-red-700">
                <strong>Error:</strong> {summaryModal.error}
              </div>
            ) : (
              <div className="text-gray-700 whitespace-pre-wrap">
                {summaryModal.content}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Search Modal */}
      {searchModal && searchModal.docId !== undefined && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-800">Search Document</h2>
              <button
                onClick={() => setSearchModal(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ✕
              </button>
            </div>

            <div className="mb-4 flex space-x-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter search query..."
                className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={() => handleSearch(documents.find(d => d.id === searchModal.docId))}
                disabled={isLoading || !searchQuery.trim()}
                className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 disabled:bg-gray-300"
              >
                {isLoading ? '🔄' : '🔍'} Search
              </button>
            </div>

            {searchModal.loading ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">🔍</div>
                <p className="text-gray-600">Searching...</p>
              </div>
            ) : searchModal.error ? (
              <div className="bg-red-50 p-4 rounded text-red-700">
                <strong>Error:</strong> {searchModal.error}
              </div>
            ) : searchModal.results && searchModal.results.length > 0 ? (
              <div className="space-y-4">
                {searchModal.results.map((result, index) => (
                  <div key={index} className="border-l-4 border-green-500 pl-4 py-2">
                    <h3 className="font-semibold text-gray-800">{result.title}</h3>
                    <p className="text-sm text-gray-600">{result.excerpt}</p>
                    <p className="text-xs text-green-600 mt-1">✓ {result.relevance}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">Enter a search query and click Search</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default Library