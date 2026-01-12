'use client'

import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Loader2, ArrowLeft, RefreshCw, Search, Wallet, AlertCircle, CheckCircle, XCircle } from 'lucide-react'

const API_URL = 'http://localhost:8000'

export default function TradingPage() {
  const [prices, setPrices] = useState({})
  const [filteredPrices, setFilteredPrices] = useState({})
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCoin, setSelectedCoin] = useState(null)
  const [tradeType, setTradeType] = useState('buy')
  const [amount, setAmount] = useState('')
  const [loading, setLoading] = useState(false)
  const [simulation, setSimulation] = useState(null)
  const [pricesLoading, setPricesLoading] = useState(true)
  const [userBalance, setUserBalance] = useState(0)
  const [riskTolerance, setRiskTolerance] = useState(5)
  const [userId, setUserId] = useState(null)
  const [portfolio, setPortfolio] = useState({})
  const [notification, setNotification] = useState(null)

  // Get user ID from localStorage
  useEffect(() => {
    const rawStoredUserId = localStorage.getItem('user')
    const storedUserId = JSON.parse(rawStoredUserId)?.user_id;
    if (storedUserId) {
      console.log('✅ Trading Page - User ID from localStorage:', storedUserId)
      // Convert to integer if it's a number-like string
      const numericId = parseInt(storedUserId)
      if (!isNaN(numericId)) {
        setUserId(numericId)
      } else {
        // If it's a string like "user_123", extract number or use 1
        const extracted = storedUserId?.match(/\d+/)
        setUserId(extracted ? parseInt(extracted[0]) : 4)
      }
    } else {
      console.log('⚠️ No user ID found, using default ID: 4')
      setUserId(4)  // Use integer 4 instead of "user_123"
    }
  }, [])

  useEffect(() => {
    if (userId) {
      fetchAll()
      const interval = setInterval(fetchPrices, 10000)
      return () => clearInterval(interval)
    }
  }, [userId])

  useEffect(() => {
    // Filter prices based on search query
    if (!searchQuery) {
      setFilteredPrices(prices)
    } else {
      const filtered = {}
      Object.keys(prices).forEach(symbol => {
        if (symbol.toLowerCase().includes(searchQuery.toLowerCase())) {
          filtered[symbol] = prices[symbol]
        }
      })
      setFilteredPrices(filtered)
    }
  }, [searchQuery, prices])

  // Auto-hide notification after 5 seconds
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        setNotification(null)
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [notification])

  const fetchAll = async () => {
    await Promise.all([
      fetchPrices(),
      fetchUserData()
    ])
  }

  const fetchPrices = async () => {
    try {
      console.log('🔄 Fetching prices...')
      const response = await fetch(`${API_URL}/api/trading/prices`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch prices from server')
      }
      
      const data = await response.json()
      setPrices(data.prices || {})
      setFilteredPrices(data.prices || {})
      setPricesLoading(false)
      console.log('✅ Prices fetched:', Object.keys(data.prices || {}).length, 'coins')
    } catch (error) {
      console.error('❌ Failed to fetch prices:', error)
      setPricesLoading(false)
      showNotification('Failed to fetch prices. Please check if backend is running.', 'error')
    }
  }

  const fetchUserData = async () => {
    if (!userId) return
    
    try {
      console.log('🔄 Fetching user data for:', userId)
      const response = await fetch(`${API_URL}/api/users/${userId}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch user data')
      }
      
      const data = await response.json()
      console.log('✅ User data:', data)
      setUserBalance(data.balance || 0)
      setRiskTolerance(data.risk_tolerance || 5)
      setPortfolio(data.portfolio?.holdings || {})
    } catch (error) {
      console.error('❌ Failed to fetch user data:', error)
      showNotification('Failed to fetch user data. Using default values.', 'error')
    }
  }

  const showNotification = (message, type = 'success') => {
    // Handle error objects from API
    let displayMessage = message
    if (typeof message === 'object') {
      // If it's an error object from FastAPI
      if (message.detail) {
        if (typeof message.detail === 'string') {
          displayMessage = message.detail
        } else if (Array.isArray(message.detail)) {
          // FastAPI validation errors come as array
          displayMessage = message.detail.map(err => {
            if (err.msg) return err.msg
            if (err.type) return `Validation error: ${err.type}`
            return JSON.stringify(err)
          }).join(', ')
        } else if (message.detail.msg) {
          displayMessage = message.detail.msg
        } else {
          displayMessage = JSON.stringify(message.detail)
        }
      } else if (message.msg) {
        displayMessage = message.msg
      } else if (message.message) {
        displayMessage = message.message
      } else {
        displayMessage = 'An error occurred'
      }
    }
    setNotification({ message: String(displayMessage), type })
  }

  const handleSimulate = async () => {
    if (!selectedCoin || !amount || !userId) return
    
    try {
      setLoading(true)
      
      const endpoint = tradeType === 'buy' 
        ? '/api/trading/simulate-buy'
        : '/api/trading/simulate-sell'
      
      const body = tradeType === 'buy'
        ? { user_id: userId, symbol: selectedCoin, amount_usd: parseFloat(amount) }
        : { user_id: userId, symbol: selectedCoin, amount_coins: parseFloat(amount) }
      
      console.log('🧪 Simulating trade:', { endpoint, body })
      
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      
      const data = await response.json()
      console.log('📥 Simulation response:', { status: response.status, data })
      
      if (response.ok && data.simulation) {
        setSimulation(data.simulation)
        showNotification('Simulation successful!', 'success')
      } else {
        // Handle error response properly
        console.error('❌ Simulation failed:', data)
        showNotification(data, 'error')
      }
    } catch (error) {
      console.error('❌ Simulation error:', error)
      showNotification('Simulation failed: ' + error.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleTrade = async () => {
    if (!selectedCoin || !amount || !userId) return
    
    // Check if user has enough holdings for sell
    if (tradeType === 'sell') {
      const currentHolding = portfolio[selectedCoin] || 0
      if (parseFloat(amount) > currentHolding) {
        showNotification(`You only have ${currentHolding.toFixed(8)} ${selectedCoin}`, 'error')
        return
      }
    }
    
    try {
      setLoading(true)
      console.log('💰 Executing trade:', { userId, tradeType, selectedCoin, amount })
      
      const endpoint = tradeType === 'buy' ? '/api/trading/buy' : '/api/trading/sell'
      const body = tradeType === 'buy' 
        ? { user_id: userId, symbol: selectedCoin, amount_usd: parseFloat(amount) }
        : { user_id: userId, symbol: selectedCoin, amount_coins: parseFloat(amount) }
      
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      
      const data = await response.json()
      console.log('✅ Trade result:', data)
      
      if (response.ok && data.status === 'success') {
        showNotification(data.message, 'success')
        setUserBalance(data.updated_balance)
        setAmount('')
        setSimulation(null)
        // Refresh user data after trade
        fetchUserData()
      } else {
        // Handle error response properly
        const errorMsg = data.detail || data.message || 'Trade failed'
        showNotification(errorMsg, 'error')
      }
    } catch (error) {
      console.error('❌ Trade error:', error)
      showNotification('Trade failed: ' + error.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const displayedCoins = Object.entries(filteredPrices).slice(0, 100)
  const totalCoins = Object.keys(prices).length
  const currentHolding = selectedCoin ? (portfolio[selectedCoin] || 0) : 0

  // Calculate portfolio value
  const portfolioValue = Object.entries(portfolio).reduce((sum, [symbol, amount]) => {
    const price = prices[symbol] || 0
    return sum + (amount * price)
  }, 0)

  // Show loading while getting user ID
  if (!userId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-purple-500 animate-spin mx-auto mb-4" />
          <p className="text-white">Loading user data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      {/* Notification Toast */}
      {notification && (
        <div className="fixed top-4 right-4 z-50 animate-slide-down">
          <div className={`flex items-center space-x-3 px-6 py-4 rounded-xl shadow-2xl backdrop-blur ${
            notification.type === 'success' 
              ? 'bg-green-900/90 border border-green-500/50' 
              : 'bg-red-900/90 border border-red-500/50'
          }`}>
            {notification.type === 'success' ? (
              <CheckCircle className="w-5 h-5 text-green-400" />
            ) : (
              <XCircle className="w-5 h-5 text-red-400" />
            )}
            <p className="text-white font-medium">{notification.message}</p>
            <button 
              onClick={() => setNotification(null)}
              className="text-gray-400 hover:text-white"
            >
              ×
            </button>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <button
            onClick={() => window.history.back()}
            className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors mb-4 group"
          >
            <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
            <span>Back to Chat</span>
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Trading Dashboard</h1>
              <p className="text-gray-400">Buy and sell cryptocurrencies • Powered by Binance</p>
            </div>
            <button
              onClick={fetchAll}
              disabled={loading}
              className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-xl transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Trade Type Selection */}
            <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6">
              <div className="flex space-x-4 mb-6">
                <button
                  onClick={() => {
                    setTradeType('buy')
                    setSimulation(null)
                    setAmount('')
                  }}
                  className={`flex-1 py-3 rounded-xl font-semibold transition-all ${
                    tradeType === 'buy'
                      ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white'
                      : 'bg-slate-700 text-gray-400 hover:bg-slate-600'
                  }`}
                >
                  Buy
                </button>
                <button
                  onClick={() => {
                    setTradeType('sell')
                    setSimulation(null)
                    setAmount('')
                  }}
                  className={`flex-1 py-3 rounded-xl font-semibold transition-all ${
                    tradeType === 'sell'
                      ? 'bg-gradient-to-r from-red-600 to-rose-600 text-white'
                      : 'bg-slate-700 text-gray-400 hover:bg-slate-600'
                  }`}
                >
                  Sell
                </button>
              </div>

              {/* Search Bar */}
              <div className="mb-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder={`Search from ${totalCoins} coins...`}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-slate-700 text-white rounded-xl pl-10 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              {pricesLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
                </div>
              ) : displayedCoins.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  No coins found matching "{searchQuery}"
                </div>
              ) : (
                <>
                  <p className="text-sm text-gray-400 mb-3">
                    Showing {displayedCoins.length} of {totalCoins} coins
                    {searchQuery && ` • Filtered by "${searchQuery}"`}
                  </p>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                    {displayedCoins.map(([symbol, price]) => {
                      const hasHolding = portfolio[symbol] > 0
                      return (
                        <button
                          key={symbol}
                          onClick={() => {
                            setSelectedCoin(symbol)
                            setSimulation(null)
                            setAmount('')
                          }}
                          className={`p-4 rounded-xl transition-all relative ${
                            selectedCoin === symbol
                              ? 'bg-gradient-to-r from-purple-600 to-pink-600 scale-105'
                              : 'bg-slate-700 hover:bg-slate-600'
                          }`}
                        >
                          {hasHolding && (
                            <div className="absolute top-1 right-1 w-2 h-2 bg-green-400 rounded-full"></div>
                          )}
                          <div className="text-left">
                            <p className="font-bold text-white">{symbol}</p>
                            <p className="text-sm text-gray-300">${price?.toFixed(8)}</p>
                            {hasHolding && (
                              <p className="text-xs text-green-400 mt-1">
                                {portfolio[symbol].toFixed(8)}
                              </p>
                            )}
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </>
              )}
            </div>

            {/* Trade Form */}
            {selectedCoin && (
              <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-white">
                    {tradeType === 'buy' ? 'Buy' : 'Sell'} {selectedCoin}
                  </h3>
                  <div className="text-right">
                    <p className="text-xs text-gray-400">Current Price</p>
                    <p className="text-sm font-semibold text-white">
                      ${prices[selectedCoin]?.toFixed(8)}
                    </p>
                  </div>
                </div>

                {/* Show current holding for sell */}
                {tradeType === 'sell' && (
                  <div className="bg-slate-700/50 rounded-lg p-3 mb-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Your Holdings</span>
                      <span className="text-white font-semibold">
                        {currentHolding.toFixed(8)} {selectedCoin}
                      </span>
                    </div>
                    {currentHolding === 0 && (
                      <p className="text-xs text-red-400 mt-2">
                        ⚠️ You don't have any {selectedCoin} to sell
                      </p>
                    )}
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">
                      {tradeType === 'buy' ? 'Amount (USD)' : `Amount (${selectedCoin})`}
                    </label>
                    <input
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      placeholder={`Enter amount${tradeType === 'sell' && currentHolding > 0 ? ` (Max: ${currentHolding.toFixed(8)})` : ''}`}
                      className="w-full bg-slate-700 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      step="0.00000001"
                      max={tradeType === 'sell' ? currentHolding : undefined}
                    />
                    {tradeType === 'sell' && currentHolding > 0 && (
                      <div className="flex gap-2 mt-2">
                        <button
                          onClick={() => setAmount((currentHolding * 0.25).toString())}
                          className="flex-1 text-xs bg-slate-600 hover:bg-slate-500 text-white py-1 rounded"
                        >
                          25%
                        </button>
                        <button
                          onClick={() => setAmount((currentHolding * 0.5).toString())}
                          className="flex-1 text-xs bg-slate-600 hover:bg-slate-500 text-white py-1 rounded"
                        >
                          50%
                        </button>
                        <button
                          onClick={() => setAmount((currentHolding * 0.75).toString())}
                          className="flex-1 text-xs bg-slate-600 hover:bg-slate-500 text-white py-1 rounded"
                        >
                          75%
                        </button>
                        <button
                          onClick={() => setAmount(currentHolding.toString())}
                          className="flex-1 text-xs bg-slate-600 hover:bg-slate-500 text-white py-1 rounded"
                        >
                          100%
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={handleSimulate}
                      disabled={loading || !amount || (tradeType === 'sell' && currentHolding === 0)}
                      className="flex-1 bg-slate-600 hover:bg-slate-500 text-white py-3 rounded-xl font-semibold disabled:opacity-50 transition-all flex items-center justify-center space-x-2"
                    >
                      {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
                      <span>Simulate</span>
                    </button>
                    <button
                      onClick={handleTrade}
                      disabled={loading || !amount || (tradeType === 'sell' && currentHolding === 0)}
                      className={`flex-1 ${
                        tradeType === 'buy'
                          ? 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700'
                          : 'bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700'
                      } text-white py-3 rounded-xl font-semibold disabled:opacity-50 transition-all flex items-center justify-center space-x-2`}
                    >
                      {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
                      <span>{tradeType === 'buy' ? 'Buy Now' : 'Sell Now'}</span>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* Account Balance */}
            <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Wallet className="w-5 h-5 text-purple-400" />
                Account Balance
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Available</span>
                  <span className="text-white font-bold text-lg">${userBalance?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Portfolio Value</span>
                  <span className="text-purple-400 font-semibold">${portfolioValue.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Assets</span>
                  <span className="text-green-400 font-bold">${(userBalance + portfolioValue).toFixed(2)}</span>
                </div>
                <div className="border-t border-slate-700 pt-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Risk Level</span>
                    <span className="text-purple-400 font-semibold">{riskTolerance}/10</span>
                  </div>
                </div>
                <div className="pt-2 border-t border-slate-700">
                  <p className="text-xs text-gray-500">User ID: {userId}</p>
                </div>
              </div>
            </div>

            {/* Portfolio Holdings */}
            {Object.keys(portfolio).length > 0 && (
              <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4">Your Holdings</h3>
                <div className="space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
                  {Object.entries(portfolio).map(([symbol, amount]) => {
                    const currentPrice = prices[symbol] || 0
                    const value = amount * currentPrice
                    return (
                      <div key={symbol} className="flex justify-between items-center bg-slate-700/50 rounded-lg p-3">
                        <div>
                          <p className="font-semibold text-white">{symbol}</p>
                          <p className="text-xs text-gray-400">{amount.toFixed(8)}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-semibold text-white">${value.toFixed(2)}</p>
                          <p className="text-xs text-gray-400">${currentPrice.toFixed(8)}</p>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Simulation Results */}
            {simulation && (
              <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4">Simulation Results</h3>
                <div className="space-y-3">
                  {tradeType === 'buy' ? (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Coins Received</span>
                        <span className="text-white font-semibold">{simulation.coins_received?.toFixed(8)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Price</span>
                        <span className="text-white font-semibold">${simulation.current_price?.toFixed(8)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Fee (0.1%)</span>
                        <span className="text-yellow-400 font-semibold">${simulation.fee?.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Total Cost</span>
                        <span className="text-white font-semibold">${simulation.total_cost?.toFixed(2)}</span>
                      </div>
                      <div className="border-t border-slate-600 pt-3">
                        <div className="flex justify-between">
                          <span className="text-gray-400">New Balance</span>
                          <span className={`font-semibold ${
                            simulation.can_afford ? 'text-green-400' : 'text-red-400'
                          }`}>
                            ${simulation.impact?.new_balance?.toFixed(2)}
                          </span>
                        </div>
                        {!simulation.can_afford && (
                          <div className="mt-2 p-2 bg-red-900/30 rounded-lg">
                            <p className="text-xs text-red-400 flex items-center gap-1">
                              <AlertCircle className="w-3 h-3" />
                              Insufficient balance
                            </p>
                          </div>
                        )}
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-400">USD Received</span>
                        <span className="text-green-400 font-semibold">${simulation.usd_received?.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Price</span>
                        <span className="text-white font-semibold">${simulation.current_price?.toFixed(8)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Fee (0.1%)</span>
                        <span className="text-yellow-400 font-semibold">${simulation.fee?.toFixed(2)}</span>
                      </div>
                      <div className="border-t border-slate-600 pt-3">
                        <div className="flex justify-between">
                          <span className="text-gray-400">New Balance</span>
                          <span className="text-green-400 font-semibold">
                            ${simulation.impact?.new_balance?.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Info Card */}
            <div className="bg-gradient-to-br from-purple-900/50 to-pink-900/50 backdrop-blur rounded-2xl p-6 border border-purple-500/30">
              <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Live Data
              </h3>
              <p className="text-xs text-gray-300">
                All prices are fetched live from Binance API. {totalCoins}+ coins available for trading with real-time updates.
              </p>
            </div>

            {/* Debug Info (Development only) */}
            {process.env.NODE_ENV === 'development' && (
              <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-4 border border-slate-700">
                <h3 className="text-xs font-semibold text-gray-400 mb-2">🔧 Debug Info</h3>
                <div className="space-y-1 text-xs text-gray-500 font-mono">
                  <p>User ID: {userId}</p>
                  <p>Balance: ${userBalance.toFixed(2)}</p>
                  <p>Holdings: {Object.keys(portfolio).length} coins</p>
                  {selectedCoin && (
                    <>
                      <p className="pt-2 border-t border-slate-700 mt-2">Selected: {selectedCoin}</p>
                      <p>Type: {tradeType}</p>
                      <p>Amount: {amount || 'N/A'}</p>
                      {tradeType === 'sell' && (
                        <p>Your {selectedCoin}: {(portfolio[selectedCoin] || 0).toFixed(8)}</p>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #1e293b;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #475569;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #64748b;
        }
        @keyframes slide-down {
          from {
            transform: translateY(-100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        .animate-slide-down {
          animation: slide-down 0.3s ease-out;
        }
      `}</style>
    </div>
  )
}