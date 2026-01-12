'use client'

import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Wallet, Target, Activity, AlertCircle, RefreshCw, Lightbulb } from 'lucide-react'
import { getCoinPrices, getUserBalance, getPortfolioPerformance, getUserProfile } from '@/lib/api'

export default function Sidebar() {
  const [prices, setPrices] = useState({})
  const [portfolio, setPortfolio] = useState(null)
  const [loading, setLoading] = useState(true)
  const [portfolioLoading, setPortfolioLoading] = useState(true)
  const [currentTip, setCurrentTip] = useState(0)
  const [error, setError] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)
  const [userId, setUserId] = useState(null)

  // Get user ID from localStorage (set by auth/login)
  useEffect(() => {
    const rawStoredUserId = localStorage.getItem('user')
    const storedUserId = JSON.parse(rawStoredUserId)?.user_id;
    if (storedUserId) {
      console.log('✅ Sidebar - User ID from localStorage:', storedUserId)
      // Convert to integer if it's a number-like string
      const numericId = parseInt(storedUserId)
      if (!isNaN(numericId)) {
        setUserId(numericId)
      } else {
        // If it's a string like "user_123", extract number or use 1
        const extracted = storedUserId.match(/\d+/)
        setUserId(extracted ? parseInt(extracted[0]) : 1)
      }
    } else {
      console.log('⚠️ Sidebar - No user ID found, using default ID: 1')
      setUserId(1)  // Use integer 1 instead of "user_123"
    }
  }, [])

  useEffect(() => {
    if (userId) {
      fetchAll()
      const interval = setInterval(fetchAll, 10000)
      return () => clearInterval(interval)
    }
  }, [userId])

  // Rotate tips every 8 seconds
  useEffect(() => {
    const tipInterval = setInterval(() => {
      setCurrentTip((prev) => (prev + 1) % 5) // Cycle through 5 dynamic tips
    }, 8000)
    return () => clearInterval(tipInterval)
  }, [])

  const fetchAll = async () => {
    await Promise.all([
      fetchPrices(),
      fetchPortfolio()
    ])
  }

  const fetchPrices = async () => {
    try {
      console.log('🔄 Sidebar - Fetching coin prices...')
      const data = await getCoinPrices()
      setPrices(data.prices || {})
      setLoading(false)
      console.log('✅ Sidebar - Prices fetched:', Object.keys(data.prices || {}).length, 'coins')
    } catch (error) {
      console.error('❌ Sidebar - Failed to fetch prices:', error)
      setLoading(false)
    }
  }

  const fetchPortfolio = async () => {
    if (!userId) {
      console.log('⚠️ Sidebar - No user ID available yet')
      return
    }

    try {
      console.log('🔄 Sidebar - Fetching portfolio data for user:', userId)
      
      // Fetch user profile (most reliable)
      const profileResponse = await getUserProfile(userId).catch(err => {
        console.error('❌ Sidebar - Profile API Error:', err)
        return null
      })

      console.log('👤 Sidebar - Profile Response:', profileResponse)

      if (!profileResponse) {
        throw new Error('User not found')
      }

      // Try to fetch performance data
      const performanceResponse = await getPortfolioPerformance(userId).catch(err => {
        console.error('⚠️ Sidebar - Performance API not available, using profile data')
        return null
      })
      
      console.log('📊 Sidebar - Performance Response:', performanceResponse)
      
      // Calculate portfolio data
      let balance = profileResponse.balance || 1000
      let invested = 0
      let currentValue = 0
      let pnl = 0
      let pnlPercentage = 0

      if (performanceResponse && performanceResponse.status === 'success') {
        // Use performance API data if available
        invested = performanceResponse.total_invested || 0
        currentValue = performanceResponse.current_value || 0
        pnl = performanceResponse.total_pnl || 0
        pnlPercentage = performanceResponse.pnl_percentage || 0
      } else if (profileResponse.portfolio) {
        // Fallback: Calculate from profile data
        const holdings = profileResponse.portfolio.holdings || {}
        
        // Calculate invested amount from transactions
        if (profileResponse.transactions) {
          const buyTotal = profileResponse.transactions
            .filter(t => t.type === 'buy')
            .reduce((sum, t) => sum + (t.amount * t.price), 0)
          const sellTotal = profileResponse.transactions
            .filter(t => t.type === 'sell')
            .reduce((sum, t) => sum + (t.amount * t.price), 0)
          
          invested = buyTotal - sellTotal
        }
        
        // Calculate current value of holdings
        currentValue = Object.entries(holdings).reduce((sum, [symbol, amount]) => {
          const currentPrice = prices[symbol]?.price || 0
          return sum + (amount * currentPrice)
        }, 0)
        
        // Calculate P&L
        pnl = currentValue - invested
        pnlPercentage = invested > 0 ? (pnl / invested) * 100 : 0
      }

      const portfolioData = {
        balance: balance,
        invested: invested,
        currentValue: currentValue,
        pnl: pnl,
        pnlPercentage: pnlPercentage,
        holdings: profileResponse.portfolio?.holdings || {}
      }
      
      console.log('✅ Sidebar - Final Portfolio Data:', portfolioData)
      setPortfolio(portfolioData)
      setError(null)
      setLastUpdate(new Date())
      setPortfolioLoading(false)
    } catch (error) {
      console.error('❌ Sidebar - Failed to fetch portfolio:', error)
      setError('Could not load portfolio data')
      setPortfolioLoading(false)
    }
  }

  const handleRefresh = () => {
    console.log('🔄 Sidebar - Manual refresh triggered')
    setLoading(true)
    setPortfolioLoading(true)
    fetchAll()
  }

  // Dynamic Smart Tips based on portfolio state
  const getSmartTip = () => {
    if (!portfolio) {
      return {
        emoji: '💡',
        text: 'Apna portfolio set up karo aur crypto investment journey shuru karo!'
      }
    }

    const holdingsCount = Object.keys(portfolio.holdings).length

    const tips = [
      // Tip 1: Based on investment status
      portfolio.invested === 0
        ? { emoji: '🚀', text: 'Apni pehli crypto investment karo! Start small aur gradually increase karo.' }
        : { emoji: '💰', text: 'DCA (Dollar Cost Averaging) strategy use karo for consistent returns.' },
      
      // Tip 2: Based on diversification
      holdingsCount === 0
        ? { emoji: '📊', text: 'Market research karo aur apni pehli crypto select karo wisely.' }
        : holdingsCount === 1
        ? { emoji: '🎯', text: 'Diversify karo! Multiple coins mein invest karke risk kam karo.' }
        : { emoji: '✅', text: 'Great diversification! Ab regular monitoring karte raho.' },
      
      // Tip 3: Based on P&L
      portfolio.pnlPercentage > 20
        ? { emoji: '🎉', text: 'Amazing gains! Consider partial profit booking aur reinvest karo.' }
        : portfolio.pnlPercentage < -10
        ? { emoji: '💪', text: 'Market down hai? Perfect time to buy the dip strategically!' }
        : { emoji: '📈', text: 'Portfolio stable hai. Market trends watch karo aur patience rakho.' },
      
      // Tip 4: Risk management
      portfolio.invested > portfolio.balance * 0.7
        ? { emoji: '⚠️', text: 'Maintain emergency fund! At least 30% balance liquid rakho.' }
        : { emoji: '🛡️', text: 'Stop-loss orders set karo to protect your investments.' },
      
      // Tip 5: General wisdom
      { emoji: '📚', text: 'Research karo har coin ki fundamentals. Informed decisions best hote hain!' }
    ]

    return tips[currentTip % tips.length]
  }

  const coins = Object.entries(prices).slice(0, 5)

  if (!userId) {
    return (
      <div className="h-full bg-slate-900/30 backdrop-blur border-l border-slate-800 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400 text-sm">Loading user data...</p>
        </div>
      </div>
    )
  }

  const currentSmartTip = getSmartTip()

  return (
    <div className="h-full bg-slate-900/30 backdrop-blur border-l border-slate-800 overflow-y-auto">
      <div className="p-4 space-y-6">
        
        {/* Header with Refresh */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-purple-400" />
            <h2 className="text-sm font-semibold text-white">Market Info</h2>
          </div>
          <button
            onClick={handleRefresh}
            disabled={loading || portfolioLoading}
            className="p-1.5 hover:bg-slate-800 rounded-lg transition-colors disabled:opacity-50"
            title="Refresh data"
          >
            <RefreshCw className={`w-4 h-4 text-gray-400 ${(loading || portfolioLoading) ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="bg-yellow-900/30 border border-yellow-500/50 rounded-lg p-3 flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-xs text-yellow-300 font-semibold">Connection Issue</p>
              <p className="text-xs text-yellow-400/70 mt-1">{error}</p>
              <button
                onClick={handleRefresh}
                className="text-xs text-yellow-300 underline mt-1 hover:text-yellow-200"
              >
                Retry Connection
              </button>
            </div>
          </div>
        )}

        {/* Live Prices Section */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <Activity className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-semibold text-white">Live Prices</h2>
            {!loading && !error && (
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            )}
          </div>
          
          <div className="space-y-2">
            {loading ? (
              // Loading skeletons
              [1, 2, 3, 4, 5].map(i => (
                <div key={i} className="glass rounded-lg p-3 animate-pulse">
                  <div className="h-4 bg-slate-700 rounded w-3/4 mb-2" />
                  <div className="h-3 bg-slate-700 rounded w-1/2" />
                </div>
              ))
            ) : coins.length > 0 ? (
              coins.map(([symbol, data]) => (
                <CoinCard key={symbol} symbol={symbol} data={data} />
              ))
            ) : (
              <div className="glass rounded-lg p-4 text-center">
                <AlertCircle className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-400 text-sm">No price data available</p>
                <p className="text-gray-500 text-xs mt-1">Check if backend is running</p>
              </div>
            )}
          </div>
        </div>

        {/* Portfolio Summary - FIXED WITH REAL DATA */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <Wallet className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-semibold text-white">Portfolio</h2>
          </div>
          
          {portfolioLoading ? (
            <div className="glass rounded-xl p-4 animate-pulse">
              <div className="h-4 bg-slate-700 rounded w-3/4 mb-3" />
              <div className="h-4 bg-slate-700 rounded w-2/3 mb-3" />
              <div className="h-4 bg-slate-700 rounded w-1/2" />
            </div>
          ) : portfolio ? (
            <div className="glass rounded-xl p-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">Available Balance</span>
                <span className="text-white font-semibold text-lg">
                  ${portfolio.balance.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">Total Invested</span>
                <span className="text-white font-semibold">
                  ${portfolio.invested.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">Current Value</span>
                <span className="text-white font-semibold">
                  ${portfolio.currentValue.toFixed(2)}
                </span>
              </div>
              <div className="border-t border-slate-700 pt-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm font-semibold">Profit & Loss</span>
                  <span className={`font-bold text-lg flex items-center ${
                    portfolio.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {portfolio.pnl >= 0 ? (
                      <TrendingUp className="w-5 h-5 mr-1" />
                    ) : (
                      <TrendingDown className="w-5 h-5 mr-1" />
                    )}
                    {portfolio.pnl >= 0 ? '+' : ''}${Math.abs(portfolio.pnl).toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-end mt-1">
                  <span className={`text-sm font-semibold ${
                    portfolio.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    ({portfolio.pnlPercentage >= 0 ? '+' : ''}{portfolio.pnlPercentage.toFixed(2)}%)
                  </span>
                </div>
              </div>
              {lastUpdate && (
                <div className="text-xs text-gray-500 pt-2 border-t border-slate-700 flex items-center justify-between">
                  <span>Last updated:</span>
                  <span className="font-mono">{lastUpdate.toLocaleTimeString()}</span>
                </div>
              )}
            </div>
          ) : (
            <div className="glass rounded-xl p-4 text-center">
              <AlertCircle className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-400 text-sm">Failed to load portfolio</p>
              <button
                onClick={handleRefresh}
                className="text-xs text-purple-400 underline mt-2 hover:text-purple-300"
              >
                Retry
              </button>
            </div>
          )}
        </div>

        {/* Risk Profile */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <Target className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-semibold text-white">Risk Profile</h2>
          </div>
          
          <div className="glass rounded-xl p-4 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">Tolerance</span>
              <span className="text-purple-400 font-semibold">5/10</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">Category</span>
              <span className="text-white font-semibold">Moderate</span>
            </div>
            
            {/* Risk Bar */}
            <div className="pt-2">
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                  style={{ width: '50%' }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Smart Tips - DYNAMIC & PERSONALIZED */}
        <div className="glass rounded-xl p-4 transition-all hover:bg-slate-800/50 border border-purple-500/20">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-400" />
              <h3 className="text-sm font-semibold text-white">
                {currentSmartTip.emoji} Smart Tip
              </h3>
            </div>
            <div className="flex space-x-1">
              {[0, 1, 2, 3, 4].map((idx) => (
                <div
                  key={idx}
                  className={`h-1.5 rounded-full transition-all ${
                    idx === currentTip % 5 ? 'bg-purple-500 w-6' : 'bg-slate-600 w-1.5'
                  }`}
                />
              ))}
            </div>
          </div>
          <p className="text-sm text-gray-300 leading-relaxed">
            {currentSmartTip.text}
          </p>
        </div>

        {/* Debug Info (only in development) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="glass rounded-lg p-3 text-xs border border-slate-700">
            <p className="text-gray-400 mb-2 font-semibold">🔧 Debug Info:</p>
            <div className="space-y-1">
              <p className="text-gray-500 font-mono">User: {userId}</p>
              <p className="text-gray-500 font-mono">
                Status: {error ? '❌ Error' : portfolioLoading ? '⏳ Loading' : '✅ Connected'}
              </p>
              <p className="text-gray-500 font-mono">
                Balance: ${portfolio?.balance.toFixed(2) || '0.00'}
              </p>
              <p className="text-gray-500 font-mono">
                Invested: ${portfolio?.invested.toFixed(2) || '0.00'}
              </p>
              <p className="text-gray-500 font-mono">
                Holdings: {portfolio ? Object.keys(portfolio.holdings).length : 0} coins
              </p>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

// Coin Card Component
function CoinCard({ symbol, data }) {
  const isPositive = data.change_24h >= 0

  return (
    <div className="glass rounded-lg p-3 hover:bg-slate-800/50 transition-all cursor-pointer group">
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
            isPositive ? 'text-green-400' : 'text-red-400'
          }`}>
            {isPositive ? (
              <TrendingUp className="w-4 h-4 mr-1" />
            ) : (
              <TrendingDown className="w-4 h-4 mr-1" />
            )}
            {data.change_24h?.toFixed(2)}%
          </div>
        </div>
      </div>
    </div>
  )
}