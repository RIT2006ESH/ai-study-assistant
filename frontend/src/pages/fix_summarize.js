  const handleSummarize = async () => {
    if (!summarizeInput.trim()) return

    setIsLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/summarize/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: summarizeInput,
          level: 'moderate'
        })
      })
      
      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || 'Failed to summarize')
      }
      
      const data = await res.json()
      
      setResults([{ 
        title: 'Summary', 
        content: data.summary
      }])
      setSummarizeInput('')
    } catch (error) {
      console.error('Summarization error:', error)
      setResults([{ 
        title: 'Error', 
        content: error.message || 'Failed to summarize. Please try again.' 
      }])
    }
    setIsLoading(false)
  }
