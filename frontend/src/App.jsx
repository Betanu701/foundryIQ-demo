import { useState, useRef, useEffect } from 'react'

const API_URL = 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const chatContainerRef = useRef(null)

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (question) => {
    if (!question.trim()) return

    setError(null)
    const userMessage = { role: 'user', content: question }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Build chat history for context
      const chatHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          chat_history: chatHistory,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      console.error('Error:', err)
      setError('Failed to get response. Make sure the API server is running.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(input)
  }

  const handleSuggestion = (suggestion) => {
    sendMessage(suggestion)
  }

  const suggestions = [
    "What products are in the catalog?",
    "Show me active support cases",
    "What are the tax jurisdictions?",
    "Any pending change requests?",
    "What's in the compliance calendar?",
  ]

  return (
    <div className="app">
      <header className="header">
        <h1>🔍 FoundryIQ Assistant</h1>
        <p>Ask questions about your Vertex tax documents</p>
      </header>

      <div className="chat-container" ref={chatContainerRef}>
        {messages.length === 0 && (
          <div className="welcome">
            <h2>Welcome to FoundryIQ</h2>
            <p>
              I can help you query and understand your business documents.
              Ask me anything about customers, products, tax data, compliance, and more.
            </p>
            <div className="suggestions">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-btn"
                  onClick={() => handleSuggestion(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">{message.content}</div>
            {message.sources && message.sources.length > 0 && (
              <div className="sources">
                <div className="sources-title">📄 Sources:</div>
                <div>
                  {message.sources.map((source, i) => (
                    <span key={i} className="source-tag">
                      {source.file_name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="loading">
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span>Searching documents...</span>
          </div>
        )}

        {error && <div className="error">{error}</div>}
      </div>

      <div className="input-area">
        <form className="input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            className="input-field"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            disabled={isLoading}
          />
          <button
            type="submit"
            className="send-button"
            disabled={isLoading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}

export default App
