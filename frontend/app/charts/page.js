'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { ArrowLeft, BarChart3, TrendingUp, TrendingDown, DollarSign, Percent, PieChart, Activity } from 'lucide-react'

export default function ChartsPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
    if (user) {
      setLoading(false)
    }
  }, [user, authLoading, router])

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-pulse">
            <BarChart3 className="w-8 h-8" />
          </div>
          <p className="text-white text-lg">Loading charts...</p>
        </div>
      </div>
    )
  }

  if (!user) return null

  // Demo data - Replace with real API calls
  const portfolioData = {
    totalValue: user.balance || 10000,
    totalInvested: 8500,
    profit: 1500,
    profitPercent: 17.65,
    holdings: [
      { coin: 'BTC', amount: 0.15, value: 4200, percent: 42, change: +12.5 },
      { coin: 'ETH', amount: 2.5, value: 3000, percent: 30, change: +8.3 },
      { coin: 'SOL', amount: 50, value: 1500, percent: 15, change: -3.2 },
      { coin: 'ADA', amount: 1000, value: 800, percent: 8, change: +5.7 },
      { coin: 'DOT', amount: 100, value: 500, percent: 5, change: +2.1 }
    ],
    history: [
      { date: '20 Dec', value: 8500 },
      { date: '21 Dec', value: 8700 },
      { date: '22 Dec', value: 8600 },
      { date: '23 Dec', value: 9000 },
      { date: '24 Dec', value: 9200 },
      { date: '25 Dec', value: 9500 },
      { date: '26 Dec', value: 9800 },
      { date: '27 Dec', value: 10200 },
      { date: '28 Dec', value: 10000 },
      { date: '29 Dec', value: 10000 }
    ]
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => router.push('/')}
            className="p-2 glass rounded-xl hover:bg-slate-800 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-400" />
          </button>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
              Portfolio Analytics
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Visualize your crypto investments • {user.name}
            </p>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatsCard
            icon={<DollarSign className="w-5 h-5" />}
            title="Total Value"
            value={`$${portfolioData.totalValue.toLocaleString()}`}
            color="blue"
          />
          <StatsCard
            icon={<TrendingUp className="w-5 h-5" />}
            title="Total Profit"
            value={`$${portfolioData.profit.toLocaleString()}`}
            subtitle={`+${portfolioData.profitPercent}%`}
            color="green"
          />
          <StatsCard
            icon={<Percent className="w-5 h-5" />}
            title="ROI"
            value={`${portfolioData.profitPercent}%`}
            color="purple"
          />
          <StatsCard
            icon={<PieChart className="w-5 h-5" />}
            title="Holdings"
            value={portfolioData.holdings.length}
            subtitle="Coins"
            color="pink"
          />
        </div>

        {/* Main Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Portfolio Value Chart */}
          <div className="lg:col-span-2 glass rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-purple-400" />
                  Portfolio Value
                </h2>
                <p className="text-sm text-gray-400 mt-1">Last 10 days performance</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-white">
                  ${portfolioData.totalValue.toLocaleString()}
                </p>
                <p className="text-sm text-green-400">+${portfolioData.profit.toLocaleString()}</p>
              </div>
            </div>

            {/* Line Chart */}
            <div className="relative h-64">
              <LineChart data={portfolioData.history} />
            </div>
          </div>

          {/* Portfolio Distribution */}
          <div className="glass rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <PieChart className="w-5 h-5 text-pink-400" />
              Distribution
            </h2>
            
            {/* Donut Chart */}
            <div className="mb-6">
              <DonutChart holdings={portfolioData.holdings} />
            </div>

            {/* Legend */}
            <div className="space-y-2">
              {portfolioData.holdings.map((holding, i) => (
                <div key={holding.coin} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: getChartColor(i) }}
                    />
                    <span className="text-sm text-gray-300">{holding.coin}</span>
                  </div>
                  <span className="text-sm font-semibold text-white">{holding.percent}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Holdings Table */}
        <div className="mt-6 glass rounded-2xl p-6">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            Your Holdings
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 text-gray-400 font-semibold text-sm">Coin</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-semibold text-sm">Amount</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-semibold text-sm">Value</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-semibold text-sm">Allocation</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-semibold text-sm">24h Change</th>
                </tr>
              </thead>
              <tbody>
                {portfolioData.holdings.map((holding) => (
                  <tr key={holding.coin} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                          <span className="text-sm font-bold">{holding.coin}</span>
                        </div>
                        <span className="text-white font-semibold">{holding.coin}</span>
                      </div>
                    </td>
                    <td className="text-right py-4 px-4 text-white">{holding.amount}</td>
                    <td className="text-right py-4 px-4 text-white font-semibold">
                      ${holding.value.toLocaleString()}
                    </td>
                    <td className="text-right py-4 px-4">
                      <div className="inline-flex items-center gap-2">
                        <div className="w-20 h-2 bg-slate-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                            style={{ width: `${holding.percent}%` }}
                          />
                        </div>
                        <span className="text-white text-sm">{holding.percent}%</span>
                      </div>
                    </td>
                    <td className="text-right py-4 px-4">
                      <span className={`flex items-center justify-end gap-1 ${
                        holding.change >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {holding.change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                        {Math.abs(holding.change)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper Components
function StatsCard({ icon, title, value, subtitle, color }) {
  const colorClasses = {
    blue: 'from-blue-500 to-cyan-500',
    green: 'from-green-500 to-emerald-500',
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
      {subtitle && <p className="text-sm text-green-400 mt-1">{subtitle}</p>}
    </div>
  )
}

function LineChart({ data }) {
  const max = Math.max(...data.map(d => d.value))
  const min = Math.min(...data.map(d => d.value))
  
  return (
    <div className="w-full h-full flex items-end justify-between gap-2">
      {data.map((point, i) => {
        const height = ((point.value - min) / (max - min)) * 100
        return (
          <div key={i} className="flex-1 flex flex-col items-center group">
            <div className="flex-1 flex items-end w-full">
              <div 
                className="w-full bg-gradient-to-t from-purple-500 to-pink-500 rounded-t-lg transition-all group-hover:opacity-80 cursor-pointer relative"
                style={{ height: `${height}%` }}
              >
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 px-2 py-1 rounded text-xs whitespace-nowrap">
                  ${point.value.toLocaleString()}
                </div>
              </div>
            </div>
            <span className="text-xs text-gray-500 mt-2">{point.date.split(' ')[0]}</span>
          </div>
        )
      })}
    </div>
  )
}

function DonutChart({ holdings }) {
  let currentAngle = 0
  
  return (
    <div className="relative w-48 h-48 mx-auto">
      <svg viewBox="0 0 100 100" className="transform -rotate-90">
        {holdings.map((holding, i) => {
          const percent = holding.percent
          const angle = (percent / 100) * 360
          const startAngle = currentAngle
          const endAngle = currentAngle + angle
          
          const x1 = 50 + 40 * Math.cos((startAngle * Math.PI) / 180)
          const y1 = 50 + 40 * Math.sin((startAngle * Math.PI) / 180)
          const x2 = 50 + 40 * Math.cos((endAngle * Math.PI) / 180)
          const y2 = 50 + 40 * Math.sin((endAngle * Math.PI) / 180)
          
          const largeArc = angle > 180 ? 1 : 0
          
          const pathData = [
            `M 50 50`,
            `L ${x1} ${y1}`,
            `A 40 40 0 ${largeArc} 1 ${x2} ${y2}`,
            `Z`
          ].join(' ')
          
          currentAngle = endAngle
          
          return (
            <path
              key={i}
              d={pathData}
              fill={getChartColor(i)}
              className="hover:opacity-80 transition-opacity cursor-pointer"
            />
          )
        })}
        <circle cx="50" cy="50" r="25" fill="#1e293b" />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{holdings.length}</p>
          <p className="text-xs text-gray-400">Coins</p>
        </div>
      </div>
    </div>
  )
}

function getChartColor(index) {
  const colors = [
    '#8b5cf6', // purple
    '#ec4899', // pink
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // orange
  ]
  return colors[index % colors.length]
}