'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, TrendingUp, TrendingDown, DollarSign, BarChart3, RefreshCw, AlertCircle } from 'lucide-react'

const API_URL = 'http://localhost:8000'

export default function PortfolioPage() {
  const router = useRouter()
  const [userId, setUserId] = useState(null)
  const [portfolio, setPortfolio] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Get user ID from localStorage (same as trading page)
  useEffect(() => {
    
    const rawStoredUserId = localStorage.getItem('user')
    const storedUserId = JSON.parse(rawStoredUserId)?.user_id;
    if (storedUserId) {
      const numericId = parseInt(storedUserId)
      if (!isNaN(numericId)) {
        setUserId(numericId)
      } else {
        const extracted = storedUserId.match(/\d+/)
        setUserId(extracted ? parseInt(extracted[0]) : 1)
      }
    } else {
      setUserId(1) // Default user ID
    }
  }, [])

  useEffect(() => {
    if (userId) {
      fetchPortfolio()
    }
  }, [userId])

  const fetchPortfolio = async () => {
    try {
      setLoading(true)
      setError('')
      
      console.log('🔄 Fetching portfolio for user:', userId)
      
      const response = await fetch(`${API_URL}/api/portfolio/${userId}`)
      
      if (!response.ok) {
        throw new Error(`Failed to load portfolio: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('✅ Portfolio data:', data)
      
      setPortfolio(data)
      setLoading(false)
    } catch (err) {
      console.error('❌ Portfolio fetch error:', err)
      setError('Failed to load portfolio. Please try again.')
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-pulse">
            <BarChart3 className="w-8 h-8 text-white" />
          </div>
          <p className="text-white text-lg">Loading portfolio...</p>
          <p className="text-gray-400 text-sm mt-2">Fetching your holdings</p>
        </div>
      </div>
    )
  }

  const holdings = portfolio?.holdings || []
  const totalInvested = portfolio?.total_invested || 0
  const totalValue = portfolio?.total_current_value || 0
  const totalPnL = portfolio?.total_profit_loss || 0
  const pnlPercent = portfolio?.total_profit_loss_percent || 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/')}
              className="p-2 glass rounded-xl hover:bg-slate-800 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400" />
            </button>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                Your Portfolio
              </h1>
              <p className="text-gray-400 text-sm mt-1">Track your crypto investments</p>
            </div>
          </div>
          
          <button
            onClick={fetchPortfolio}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-red-400 font-semibold">{error}</p>
              <button
                onClick={fetchPortfolio}
                className="text-sm text-red-300 underline mt-1 hover:text-red-200"
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            icon={<DollarSign className="w-5 h-5" />}
            title="Total Value"
            value={`$${totalValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`}
            color="blue"
          />
          <StatCard
            icon={<DollarSign className="w-5 h-5" />}
            title="Total Invested"
            value={`$${totalInvested.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`}
            color="purple"
          />
          <StatCard
            icon={totalPnL >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
            title="P&L"
            value={`${totalPnL >= 0 ? '+' : ''}$${Math.abs(totalPnL).toFixed(2)}`}
            subtitle={`${pnlPercent >= 0 ? '+' : ''}${pnlPercent.toFixed(2)}%`}
            color={totalPnL >= 0 ? "green" : "red"}
          />
          <StatCard
            icon={<BarChart3 className="w-5 h-5" />}
            title="Holdings"
            value={holdings.length}
            subtitle={holdings.length === 1 ? "Coin" : "Coins"}
            color="pink"
          />
        </div>

        {/* Holdings Table */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-xl font-bold text-white mb-6">Your Holdings</h2>
          
          {holdings.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-10 h-10 text-purple-400" />
              </div>
              <p className="text-gray-400 text-lg mb-2">No holdings yet</p>
              <p className="text-gray-500 text-sm mb-6">Start investing to build your portfolio</p>
              <button
                onClick={() => router.push('/trading')}
                className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-semibold hover:shadow-lg hover:scale-105 transition-all"
              >
                Start Trading
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-gray-400 text-sm font-semibold">Coin</th>
                    <th className="text-right py-3 px-4 text-gray-400 text-sm font-semibold">Quantity</th>
                    <th className="text-right py-3 px-4 text-gray-400 text-sm font-semibold">Avg Buy</th>
                    <th className="text-right py-3 px-4 text-gray-400 text-sm font-semibold">Current Price</th>
                    <th className="text-right py-3 px-4 text-gray-400 text-sm font-semibold">Total Value</th>
                    <th className="text-right py-3 px-4 text-gray-400 text-sm font-semibold">P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {holdings.map((holding, i) => {
                    const pnl = holding.profit_loss || 0
                    const pnlPercent = holding.profit_loss_percent || 0
                    
                    return (
                      <tr key={i} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                        <td className="py-4 px-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                              <span className="text-sm font-bold text-white">{holding.symbol.substring(0, 3)}</span>
                            </div>
                            <span className="text-white font-semibold">{holding.symbol}</span>
                          </div>
                        </td>
                        <td className="text-right py-4 px-4 text-white font-mono">
                          {holding.quantity.toFixed(8)}
                        </td>
                        <td className="text-right py-4 px-4 text-white">
                          ${holding.avg_buy_price.toFixed(2)}
                        </td>
                        <td className="text-right py-4 px-4 text-white">
                          ${(holding.current_price || 0).toFixed(2)}
                        </td>
                        <td className="text-right py-4 px-4 text-white font-semibold">
                          ${(holding.current_value || 0).toFixed(2)}
                        </td>
                        <td className="text-right py-4 px-4">
                          <div className={`flex flex-col items-end gap-1`}>
                            <div className={`flex items-center gap-1 font-semibold ${
                              pnl >= 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                              {pnl >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                              <span>
                                {pnl >= 0 ? '+' : ''}${Math.abs(pnl).toFixed(2)}
                              </span>
                            </div>
                            <span className={`text-sm ${
                              pnl >= 0 ? 'text-green-400/80' : 'text-red-400/80'
                            }`}>
                              ({pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%)
                            </span>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Debug Info (Development) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="glass rounded-lg p-4 mt-6">
            <p className="text-xs text-gray-500 mb-2">🔧 Debug Info:</p>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div>
                <span className="text-gray-400">User ID:</span>
                <span className="text-white ml-2">{userId}</span>
              </div>
              <div>
                <span className="text-gray-400">Holdings:</span>
                <span className="text-white ml-2">{holdings.length}</span>
              </div>
              <div>
                <span className="text-gray-400">Total Value:</span>
                <span className="text-white ml-2">${totalValue.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-gray-400">Status:</span>
                <span className={`ml-2 ${error ? 'text-red-400' : loading ? 'text-yellow-400' : 'text-green-400'}`}>
                  {error ? 'Error' : loading ? 'Loading' : 'Success'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({ icon, title, value, subtitle, color }) {
  const colorClasses = {
    blue: 'from-blue-500 to-cyan-500',
    green: 'from-green-500 to-emerald-500',
    red: 'from-red-500 to-rose-500',
    purple: 'from-purple-500 to-pink-500',
    pink: 'from-pink-500 to-rose-500'
  }

  return (
    <div className="glass rounded-xl p-4 hover:bg-slate-800/50 transition-all">
      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center mb-3`}>
        {icon}
      </div>
      <p className="text-gray-400 text-sm mb-1">{title}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
      {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
    </div>
  )
}