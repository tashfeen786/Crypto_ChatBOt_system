'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { Send, Loader2, Menu, X, Home as HomeIcon, TrendingUp, Newspaper, Bell, User, BarChart3, Wallet, Settings, LogOut, ChevronDown, Lightbulb } from 'lucide-react'
import { sendChatMessage, getCoinPrices, getUserProfile, getPortfolioPerformance } from '@/lib/api'

export default function Home() {
  const router = useRouter()
  const pathname = usePathname()
  
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '👋 Hello! I\'m your AI crypto investment advisor. Feel free to ask me anything about Bitcoin, Ethereum, or any other cryptocurrency!',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const messagesEndRef = useRef(null)

  // User and Portfolio State
  const [userId, setUserId] = useState(null)
  const [user, setUser] = useState({
    name: 'User',
    email: 'user@example.com',
    balance: 1000.00,

    riskTolerance: 5
  })
  const [portfolio, setPortfolio] = useState(null)
  const [portfolioLoading, setPortfolioLoading] = useState(true)

  // Real prices from backend
  const [prices, setPrices] = useState({})

  // Get user ID from localStorage
  useEffect(() => {
    const rawStoredUserId = localStorage.getItem('user')
    const storedUserId = JSON.parse(rawStoredUserId)?.user_id;
    if (storedUserId) {
      console.log('✅ Page - User ID from localStorage:', storedUserId)
      // Convert to integer if it's a number-like string
      const numericId = parseInt(storedUserId)
      if (!isNaN(numericId)) {
        setUserId(numericId)
      } else {
        // If it's a string like "user_123", extract number or use 1
        const extracted = storedUserId.match(/\d+/)
        setUserId(extracted ? parseInt(extracted[0]) : 4)
      }
    } else {
      console.log('⚠️ Page - No user ID found, using default ID: 4')
      setUserId(4)  // Use integer 4 instead of "user_123"
    }
  }, [])

  // Fetch prices and portfolio
  useEffect(() => {
    if (userId) {
      fetchAll()
      const interval = setInterval(fetchAll, 10000)
      return () => clearInterval(interval)
    }
  }, [userId])

  const fetchAll = async () => {
    await Promise.all([
      fetchPrices(),
      fetchPortfolio()
    ])
  }

  const fetchPrices = async () => {
    try {
      const data = await getCoinPrices()
      setPrices(data.prices || {})
    } catch (error) {
      console.error('Failed to fetch prices:', error)
    }
  }

  const fetchPortfolio = async () => {
    if (!userId) return

    try {
      console.log('🔄 Page - Fetching portfolio for user:', userId)
      
      // Fetch user profile
      const profileResponse = await getUserProfile(userId).catch(err => {
        console.error('❌ Page - Profile API Error:', err)
        return null
      })

      if (!profileResponse) {
        setPortfolioLoading(false)
        return
      }

      // Update user data
      setUser(prev => ({
        ...prev,
        balance: profileResponse.balance || 1000,
        riskTolerance: profileResponse.risk_tolerance || 5
      }))

      // Try to fetch performance data
      const performanceResponse = await getPortfolioPerformance(userId).catch(err => {
        console.error('⚠️ Page - Performance API not available')
        return null
      })
      
      // Calculate portfolio data
      let balance = profileResponse.balance || 1000
      let invested = 0
      let currentValue = 0
      let pnl = 0
      let pnlPercentage = 0

      if (performanceResponse && performanceResponse.status === 'success') {
        invested = performanceResponse.total_invested || 0
        currentValue = performanceResponse.current_value || 0
        pnl = performanceResponse.total_pnl || 0
        pnlPercentage = performanceResponse.pnl_percentage || 0
      } else if (profileResponse.portfolio) {
        const holdings = profileResponse.portfolio.holdings || {}
        
        // Calculate from transactions
        if (profileResponse.transactions) {
          const buyTotal = profileResponse.transactions
            .filter(t => t.type === 'buy')
            .reduce((sum, t) => sum + (t.amount * t.price), 0)
          const sellTotal = profileResponse.transactions
            .filter(t => t.type === 'sell')
            .reduce((sum, t) => sum + (t.amount * t.price), 0)
          
          invested = buyTotal - sellTotal
        }
        
        // Calculate current value
        currentValue = Object.entries(holdings).reduce((sum, [symbol, amount]) => {
          const currentPrice = prices[symbol]?.price || 0
          return sum + (amount * currentPrice)
        }, 0)
        
        pnl = currentValue - invested
        pnlPercentage = invested > 0 ? (pnl / invested) * 100 : 0
      }

      setPortfolio({
        balance: balance,
        invested: invested,
        currentValue: currentValue,
        pnl: pnl,
        pnlPercentage: pnlPercentage,
        holdings: profileResponse.portfolio?.holdings || {}
      })
      
      console.log('✅ Page - Portfolio loaded:', { balance, invested, pnl })
      setPortfolioLoading(false)
    } catch (error) {
      console.error('❌ Page - Failed to fetch portfolio:', error)
      setPortfolioLoading(false)
    }
  }

  const navigation = [
    { name: 'Chat', icon: HomeIcon, path: '/' },
    { name: 'Trading', icon: TrendingUp, path: '/trading' },
    { name: 'Portfolio', icon: BarChart3, path: '/portfolio' },
    { name: 'News', icon: Newspaper, path: '/news' },
    { name: 'Alerts', icon: Bell, path: '/alerts' },
    { name: 'Profile', icon: User, path: '/profile' }
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentInput = input
    setInput('')
    setLoading(true)

    try {
      const response = await sendChatMessage({
        message: currentInput,
        user_id: userId || 'user_123',
        user_risk_tolerance: user.riskTolerance,
        user_balance: user.balance,
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
      console.error('Chat API Error:', error)
      const errorMessage = {
        role: 'assistant',
        content: '❌ Sorry, there was an error connecting to the backend. Please make sure the backend server is running!',
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

  const handleNavigation = (path) => {
    router.push(path)
    setSidebarOpen(false)
  }

  // Get smart tip based on portfolio
  const getSmartTip = () => {
    if (!portfolio) {
      return "Start your crypto journey! Research and invest wisely."
    }

    const holdingsCount = Object.keys(portfolio.holdings).length

    if (portfolio.invested === 0) {
      return "Ready to invest? Start with small amounts and gradually increase."
    } else if (holdingsCount === 1) {
      return "Consider diversifying! Multiple coins can help reduce risk."
    } else if (portfolio.pnlPercentage > 20) {
      return "Great gains! Consider booking partial profits."
    } else if (portfolio.pnlPercentage < -10) {
      return "Market down? Stay calm and stick to your strategy."
    } else {
      return "Portfolio looking good! Keep monitoring market trends."
    }
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Navbar */}
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-40">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            
            {/* Logo & Title */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <span className="text-xl">🤖</span>
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Crypto AI Advisor
                </h1>
                <p className="text-xs text-gray-400">Investment Chatbot</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-1">
              {navigation.map((item) => (
                <button
                  key={item.path}
                  onClick={() => handleNavigation(item.path)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                    pathname === item.path
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-400 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <item.icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{item.name}</span>
                </button>
              ))}
            </div>

            {/* Right Actions */}
            <div className="flex items-center space-x-2">
              
              {/* User Profile Dropdown */}
              <div className="hidden sm:block relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                    <User className="w-4 h-4" />
                  </div>
                  <div className="text-left hidden md:block">
                    <p className="text-sm font-medium text-white">{user.name}</p>
                    <p className="text-xs text-gray-400">Risk: {user.riskTolerance}/10</p>
                  </div>
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                </button>

                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-slate-800 rounded-xl shadow-xl border border-slate-700 py-2">
                    <button
                      onClick={() => handleNavigation('/profile')}
                      className="w-full flex items-center space-x-2 px-4 py-2 hover:bg-slate-700 text-white text-sm"
                    >
                      <Settings className="w-4 h-4" />
                      <span>Settings</span>
                    </button>
                    <button
                      onClick={() => router.push('/login')}
                      className="w-full flex items-center space-x-2 px-4 py-2 hover:bg-slate-700 text-red-400 text-sm"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                )}
              </div>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-slate-800 transition-colors"
              >
                <Menu className="w-5 h-5 text-gray-400" />
              </button>
            </div>

          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Chat Interface */}
        <div className="flex-1 flex flex-col">
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <MessageBubble key={index} message={message} />
            ))}
            
            {loading && (
              <div className="flex items-start space-x-3 animate-slide-up">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                  <span className="text-sm">🤖</span>
                </div>
                <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-4">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
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
                  placeholder="Should I invest in Bitcoin? Type your question..."
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
        
        {/* Desktop Sidebar - WITH REAL DATA */}
        <div className="hidden lg:block w-80 xl:w-96 border-l border-slate-800 bg-slate-900/30 backdrop-blur overflow-y-auto">
          <div className="p-4 space-y-6">
            
            {/* Live Prices */}
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <TrendingUp className="w-5 h-5 text-purple-400" />
                <h2 className="text-lg font-semibold text-white">Live Prices</h2>
                {Object.keys(prices).length > 0 && (
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                )}
              </div>
              
              <div className="space-y-2">
                {Object.entries(prices).length === 0 ? (
                  <div className="text-center text-gray-500 text-sm py-4">
                    Loading prices...
                  </div>
                ) : (
                  Object.entries(prices).slice(0, 5).map(([symbol, data]) => (
                    <div key={symbol} className="bg-slate-800/50 backdrop-blur rounded-lg p-3 hover:bg-slate-800/70 transition-all cursor-pointer group">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                            <span className="text-xs font-bold">{symbol}</span>
                          </div>
                          <div>
                            <p className="text-white font-semibold">{symbol}</p>
                            <p className="text-xs text-gray-400">${data.price?.toFixed(2)}</p>
                          </div>
                        </div>
                        
                        <div className="text-right">
                          <div className={`flex items-center text-sm font-semibold ${
                            data.change_24h >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {data.change_24h >= 0 ? '↑' : '↓'}
                            {Math.abs(data.change_24h)?.toFixed(2)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Portfolio Summary - REAL DATA */}
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Wallet className="w-5 h-5 text-purple-400" />
                <h2 className="text-lg font-semibold text-white">Portfolio</h2>
              </div>
              
              {portfolioLoading ? (
                <div className="bg-slate-800/50 backdrop-blur rounded-xl p-4 animate-pulse">
                  <div className="h-4 bg-slate-700 rounded w-3/4 mb-3" />
                  <div className="h-4 bg-slate-700 rounded w-2/3 mb-3" />
                  <div className="h-4 bg-slate-700 rounded w-1/2" />
                </div>
              ) : portfolio ? (
                <div className="bg-slate-800/50 backdrop-blur rounded-xl p-4 space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 text-sm">Balance</span>
                    <span className="text-white font-semibold">${portfolio.balance.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 text-sm">Invested</span>
                    <span className="text-white font-semibold">${portfolio.invested.toFixed(2)}</span>
                  </div>
                  <div className="border-t border-slate-700 pt-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400 text-sm">P&L</span>
                      <span className={`font-semibold flex items-center ${
                        portfolio.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {portfolio.pnl >= 0 ? '↑' : '↓'} 
                        {portfolio.pnl >= 0 ? '+' : ''}${Math.abs(portfolio.pnl).toFixed(2)} 
                        ({portfolio.pnlPercentage.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-slate-800/50 backdrop-blur rounded-xl p-4 text-center">
                  <p className="text-gray-400 text-sm">Failed to load portfolio</p>
                </div>
              )}
            </div>

            {/* Smart Tip - Dynamic */}
            <div className="bg-slate-800/50 backdrop-blur rounded-xl p-4 border border-purple-500/20">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="w-4 h-4 text-yellow-400" />
                <h3 className="text-sm font-semibold text-white">💡 Smart Tip</h3>
              </div>
              <p className="text-xs text-gray-300">
                {getSmartTip()}
              </p>
            </div>

          </div>
        </div>
        
        {/* Mobile Sidebar */}
        {sidebarOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            {/* Backdrop */}
            <div 
              className="absolute inset-0 bg-black/50 backdrop-blur-sm"
              onClick={() => setSidebarOpen(false)}
            />
            
            {/* Sidebar */}
            <div className="absolute right-0 top-0 h-full w-80 bg-slate-900 overflow-y-auto">
              <div className="flex items-center justify-between p-4 border-b border-slate-800">
                <h2 className="text-lg font-semibold text-white">Menu</h2>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>
              
              {/* Mobile Navigation */}
              <div className="p-4 space-y-2">
                {navigation.map((item) => (
                  <button
                    key={item.path}
                    onClick={() => handleNavigation(item.path)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                      pathname === item.path
                        ? 'bg-purple-600 text-white'
                        : 'text-gray-400 hover:bg-slate-800 hover:text-white'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.name}</span>
                  </button>
                ))}
              </div>

              {/* Mobile Portfolio */}
              <div className="p-4 border-t border-slate-800">
                <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  <Wallet className="w-4 h-4" />
                  Portfolio
                </h3>
                {portfolio ? (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Balance</span>
                      <span className="text-white font-semibold">${portfolio.balance.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Invested</span>
                      <span className="text-white font-semibold">${portfolio.invested.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between pt-2 border-t border-slate-700">
                      <span className="text-gray-400">P&L</span>
                      <span className={portfolio.pnl >= 0 ? 'text-green-400' : 'text-red-400'}>
                        {portfolio.pnl >= 0 ? '+' : ''}${portfolio.pnl.toFixed(2)} ({portfolio.pnlPercentage.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">Loading...</p>
                )}
              </div>

              {/* Mobile Prices */}
              <div className="p-4 border-t border-slate-800">
                <h3 className="text-sm font-semibold text-white mb-3">Live Prices</h3>
                <div className="space-y-2">
                  {Object.entries(prices).length === 0 ? (
                    <div className="text-center text-gray-500 text-sm py-2">
                      Loading...
                    </div>
                  ) : (
                    Object.entries(prices).slice(0, 3).map(([symbol, data]) => (
                      <div key={symbol} className="flex justify-between items-center">
                        <span className="text-white font-medium">{symbol}</span>
                        <div className="text-right">
                          <p className="text-white text-sm">${data.price?.toFixed(2)}</p>
                          <p className={`text-xs ${data.change_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {data.change_24h >= 0 ? '+' : ''}{data.change_24h?.toFixed(2)}%
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser 
          ? 'bg-gradient-to-br from-blue-500 to-cyan-500' 
          : message.error
          ? 'bg-red-900'
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
            : 'bg-slate-800/50 backdrop-blur'
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