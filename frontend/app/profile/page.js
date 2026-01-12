'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { ArrowLeft, User, Mail, Wallet, Target, LogOut, Loader2, Shield } from 'lucide-react'

export default function ProfilePage() {
  const router = useRouter()
  const { user, logout, loading, refreshUserData } = useAuth()
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    }
  }, [user, loading, router])

  const handleLogout = () => {
    if (confirm('Are you sure you want to logout?')) {
      console.log('🚪 User clicked logout')
      logout()
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await refreshUserData()
    setRefreshing(false)
  }

  if (loading || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-purple-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/')}
            className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors mb-4 group"
          >
            <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
            <span>Back to Dashboard</span>
          </button>
          <h1 className="text-4xl font-bold text-white mb-2">My Profile</h1>
          <p className="text-gray-400">Manage your account settings</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Profile Info */}
          <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Account Information</h2>
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
              >
                {refreshing ? 'Refreshing...' : ''}
              </button>
            </div>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <User className="w-5 h-5 text-purple-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-400">Username</p>
                  <p className="text-white font-semibold">{user.username || 'N/A'}</p>
                </div>
              </div>

              {user.full_name && (
                <div className="flex items-start space-x-3">
                  <User className="w-5 h-5 text-purple-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-400">Full Name</p>
                    <p className="text-white font-semibold">{user.full_name}</p>
                  </div>
                </div>
              )}

              <div className="flex items-start space-x-3">
                <Mail className="w-5 h-5 text-purple-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-400">Email</p>
                  <p className="text-white font-semibold">{user.email}</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Wallet className="w-5 h-5 text-green-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-400">Balance</p>
                  <p className="text-green-400 font-bold text-2xl">
                    ${user.balance?.toFixed(2) || '0.00'}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Target className="w-5 h-5 text-purple-400 mt-1" />
                <div className="w-full">
                  <p className="text-sm text-gray-400 mb-2">Risk Tolerance</p>
                  <div className="flex items-center space-x-3">
                    <div className="flex-1 bg-slate-700 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                        style={{ width: `${(user.risk_tolerance || 5) * 10}%` }}
                      />
                    </div>
                    <span className="text-purple-400 font-semibold">
                      {user.risk_tolerance || 5}/10
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {user.risk_tolerance <= 3 ? 'Conservative' : user.risk_tolerance <= 6 ? 'Moderate' : 'Aggressive'}
                  </p>
                </div>
              </div>

              {user.created_at && (
                <div className="flex items-start space-x-3">
                  <Shield className="w-5 h-5 text-purple-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-400">Member Since</p>
                    <p className="text-white font-semibold">
                      {new Date(user.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6">
              <h2 className="text-xl font-bold text-white mb-4">Quick Stats</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">User ID</span>
                  <span className="text-white font-mono">#{user.id}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Status</span>
                  <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold">
                    Active
                  </span>
                </div>
              </div>
            </div>

            {/* Portfolio */}
            {user.portfolio && user.portfolio.length > 0 && (
              <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6">
                <h2 className="text-xl font-bold text-white mb-4">Portfolio</h2>
                <div className="space-y-2">
                  {user.portfolio.map((holding, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span className="text-gray-400">{holding.symbol}</span>
                      <span className="text-white font-semibold">
                        {holding.amount?.toFixed(4)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Danger Zone */}
            <div className="bg-red-900/20 backdrop-blur rounded-2xl p-6 border border-red-500/30">
              <h2 className="text-xl font-bold text-red-400 mb-4">Danger Zone</h2>
              <p className="text-sm text-gray-400 mb-4">
                Logging out will end your current session. You'll need to login again to access your account.
              </p>
              <button
                onClick={handleLogout}
                className="w-full flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-700 text-white py-3 rounded-xl font-semibold transition-all"
              >
                <LogOut className="w-5 h-5" />
                <span>Logout from Account</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}