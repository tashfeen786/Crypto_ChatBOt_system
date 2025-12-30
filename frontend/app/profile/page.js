'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import { User, Wallet, Target, Shield, ArrowLeft, Save } from 'lucide-react'

export default function ProfilePage() {
  const router = useRouter()
  const [saving, setSaving] = useState(false)
  
  const [profile, setProfile] = useState({
    name: 'User',
    email: 'user@example.com',
    balance: 1000,
    riskTolerance: 5,
    investmentGoal: 'Long-term Growth',
    experience: 'Beginner'
  })

  const handleSave = async () => {
    setSaving(true)
    
    // Save to localStorage for now (backend integration baad mein)
    localStorage.setItem('userProfile', JSON.stringify(profile))
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    setSaving(false)
    alert('Profile saved successfully! ✅')
  }

  const riskLevels = [
    { value: 1, label: 'Very Low', color: 'text-green-400' },
    { value: 3, label: 'Low', color: 'text-green-300' },
    { value: 5, label: 'Moderate', color: 'text-yellow-400' },
    { value: 7, label: 'High', color: 'text-orange-400' },
    { value: 10, label: 'Very High', color: 'text-red-400' }
  ]

  const currentRiskLabel = riskLevels.find(r => r.value === profile.riskTolerance)

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <Navbar onMenuClick={() => {}} />
      
      <div className="flex-1 overflow-y-auto p-4 md:p-8">
        <div className="max-w-4xl mx-auto">
          
          {/* Header */}
          <div className="flex items-center space-x-4 mb-8">
            <button
              onClick={() => router.push('/')}
              className="p-2 glass rounded-xl hover:bg-slate-800 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400" />
            </button>
            <div>
              <h1 className="text-3xl font-bold gradient-text">Profile Settings</h1>
              <p className="text-gray-400 text-sm mt-1">Apni details update karo</p>
            </div>
          </div>

          {/* Profile Card */}
          <div className="glass rounded-2xl p-6 md:p-8 space-y-8">
            
            {/* Personal Info */}
            <div>
              <div className="flex items-center space-x-3 mb-6">
                <User className="w-6 h-6 text-purple-400" />
                <h2 className="text-xl font-semibold text-white">Personal Information</h2>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Name</label>
                  <input
                    type="text"
                    value={profile.name}
                    onChange={(e) => setProfile({...profile, name: e.target.value})}
                    className="w-full bg-slate-800 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Your name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Email</label>
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({...profile, email: e.target.value})}
                    className="w-full bg-slate-800 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="your@email.com"
                  />
                </div>
              </div>
            </div>

            {/* Financial Info */}
            <div>
              <div className="flex items-center space-x-3 mb-6">
                <Wallet className="w-6 h-6 text-purple-400" />
                <h2 className="text-xl font-semibold text-white">Financial Details</h2>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Balance (USD)</label>
                  <input
                    type="number"
                    value={profile.balance}
                    onChange={(e) => setProfile({...profile, balance: parseFloat(e.target.value)})}
                    className="w-full bg-slate-800 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="1000"
                  />
                  <p className="text-xs text-gray-500 mt-1">Investment ke liye available amount</p>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Experience Level</label>
                  <select
                    value={profile.experience}
                    onChange={(e) => setProfile({...profile, experience: e.target.value})}
                    className="w-full bg-slate-800 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="Beginner">Beginner - Naya investor</option>
                    <option value="Intermediate">Intermediate - Kuch experience hai</option>
                    <option value="Advanced">Advanced - Expert level</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Risk Tolerance */}
            <div>
              <div className="flex items-center space-x-3 mb-6">
                <Target className="w-6 h-6 text-purple-400" />
                <h2 className="text-xl font-semibold text-white">Risk Profile</h2>
              </div>
              
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <label className="text-sm text-gray-400">Risk Tolerance</label>
                    <span className={`text-lg font-semibold ${currentRiskLabel?.color}`}>
                      {profile.riskTolerance}/10 - {currentRiskLabel?.label}
                    </span>
                  </div>
                  
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={profile.riskTolerance}
                    onChange={(e) => setProfile({...profile, riskTolerance: parseInt(e.target.value)})}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
                    style={{
                      background: `linear-gradient(to right, #8b5cf6 0%, #ec4899 ${profile.riskTolerance * 10}%, #1e293b ${profile.riskTolerance * 10}%, #1e293b 100%)`
                    }}
                  />
                  
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>Conservative (Kam risk)</span>
                    <span>Aggressive (Zyada risk)</span>
                  </div>
                </div>

                <div className="glass rounded-xl p-4 bg-slate-800/30">
                  <div className="flex items-start space-x-3">
                    <Shield className="w-5 h-5 text-purple-400 mt-0.5" />
                    <div className="text-sm text-gray-300">
                      <strong className="text-white">Risk ka matlab:</strong>
                      <ul className="mt-2 space-y-1 text-gray-400">
                        <li>• <strong>Low (1-3):</strong> Safe coins (BTC, ETH), stable returns</li>
                        <li>• <strong>Moderate (4-6):</strong> Mix of safe + growth coins</li>
                        <li>• <strong>High (7-10):</strong> Aggressive, altcoins, high volatility</li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Investment Goal</label>
                  <select
                    value={profile.investmentGoal}
                    onChange={(e) => setProfile({...profile, investmentGoal: e.target.value})}
                    className="w-full bg-slate-800 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="Short-term Gains">Short-term - Quick profit (1-3 months)</option>
                    <option value="Medium-term Growth">Medium-term - Growth (3-12 months)</option>
                    <option value="Long-term Growth">Long-term - HODL (1+ years)</option>
                    <option value="Passive Income">Passive Income - Staking/Yield</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex items-center justify-end space-x-4 pt-6 border-t border-slate-700">
              <button
                onClick={() => router.push('/')}
                className="px-6 py-3 rounded-xl bg-slate-800 text-white hover:bg-slate-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 transition-all flex items-center space-x-2"
              >
                {saving ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5" />
                    <span>Save Profile</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}