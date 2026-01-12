'use client'

import { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, Loader2 } from 'lucide-react'
import { getPortfolioPerformance } from '@/lib/api'

export default function ChartsPage() {
  const userId = 'user_123'
  const [performance, setPerformance] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPerformance()
  }, [])

  const fetchPerformance = async () => {
    try {
      const data = await getPortfolioPerformance(userId)
      setPerformance(data)
    } catch (error) {
      console.error('Failed to fetch performance:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Portfolio Analytics</h1>
          <p className="text-gray-400">Track your investment performance</p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-12 h-12 text-purple-500 animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">Performance Overview</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Return</span>
                  <span className="text-green-400 font-semibold">
                    +{performance?.total_return?.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Best Performer</span>
                  <span className="text-white font-semibold">{performance?.best_performer}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Worst Performer</span>
                  <span className="text-white font-semibold">{performance?.worst_performer}</span>
                </div>
              </div>
            </div>

            <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6">
              <div className="flex items-center space-x-2 mb-4">
                <TrendingUp className="w-5 h-5 text-purple-400" />
                <h3 className="text-xl font-bold text-white">Growth Metrics</h3>
              </div>
              <p className="text-gray-400 text-sm">
                Advanced charts and analytics will be displayed here.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}