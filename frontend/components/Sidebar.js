'use client'

import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Wallet, Target, Activity } from 'lucide-react'
import { getCoinPrices } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

export default function Sidebar() {
  const { user } = useAuth()
  const [prices, setPrices] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPrices()
    const interval = setInterval(fetchPrices, 10000) // Update every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchPrices = async () => {
    try {
      const data = await getCoinPrices()
      setPrices(data.prices || {})
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch prices:', error)
      setLoading(false)
    }
  }

  const coins = Object.entries(prices).slice(0, 5)

  // Calculate P&L (dummy for now - will be real when portfolio is implemented)
  const investedAmount = 500
  const currentValue = 550
  const pnl = currentValue - investedAmount
  const pnlPercentage = ((pnl / investedAmount) * 100).toFixed(2)

  return (
    <div className="h-full bg-slate-900/30 backdrop-blur border-l border-slate-800 overflow-y-auto">
      <div className="p-4 space-y-6">
        
        {/* Live Prices Section */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <Activity className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-semibold text-white">Live Prices</h2>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
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
            ) : (
              coins.map(([symbol, data]) => (
                <CoinCard key={symbol} symbol={symbol} data={data} />
              ))
            )}
          </div>
        </div>

        {/* Portfolio Summary */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <Wallet className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-semibold text-white">Portfolio</h2>
          </div>
          
          <div className="glass rounded-xl p-4 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">Balance</span>
              <span className="text-white font-semibold">
                ${user?.balance?.toLocaleString() || '0'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">Invested</span>
              <span className="text-white font-semibold">${investedAmount}</span>
            </div>
            <div className="border-t border-slate-700 pt-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">P&L</span>
                <span className={`font-semibold flex items-center ${
                  pnl >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {pnl >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                  {pnl >= 0 ? '+' : ''}{pnl} ({pnlPercentage}%)
                </span>
              </div>
            </div>
          </div>
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
              <span className="text-purple-400 font-semibold">
                {user?.risk_tolerance || 5}/10
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">Category</span>
              <span className="text-white font-semibold">
                {(user?.risk_tolerance || 5) <= 3 ? 'Conservative' :
                 (user?.risk_tolerance || 5) <= 6 ? 'Moderate' :
                 'Aggressive'}
              </span>
            </div>
            
            {/* Risk Bar */}
            <div className="pt-2">
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                  style={{ width: `${((user?.risk_tolerance || 5) / 10) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Quick Tips */}
        <div className="glass rounded-xl p-4">
          <h3 className="text-sm font-semibold text-white mb-2">💡 Quick Tip</h3>
          <p className="text-xs text-gray-400">
            {user?.risk_tolerance <= 3 
              ? 'Conservative approach! Stable coins jaise BTC aur ETH par focus karo.'
              : user?.risk_tolerance <= 6
              ? 'Diversify karo! Apne portfolio mein multiple coins rakho to risk kam hoga.'
              : 'High risk, high reward! Lekin apne portfolio ka sirf 20% altcoins mein lagao.'
            }
          </p>
        </div>

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