'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { Send, Loader2, TrendingUp, TrendingDown, Menu, X, User, Sparkles, Wallet, Activity, Info, Newspaper, LogOut, Settings } from 'lucide-react'
import { sendChatMessage, getCoinPrices, getLatestNews } from '@/lib/api'

export default function Home() {
  const router = useRouter()
  const { user, loading: authLoading, logout } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [prices, setPrices] = useState({})
  const [news, setNews] = useState([])
  const [showUserMenu, setShowUserMenu] = useState(false)
  const messagesEndRef = useRef(null)

  // Auth Check - Redirect to login if not authenticated
  useEffect(() => {
    console.log('🏠 Home - Auth state:', { user, authLoading })
    
    if (!authLoading && !user) {
      console.log('❌ No user, redirecting to login...')
      router.push('/login')
    }
  }, [user, authLoading, router])

  // Initialize data when user is loaded
  useEffect(() => {
    if (user) {
      console.log('✅ User loaded:', user)
      initializeApp()
    }
  }, [user])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const initializeApp = () => {
    // Welcome message
    setMessages([{
      role: 'assistant',
      content: `👋 Salam ${user.name}!\n\nMain aapka AI crypto investment advisor hoon.\n\n💰 Balance: $${user.balance?.toLocaleString()}\n🎯 Risk Tolerance: ${user.risk_tolerance}/10\n\nKisi bhi coin ke baare mein pooch sakte ho! Bitcoin, Ethereum, Solana, ya koi bhi coin!`,
      timestamp: new Date()
    }])

    // Fetch initial data
    fetchPrices()
    fetchNews()
    
    // Set up intervals
    const priceInterval = setInterval(fetchPrices, 30000) // Every 30s
    const newsInterval = setInterval(fetchNews, 300000)   // Every 5min
    
    return () => {
      clearInterval(priceInterval)
      clearInterval(newsInterval)
    }
  }

  const fetchPrices = async () => {
    try {
      const symbols = 'BTC,ETH,BNB,SOL,ADA,XRP,DOGE,DOT,MATIC,AVAX,LINK,UNI,LTC,ATOM,SHIB,TRX,TON,LEO,DAI,WBTC,BCH,ETC,XLM,ALGO,VET,FIL,ICP,HBAR,APT,CRO,NEAR,QNT,LDO,ARB,OP,IMX,SAND,MANA,AXS,GALA,APE,CHZ,ENJ,FTM,GRT,AAVE,MKR,SNX,COMP,YFI'
      const data = await getCoinPrices(symbols)
      setPrices(data.prices || {})
      console.log(`✅ Loaded ${Object.keys(data.prices || {}).length} coins`)
    } catch (error) {
      console.error('❌ Failed to fetch prices:', error)
    }
  }

  const fetchNews = async () => {
    try {
      const data = await getLatestNews(5, 'hot')
      setNews(data.news || [])
      console.log(`✅ Loaded ${data.news?.length || 0} news items`)
    } catch (error) {
      console.error('❌ Failed to fetch news:', error)
    }
  }

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
      console.error('❌ Chat error:', error)
      const errorMessage = {
        role: 'assistant',
        content: '❌ Sorry, backend se connect nahi ho paya! Backend running hai? Check karo.',
        timestamp: new Date(),
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    if (confirm('Are you sure you want to logout?')) {
      await logout()
    }
  }

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading your account...</p>
        </div>
      </div>
    )
  }

  // Don't render if no user (will redirect)
  if (!user) {
    return null
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Navbar */}
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-40">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-lg font-bold gradient-text">Crypto AI Advisor</h1>
                <p className="text-xs text-gray-400">Investment Chatbot</p>
              </div>
            </div>

            {/* User Menu - Improved */}
            <div className="flex items-center space-x-2">
              <div className="relative">
                <button 
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-3 px-4 py-2 rounded-xl hover:bg-slate-800/50 transition-all group"
                >
                  {/* Avatar with status */}
                  <div className="relative">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg group-hover:shadow-blue-500/50 transition-all">
                      <User className="w-5 h-5" />
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-slate-900 animate-pulse" />
                  </div>
                  
                  {/* User Info - Desktop */}
                  <div className="text-left hidden md:block">
                    <p className="text-sm font-semibold text-white">{user.name}</p>
                    <p className="text-xs text-gray-400">
                      ${user.balance?.toLocaleString()}
                    </p>
                  </div>
                </button>

                {/* Improved Dropdown */}
                {showUserMenu && (
                  <>
                    <div 
                      className="fixed inset-0 z-40"
                      onClick={() => setShowUserMenu(false)}
                    />
                    <div className="absolute right-0 mt-2 w-80 bg-slate-800/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-700 overflow-hidden z-50 animate-slide-up">
                      {/* Header */}
                      <div className="p-6 bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-blue-500/20 border-b border-slate-700">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-xl">
                              <User className="w-7 h-7" />
                            </div>
                            <div>
                              <p className="text-lg font-bold text-white">{user.name}</p>
                              <p className="text-sm text-gray-300">{user.email}</p>
                            </div>
                          </div>
                          <button
                            onClick={() => setShowUserMenu(false)}
                            className="p-1 hover:bg-slate-700 rounded-lg transition-colors"
                          >
                            <X className="w-4 h-4 text-gray-400" />
                          </button>
                        </div>
                      </div>

                      {/* Stats Grid */}
                      <div className="p-4 bg-slate-800/50 border-b border-slate-700">
                        <div className="grid grid-cols-2 gap-3">
                          {/* Balance */}
                          <div className="glass rounded-xl p-3">
                            <div className="flex items-center space-x-2 mb-1">
                              <Wallet className="w-4 h-4 text-blue-400" />
                              <span className="text-xs text-gray-400">Balance</span>
                            </div>
                            <p className="text-lg font-bold text-white">
                              ${user.balance?.toLocaleString()}
                            </p>
                          </div>

                          {/* Risk */}
                          <div className="glass rounded-xl p-3">
                            <div className="flex items-center space-x-2 mb-1">
                              <Activity className="w-4 h-4 text-purple-400" />
                              <span className="text-xs text-gray-400">Risk</span>
                            </div>
                            <p className="text-lg font-bold text-purple-400">
                              {user.risk_tolerance}/10
                            </p>
                          </div>
                        </div>

                        {/* Risk Meter */}
                        <div className="mt-3 glass rounded-xl p-3">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs text-gray-400">Risk Tolerance</span>
                            <span className="text-xs font-bold text-purple-400">
                              {user.risk_tolerance <= 3 ? 'Conservative' : user.risk_tolerance <= 6 ? 'Moderate' : 'Aggressive'}
                            </span>
                          </div>
                          
                          {/* Progress Bar */}
                          <div className="relative w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                            <div 
                              className="absolute top-0 left-0 h-full bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 rounded-full transition-all duration-500"
                              style={{ width: `${(user.risk_tolerance / 10) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Mini Chart */}
                      <div className="p-4 border-b border-slate-700">
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-sm font-semibold text-white">Performance</span>
                          <span className="text-xs text-green-400 font-semibold">+12.5%</span>
                        </div>
                        
                        {/* Simple Bar Chart */}
                        <div className="relative h-16 flex items-end justify-between space-x-1">
                          {[40, 55, 45, 70, 65, 80, 75, 90, 85, 100].map((height, i) => (
                            <div key={i} className="flex-1 flex flex-col justify-end group">
                              <div 
                                className="w-full bg-gradient-to-t from-purple-500 to-pink-500 rounded-t transition-all group-hover:opacity-80 cursor-pointer"
                                style={{ height: `${height}%` }}
                              />
                            </div>
                          ))}
                        </div>
                        
                        <div className="flex justify-between mt-2">
                          <span className="text-xs text-gray-500">Last 10 days</span>
                          <span className="text-xs text-gray-400">Today</span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="p-3 space-y-1">
                        <button 
                          onClick={() => {
                            setShowUserMenu(false)
                            router.push('/charts')
                          }}
                          className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-purple-500/10 transition-colors text-left group"
                        >
                          <Activity className="w-5 h-5 text-gray-400 group-hover:text-purple-400 transition-colors" />
                          <div>
                            <p className="text-sm font-medium text-white group-hover:text-purple-400 transition-colors">
                              View Charts
                            </p>
                            <p className="text-xs text-gray-400">Portfolio analytics</p>
                          </div>
                        </button>

                        <button 
                          onClick={handleLogout}
                          className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-red-500/10 transition-colors text-left group"
                        >
                          <LogOut className="w-5 h-5 text-gray-400 group-hover:text-red-400 transition-colors" />
                          <div>
                            <p className="text-sm font-medium text-white group-hover:text-red-400 transition-colors">
                              Logout
                            </p>
                            <p className="text-xs text-gray-400">Sign out of your account</p>
                          </div>
                        </button>
                      </div>
                    </div>
                  </>
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
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, i) => (
              <MessageBubble key={i} message={msg} />
            ))}
            {loading && <LoadingBubble />}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-slate-800 p-4 bg-slate-900/50">
            <div className="max-w-4xl mx-auto relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSend()
                  }
                }}
                placeholder="Bitcoin mein invest karna chahiye? Type karo..."
                className="w-full bg-slate-800 text-white rounded-2xl px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                rows="1"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                className="absolute right-2 bottom-2 p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2 text-center">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </div>
        
        {/* Sidebar - Desktop */}
        <div className="hidden lg:block w-80">
          <Sidebar prices={prices} user={user} news={news} />
        </div>
        
        {/* Sidebar - Mobile */}
        {sidebarOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
            <div className="absolute right-0 top-0 h-full w-80 bg-slate-900">
              <div className="flex items-center justify-between p-4 border-b border-slate-800">
                <h2 className="text-lg font-semibold text-white">Market Info</h2>
                <button onClick={() => setSidebarOpen(false)} className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>
              <Sidebar prices={prices} user={user} news={news} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ====================== COMPONENTS ======================

function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex items-start space-x-3 animate-slide-up ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser ? 'bg-gradient-to-br from-blue-500 to-cyan-500' : 'bg-gradient-to-br from-purple-500 to-pink-500'
      }`}>
        <span className="text-sm">{isUser ? '👤' : '🤖'}</span>
      </div>

      {/* Message Content */}
      <div className={`max-w-2xl ${isUser ? 'ml-auto' : ''}`}>
        <div className={`rounded-2xl p-4 ${
          isUser ? 'bg-gradient-to-br from-blue-600 to-cyan-600' : 
          message.error ? 'bg-red-900/30 border border-red-500/50' : 'glass'
        }`}>
          <p className="text-sm text-white whitespace-pre-wrap">{message.content}</p>
          
          {/* Risk Analysis */}
          {message.risk && (
            <div className="mt-3 p-3 bg-slate-800/50 rounded-lg">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">Risk Score:</span>
                <span className={`font-semibold ${
                  message.risk.risk_score <= 3 ? 'text-green-400' :
                  message.risk.risk_score <= 6 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {message.risk.risk_score?.toFixed(1)}/10
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

function LoadingBubble() {
  return (
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
  )
}

function Sidebar({ prices, user, news }) {
  const allCoins = Object.entries(prices)
  const topCoins = allCoins.slice(0, 10)
  
  return (
    <div className="h-full bg-slate-900/30 backdrop-blur border-l border-slate-800 overflow-y-auto">
      <div className="p-4 space-y-6">
        {/* Top Coins */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-purple-400" />
              <h2 className="text-lg font-semibold text-white">Live Prices</h2>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            </div>
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <Info className="w-3 h-3" />
              <span>{allCoins.length}</span>
            </div>
          </div>
          
          <div className="space-y-2">
            {topCoins.length > 0 ? topCoins.map(([symbol, data]) => (
              <CoinCard key={symbol} symbol={symbol} data={data} />
            )) : (
              [1,2,3,4,5].map(i => (
                <div key={i} className="glass rounded-lg p-3 animate-pulse">
                  <div className="h-4 bg-slate-700 rounded w-3/4 mb-2" />
                  <div className="h-3 bg-slate-700 rounded w-1/2" />
                </div>
              ))
            )}
          </div>
          
          {allCoins.length > 10 && (
            <div className="mt-3 p-2 glass rounded-lg text-center">
              <p className="text-xs text-gray-400">
                + {allCoins.length - 10} more coins tracking
              </p>
            </div>
          )}
        </div>

        {/* Portfolio */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <Wallet className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-semibold text-white">Portfolio</h2>
          </div>
          <div className="glass rounded-xl p-4 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">Balance</span>
              <span className="text-white font-semibold">${user?.balance?.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">Risk Tolerance</span>
              <span className="text-purple-400 font-semibold">{user?.risk_tolerance}/10</span>
            </div>
            <div className="border-t border-slate-700 pt-3">
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                  style={{ width: `${((user?.risk_tolerance || 5) / 10) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* News */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <Newspaper className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-semibold text-white">Latest News</h2>
          </div>
          
          <div className="space-y-3">
            {news.length > 0 ? news.map((item, i) => (
              <NewsCard key={item.id || i} news={item} />
            )) : (
              [1,2,3].map(i => (
                <div key={i} className="glass rounded-lg p-3 animate-pulse">
                  <div className="h-3 bg-slate-700 rounded w-full mb-2" />
                  <div className="h-2 bg-slate-700 rounded w-2/3" />
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function CoinCard({ symbol, data }) {
  const isPositive = data.change_24h >= 0
  return (
    <div className="glass rounded-lg p-3 hover:bg-slate-800/50 transition-all cursor-pointer group">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <span className="text-xs font-bold">{symbol.slice(0,3)}</span>
          </div>
          <div>
            <p className="text-white font-semibold text-sm">{symbol}</p>
            <p className="text-xs text-gray-400">${data.price?.toFixed(2)}</p>
          </div>
        </div>
        
        <div className={`flex items-center text-sm font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          {isPositive ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
          {Math.abs(data.change_24h)?.toFixed(2)}%
        </div>
      </div>
    </div>
  )
}

function NewsCard({ news }) {
  const timeAgo = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const seconds = Math.floor((now - date) / 1000)
    
    if (seconds < 60) return `${seconds}s ago`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
    return `${Math.floor(seconds / 86400)}d ago`
  }

  return (
    <a
      href={news.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block glass rounded-lg p-3 hover:bg-slate-800/50 transition-all cursor-pointer group"
    >
      <p className="text-sm text-white line-clamp-2 group-hover:text-purple-400 transition-colors leading-snug">
        {news.title}
      </p>
      
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs text-gray-500">{news.source || 'News'}</span>
        <span className="text-xs text-gray-600">{timeAgo(news.published_at)}</span>
      </div>
      
      {news.currencies && news.currencies.length > 0 && (
        <div className="flex gap-1 mt-2 flex-wrap">
          {news.currencies.slice(0, 3).map(coin => (
            <span key={coin} className="text-xs px-2 py-0.5 bg-purple-500/20 rounded text-purple-300">
              {coin}
            </span>
          ))}
        </div>
      )}
    </a>
  )
}