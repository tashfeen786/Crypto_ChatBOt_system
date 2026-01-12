'use client'

import { Menu, Settings, User, LogOut } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Navbar({ onMenuClick }) {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [showDropdown, setShowDropdown] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleLogout = async () => {
    setShowDropdown(false)
    await logout()
    // Force redirect to login
    router.push('/login')
    router.refresh()
  }

  // Prevent hydration mismatch
  if (!mounted) return null

  return (
    <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-40">
      <div className="px-4 py-3">
        <div className="flex items-center justify-between">
          
          {/* Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <span className="text-xl">🤖</span>
            </div>
            <div>
              <h1 className="text-lg font-bold gradient-text">Crypto AI Advisor</h1>
              <p className="text-xs text-gray-400">Investment Chatbot</p>
            </div>
          </div>

          {/* Right Actions */}
          <div className="flex items-center space-x-2">
            
            {/* User Profile Button */}
            {user && (
              <div className="relative">
                <button 
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="hidden sm:flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                    <User className="w-4 h-4" />
                  </div>
                  <div className="text-left hidden md:block">
                    <p className="text-sm font-medium text-white">{user?.name || 'User'}</p>
                    <p className="text-xs text-gray-400">
                      ${user?.balance?.toLocaleString() || '0'}
                    </p>
                  </div>
                </button>

                {/* Dropdown Menu */}
                {showDropdown && (
                  <>
                    {/* Backdrop */}
                    <div 
                      className="fixed inset-0 z-40"
                      onClick={() => setShowDropdown(false)}
                    />
                    
                    {/* Dropdown Content */}
                    <div className="absolute right-0 mt-2 w-64 glass rounded-xl shadow-2xl overflow-hidden z-50">
                      <div className="p-4 border-b border-slate-700">
                        <p className="text-white font-semibold">{user?.name || 'User'}</p>
                        <p className="text-sm text-gray-400">{user?.email || ''}</p>
                      </div>
                      
                      <div className="p-2">
                        <div className="px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors">
                          <p className="text-xs text-gray-400">Balance</p>
                          <p className="text-white font-semibold">
                            ${user?.balance?.toLocaleString() || '0'}
                          </p>
                        </div>
                        <div className="px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors">
                          <p className="text-xs text-gray-400">Risk Tolerance</p>
                          <p className="text-white font-semibold">
                            {user?.risk_tolerance || 5}/10 - {(() => {
                              const risk = user?.risk_tolerance || 5;
                              return risk <= 3 ? 'Conservative' :
                                     risk <= 6 ? 'Moderate' :
                                     'Aggressive';
                            })()}
                          </p>
                        </div>
                      </div>
                      
                      <div className="p-2 border-t border-slate-700">
                        <button 
                          onClick={handleLogout}
                          className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-red-500/10 text-red-400 hover:text-red-300 transition-colors"
                        >
                          <LogOut className="w-4 h-4" />
                          <span className="text-sm font-medium">Logout</span>
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Settings Button */}
            <button className="hidden sm:block p-2 rounded-lg hover:bg-slate-800 transition-colors">
              <Settings className="w-5 h-5 text-gray-400" />
            </button>

            {/* Mobile Menu Button */}
            <button
              onClick={onMenuClick}
              className="lg:hidden p-2 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <Menu className="w-5 h-5 text-gray-400" />
            </button>
          </div>

        </div>
      </div>
    </nav>
  )
}