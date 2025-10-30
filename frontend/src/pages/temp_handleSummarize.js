  const handleSummarize = async () => {
    if (!summarizeInput.trim()) return

    setIsLoading(true)
    setResults([])
    
    try {
      const res = await fetch('http://localhost:8000/api/summarize/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          problem: `Please provide a clear and concise summary of the following text:\n\n${summarizeInput}`,
          type: 'general'
        })
      })
      
      const data = await res.json()
      
      if (!res.ok) {
        setResults([{ 
          title: 'Error', 
          content: String(data.detail || data.message || 'Server error') 
        }])
      } else {
        setResults([{ title: 'Summary', content: data.solution || 'No solution provided' }])
        setSummarizeInput('')
      }
    } catch (error) {
      setResults([{ 
        title: 'Error', 
        content: String(error?.message || error || 'Network error. Please check your connection.')
      }])
    }
    
    setIsLoading(false)
  }
