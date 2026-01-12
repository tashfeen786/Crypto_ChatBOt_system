'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { ArrowLeft, AlertTriangle, TrendingUp, Bell, Plus, X, Trash2, Edit2, Check } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function AlertsPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [portfolio, setPortfolio] = useState([])
  const [editingAlert, setEditingAlert] = useState(null)
  
  // New alert form
  const [newAlert, setNewAlert] = useState({
    symbol: '',
    target_price: '',
    condition: 'above'
  })

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
    if (user) {
      fetchData()
      const interval = setInterval(fetchData, 30000) // Every 30 seconds
      return () => clearInterval(interval)
    }
  }, [user, authLoading, router])

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      // Fetch portfolio
      const portfolioResponse = await axios.get(
        `${API_URL}/api/portfolio/${user.user_id}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      setPortfolio(portfolioResponse.data.holdings || [])

      // Fetch alerts
      const alertsResponse = await axios.get(
        `${API_URL}/api/alerts/${user.user_id}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      setAlerts(alertsResponse.data.alerts || [])
      
      setLoading(false)
    } catch (err) {
      console.error('Fetch error:', err)
      setLoading(false)
    }
  }

  const createAlert = async () => {
    try {
      if (!newAlert.symbol || !newAlert.target_price) {
        alert('Please fill in all fields')
        return
      }

      const token = localStorage.getItem('access_token')
      await axios.post(
        `${API_URL}/api/alerts/`,
        {
          user_id: user.user_id,
          symbol: newAlert.symbol.toUpperCase(),
          target_price: parseFloat(newAlert.target_price),
          condition: newAlert.condition
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      setShowCreateModal(false)
      setNewAlert({ symbol: '', target_price: '', condition: 'above' })
      fetchData()
    } catch (err) {
      console.error('Create alert error:', err)
      alert('Failed to create alert: ' + (err.response?.data?.detail || err.message))
    }
  }

  const deleteAlert = async (alertId) => {
    try {
      const token = localStorage.getItem('access_token')
      await axios.delete(
        `${API_URL}/api/alerts/${alertId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      fetchData()
    } catch (err) {
      console.error('Delete alert error:', err)
      alert('Failed to delete alert')
    }
  }

  const toggleAlert = async (alertId) => {
    try {
      const token = localStorage.getItem('access_token')
      await axios.post(
        `${API_URL}/api/alerts/${alertId}/toggle`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      fetchData()
    } catch (err) {
      console.error('Toggle alert error:', err)
      alert('Failed to toggle alert')
    }
  }

  const updateAlert = async (alertId, newPrice) => {
    try {
      const token = localStorage.getItem('access_token')
      await axios.put(
        `${API_URL}/api/alerts/${alertId}?target_price=${newPrice}`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      setEditingAlert(null)
      fetchData()
    } catch (err) {
      console.error('Update alert error:', err)
      alert('Failed to update alert')
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Bell className="w-8 h-8" />
          </div>
          <p className="text-white">Loading alerts...</p>
        </div>
      </div>
    )
  }

  if (!user) return null

  const activeAlerts = alerts.filter(a => !a.triggered_at)
  const triggeredAlerts = alerts.filter(a => a.triggered_at)

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
                Price Alerts
              </h1>
              <p className="text-gray-400 text-sm mt-1">Set custom price alerts for your coins</p>
            </div>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white font-semibold hover:shadow-lg hover:shadow-purple-500/50 transition-all flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            New Alert
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="glass rounded-xl p-4">
            <p className="text-gray-400 text-sm">Total Alerts</p>
            <p className="text-2xl font-bold text-white">{alerts.length}</p>
          </div>
          <div className="glass rounded-xl p-4">
            <p className="text-gray-400 text-sm">Active</p>
            <p className="text-2xl font-bold text-green-400">{activeAlerts.length}</p>
          </div>
          <div className="glass rounded-xl p-4">
            <p className="text-gray-400 text-sm">Triggered</p>
            <p className="text-2xl font-bold text-yellow-400">{triggeredAlerts.length}</p>
          </div>
          <div className="glass rounded-xl p-4">
            <p className="text-gray-400 text-sm">Tracked Coins</p>
            <p className="text-2xl font-bold text-blue-400">{new Set(alerts.map(a => a.symbol)).size}</p>
          </div>
        </div>

        {/* Active Alerts */}
        <div className="glass rounded-2xl p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-white">Active Alerts</h2>
            <span className="px-3 py-1 bg-green-500/20 rounded-full text-green-300 text-sm">
              {activeAlerts.length} active
            </span>
          </div>

          {activeAlerts.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Bell className="w-8 h-8 text-purple-400" />
              </div>
              <p className="text-gray-400 text-lg mb-2">No Active Alerts</p>
              <p className="text-gray-500 text-sm mb-4">Create your first price alert to get notified</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-6 py-2 bg-purple-500/20 rounded-lg text-purple-300 hover:bg-purple-500/30 transition-colors"
              >
                Create Alert
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {activeAlerts.map((alert) => (
                <div key={alert.id} className="p-4 glass rounded-xl border border-slate-700/50 hover:border-purple-500/30 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-xl ${
                        alert.condition === 'above' ? 'bg-green-500/20' : 'bg-red-500/20'
                      } flex items-center justify-center`}>
                        {alert.condition === 'above' ? (
                          <TrendingUp className="w-6 h-6 text-green-400" />
                        ) : (
                          <AlertTriangle className="w-6 h-6 text-red-400" />
                        )}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-white font-bold text-lg">{alert.symbol}</h3>
                        {editingAlert === alert.id ? (
                          <div className="flex items-center gap-2 mt-1">
                            <input
                              type="number"
                              defaultValue={alert.target_price}
                              className="px-2 py-1 glass rounded text-white text-sm w-32"
                              id={`edit-${alert.id}`}
                            />
                            <button
                              onClick={() => {
                                const newPrice = document.getElementById(`edit-${alert.id}`).value
                                updateAlert(alert.id, parseFloat(newPrice))
                              }}
                              className="p-1 bg-green-500/20 rounded hover:bg-green-500/30"
                            >
                              <Check className="w-4 h-4 text-green-400" />
                            </button>
                            <button
                              onClick={() => setEditingAlert(null)}
                              className="p-1 bg-red-500/20 rounded hover:bg-red-500/30"
                            >
                              <X className="w-4 h-4 text-red-400" />
                            </button>
                          </div>
                        ) : (
                          <p className="text-gray-400 text-sm">
                            Alert when price goes <span className={alert.condition === 'above' ? 'text-green-400' : 'text-red-400'}>
                              {alert.condition}
                            </span> ${parseFloat(alert.target_price).toLocaleString()}
                          </p>
                        )}
                        <p className="text-xs text-gray-500 mt-1">
                          Created: {new Date(alert.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setEditingAlert(alert.id)}
                        className="p-2 glass rounded-lg hover:bg-blue-500/20 text-blue-400 transition-colors"
                        title="Edit price"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => toggleAlert(alert.id)}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          alert.is_active 
                            ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' 
                            : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
                        }`}
                      >
                        {alert.is_active ? 'ON' : 'OFF'}
                      </button>
                      <button
                        onClick={() => deleteAlert(alert.id)}
                        className="p-2 glass rounded-lg hover:bg-red-500/20 text-red-400 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Triggered Alerts */}
        {triggeredAlerts.length > 0 && (
          <div className="glass rounded-2xl p-6 mb-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold text-white">Triggered Alerts</h2>
              <span className="px-3 py-1 bg-yellow-500/20 rounded-full text-yellow-300 text-sm">
                {triggeredAlerts.length} triggered
              </span>
            </div>
            <div className="space-y-3">
              {triggeredAlerts.map((alert) => (
                <div key={alert.id} className="p-4 glass rounded-xl border border-yellow-500/30 bg-yellow-500/5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center">
                        <Check className="w-5 h-5 text-yellow-400" />
                      </div>
                      <div>
                        <h3 className="text-white font-semibold">{alert.symbol}</h3>
                        <p className="text-yellow-400 text-sm">
                          Triggered: Price went {alert.condition} ${parseFloat(alert.target_price).toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(alert.triggered_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => deleteAlert(alert.id)}
                      className="p-2 glass rounded-lg hover:bg-red-500/20 text-red-400 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Add from Portfolio */}
        {portfolio.length > 0 && (
          <div className="glass rounded-2xl p-6">
            <h2 className="text-lg font-bold text-white mb-4">Quick Add from Portfolio</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {portfolio.slice(0, 8).map((holding) => (
                <button
                  key={holding.symbol}
                  onClick={() => {
                    setNewAlert({
                      symbol: holding.symbol,
                      target_price: holding.current_price.toString(),
                      condition: 'above'
                    })
                    setShowCreateModal(true)
                  }}
                  className="p-3 glass rounded-xl hover:bg-slate-800 transition-colors text-left"
                >
                  <p className="text-white font-semibold">{holding.symbol}</p>
                  <p className="text-gray-400 text-sm">${holding.current_price.toLocaleString()}</p>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Create Alert Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass rounded-2xl p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Create Price Alert</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-2 glass rounded-lg hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Coin Symbol</label>
                <input
                  type="text"
                  placeholder="BTC"
                  value={newAlert.symbol}
                  onChange={(e) => setNewAlert({...newAlert, symbol: e.target.value.toUpperCase()})}
                  className="w-full px-4 py-3 glass rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Target Price ($)</label>
                <input
                  type="number"
                  placeholder="45000"
                  value={newAlert.target_price}
                  onChange={(e) => setNewAlert({...newAlert, target_price: e.target.value})}
                  className="w-full px-4 py-3 glass rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Condition</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setNewAlert({...newAlert, condition: 'above'})}
                    className={`p-3 rounded-xl font-semibold transition-colors ${
                      newAlert.condition === 'above'
                        ? 'bg-green-500/20 text-green-400 border-2 border-green-500'
                        : 'glass text-gray-400 border-2 border-transparent'
                    }`}
                  >
                    Above
                  </button>
                  <button
                    onClick={() => setNewAlert({...newAlert, condition: 'below'})}
                    className={`p-3 rounded-xl font-semibold transition-colors ${
                      newAlert.condition === 'below'
                        ? 'bg-red-500/20 text-red-400 border-2 border-red-500'
                        : 'glass text-gray-400 border-2 border-transparent'
                    }`}
                  >
                    Below
                  </button>
                </div>
              </div>

              <button
                onClick={createAlert}
                className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white font-semibold hover:shadow-lg hover:shadow-purple-500/50 transition-all"
              >
                Create Alert
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}