'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, TrendingUp, AlertCircle } from 'lucide-react'
import { sendChatMessage } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

export default function ChatInterface() {
  const { user } = useAuth()
  
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `👋 Salam ${user?.name || 'Boss'}! Main aapka AI crypto investment advisor hoon. Bitcoin, Ethereum ya kisi bhi coin ke baare mein pooch sakte ho!`,
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Update welcome message when user loads
  useEffect(() => {
    if (user) {
      setMessages([{
        role: 'assistant',
        content: `👋 Salam ${user.name}! Main aapka AI crypto investment advisor hoon. Bitcoin, Ethereum ya kisi bhi coin ke baare mein pooch sakte ho!`,
        timestamp: new Date()
      }])
    }
  }, [user])

  const handleSend = async () => {
    if (!input.trim() || loading || !user) return

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await sendChatMessage({
        message: input,
        user_id: user.user_id,
        user_risk_tolerance: user.risk_tolerance || 5,
        user_balance: user.balance || 1000,
        include_trading: false
      })

      const botMessage = {
        role: 'assistant',
        content: response.response,
        coins: response.coins_mentioned || [],
        risk: response.risk_analysis,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage = {
        role: 'assistant',
        content: '❌ Sorry, kuch error aa gayi. Backend running hai? Phir se try karo!',
        timestamp: new Date(),
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Show loading if user not loaded yet
  if (!user) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-4">
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}
        
        {loading && (
          <div className="flex items-start space-x-3 animate-slide-up">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
              <span className="text-sm">🤖</span>
            </div>
            <div className="glass rounded-2xl p-4">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full loading-dot"></div>
                <div className="w-2 h-2 bg-purple-500 rounded-full loading-dot"></div>
                <div className="w-2 h-2 bg-purple-500 rounded-full loading-dot"></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-800 p-4 bg-slate-900/50 backdrop-blur">
        <div className="max-w-4xl mx-auto">
          <div className="relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Bitcoin mein invest karna chahiye? Type karo..."
              className="w-full bg-slate-800 text-white rounded-2xl px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
              rows="1"
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="absolute right-2 bottom-2 p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  )
}

// Message Bubble Component
function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex items-start space-x-3 animate-slide-up ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser 
          ? 'bg-gradient-to-br from-blue-500 to-cyan-500' 
          : 'bg-gradient-to-br from-purple-500 to-pink-500'
      }`}>
        <span className="text-sm">{isUser ? '👤' : '🤖'}</span>
      </div>

      {/* Message Content */}
      <div className={`max-w-2xl ${isUser ? 'ml-auto' : ''}`}>
        <div className={`rounded-2xl p-4 ${
          isUser 
            ? 'bg-gradient-to-br from-blue-600 to-cyan-600' 
            : message.error
            ? 'bg-red-900/30 border border-red-500/50'
            : 'glass'
        }`}>
          <p className="text-sm text-white whitespace-pre-wrap">{message.content}</p>
          
          {/* Risk Analysis */}
          {message.risk && (
            <div className="mt-3 p-3 bg-slate-800/50 rounded-lg">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">Risk Score:</span>
                <span className={`font-semibold ${
                  message.risk.risk_score <= 3 ? 'text-green-400' :
                  message.risk.risk_score <= 6 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {message.risk.risk_score?.toFixed(1)}/10
                </span>
              </div>
              <div className="flex items-center justify-between text-xs mt-1">
                <span className="text-gray-400">Risk Level:</span>
                <span className="font-semibold text-purple-400 uppercase">
                  {message.risk.risk_level}
                </span>
              </div>
            </div>
          )}

          {/* Mentioned Coins */}
          {message.coins && message.coins.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-2">
              {message.coins.map(coin => (
                <span key={coin} className="px-2 py-1 bg-purple-500/20 rounded-full text-xs text-purple-300">
                  {coin}
                </span>
              ))}
            </div>
          )}
        </div>
        
        <p className="text-xs text-gray-500 mt-1 px-2">
          {message.timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  )
}