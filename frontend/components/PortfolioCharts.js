'use client'

import { PieChart, Pie, Cell, LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, DollarSign, Percent, PieChart as PieChartIcon, Activity } from 'lucide-react'

export default function PortfolioCharts({ userProfile }) {
  // Sample portfolio data (replace with real data from API later)
  const portfolioData = [
    { name: 'BTC', value: 40, amount: 400, profit: 50, color: '#F7931A' },
    { name: 'ETH', value: 30, amount: 300, profit: 30, color: '#627EEA' },
    { name: 'SOL', value: 20, amount: 200, profit: -10, color: '#14F195' },
    { name: 'ADA', value: 10, amount: 100, profit: 5, color: '#0033AD' },
  ]

  const timelineData = [
    { date: 'Jan', value: 800 },
    { date: 'Feb', value: 850 },
    { date: 'Mar', value: 900 },
    { date: 'Apr', value: 920 },
    { date: 'May', value: 1000 },
  ]

  const totalValue = portfolioData.reduce((sum, item) => sum + item.amount, 0)
  const totalProfit = portfolioData.reduce((sum, item) => sum + item.profit, 0)
  const totalInvested = totalValue - totalProfit
  const roi = ((totalProfit / totalInvested) * 100).toFixed(2)

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={<DollarSign className="w-5 h-5" />}
          label="Total Value"
          value={`$${totalValue.toLocaleString()}`}
          color="text-blue-400"
        />
        <StatCard
          icon={<TrendingUp className="w-5 h-5" />}
          label="Total Profit"
          value={`$${totalProfit}`}
          color={totalProfit >= 0 ? "text-green-400" : "text-red-400"}
        />
        <StatCard
          icon={<Percent className="w-5 h-5" />}
          label="ROI"
          value={`${roi}%`}
          color={totalProfit >= 0 ? "text-green-400" : "text-red-400"}
        />
        <StatCard
          icon={<Activity className="w-5 h-5" />}
          label="Invested"
          value={`$${totalInvested}`}
          color="text-purple-400"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Donut Chart - Portfolio Allocation */}
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <PieChartIcon className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-bold text-white">Portfolio Allocation</h3>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={portfolioData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={5}
                dataKey="value"
              >
                {portfolioData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid rgba(148, 163, 184, 0.1)',
                  borderRadius: '12px',
                  color: 'white'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-2 mt-4">
            {portfolioData.map((item, i) => (
              <div key={i} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-sm text-gray-300">{item.name}: {item.value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bar Chart - P&L by Coin */}
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-bold text-white">Profit & Loss</h3>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={portfolioData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid rgba(148, 163, 184, 0.1)',
                  borderRadius: '12px',
                  color: 'white'
                }}
              />
              <Bar dataKey="profit" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Line Chart - Value Over Time */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-bold text-white">Portfolio Value Over Time</h3>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timelineData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" />
            <XAxis dataKey="date" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                border: '1px solid rgba(148, 163, 184, 0.1)',
                borderRadius: '12px',
                color: 'white'
              }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#8b5cf6"
              strokeWidth={3}
              dot={{ fill: '#8b5cf6', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, color }) {
  return (
    <div className="glass rounded-xl p-4 hover:bg-slate-800/50 transition-all">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{label}</span>
        <div className={color}>{icon}</div>
      </div>
      <p className="text-xl font-bold text-white">{value}</p>
    </div>
  )
}