import React, { useState } from 'react'

const Library = () => {
  const [documents, setDocuments] = useState([])
  const [dragActive, setDragActive] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState([])

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
      file: file
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

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Document Library 📖</h1>
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
                
                <div className="mt-4 flex space-x-2">
                  <button className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200">
                    📊 Summarize
                  </button>
                  <button className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200">
                    🔍 Search
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Library