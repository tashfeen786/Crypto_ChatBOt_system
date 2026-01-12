// frontend/app/signup/page.js - COMPLETE FIXED VERSION
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { Lock, Mail, Eye, EyeOff, UserPlus, Sparkles, User, DollarSign, Target } from 'lucide-react'
import Link from 'next/link'

export default function SignupPage() {
  const router = useRouter()
  const { signup } = useAuth()
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    balance: 1000,
    risk_tolerance: 5
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    setLoading(true)

    // Remove confirmPassword (not needed for backend)
    const { confirmPassword, ...signupData } = formData
    
    console.log('📤 Sending signup data:', signupData)
    
    const result = await signup(signupData)

    if (result.success) {
      console.log('✅ Signup successful!')
      // router.push('/') is handled by AuthContext
    } else {
      console.error('❌ Signup failed:', result.error)
      setError(result.error || 'Signup failed')
      setLoading(false)
    }
  }

  const nextStep = () => {
    if (step === 1) {
      if (!formData.name || !formData.email) {
        setError('Please fill in all fields')
        return
      }
    }
    setError('')
    setStep(step + 1)
  }

  const prevStep = () => {
    setError('')
    setStep(step - 1)
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <div className="relative w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-4 rounded-3xl bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 flex items-center justify-center shadow-2xl shadow-purple-500/50 animate-pulse">
            <Sparkles className="w-10 h-10" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
            Create Account
          </h1>
          <p className="text-gray-400 mt-2">Join Crypto AI Advisor</p>
        </div>

        {/* Progress Indicator */}
        <div className="flex justify-center gap-2 mb-6">
          <div className={`h-1 w-16 rounded-full transition-all ${step >= 1 ? 'bg-purple-500' : 'bg-slate-700'}`} />
          <div className={`h-1 w-16 rounded-full transition-all ${step >= 2 ? 'bg-purple-500' : 'bg-slate-700'}`} />
          <div className={`h-1 w-16 rounded-full transition-all ${step >= 3 ? 'bg-purple-500' : 'bg-slate-700'}`} />
        </div>

        {/* Signup Card */}
        <div className="glass rounded-2xl p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {/* Step 1: Basic Info */}
            {step === 1 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <User className="w-5 h-5 text-purple-400" />
                  Basic Information
                </h3>

                <div>
                  <label className="block text-sm text-gray-400 mb-2">Full Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="John Doe"
                    className="w-full bg-slate-800 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    required
                    disabled={loading}
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-2">Email Address</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      placeholder="your@email.com"
                      className="w-full bg-slate-800 text-white rounded-xl pl-10 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      required
                      disabled={loading}
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={nextStep}
                  disabled={loading}
                  className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-bold hover:shadow-2xl hover:shadow-purple-500/50 transition-all hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
                >
                  Next Step →
                </button>
              </div>
            )}

            {/* Step 2: Password */}
            {step === 2 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Lock className="w-5 h-5 text-purple-400" />
                  Secure Your Account
                </h3>

                <div>
                  <label className="block text-sm text-gray-400 mb-2">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      placeholder="Min. 6 characters"
                      className="w-full bg-slate-800 text-white rounded-xl pl-10 pr-12 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      required
                      disabled={loading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                      disabled={loading}
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-2">Confirm Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={formData.confirmPassword}
                      onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                      placeholder="Re-enter password"
                      className="w-full bg-slate-800 text-white rounded-xl pl-10 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      required
                      disabled={loading}
                    />
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={prevStep}
                    disabled={loading}
                    className="flex-1 py-3 bg-slate-800 rounded-xl font-semibold hover:bg-slate-700 transition-all disabled:opacity-50"
                  >
                    ← Back
                  </button>
                  <button
                    type="button"
                    onClick={nextStep}
                    disabled={loading}
                    className="flex-1 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-bold hover:shadow-2xl hover:shadow-purple-500/50 transition-all disabled:opacity-50"
                  >
                    Next →
                  </button>
                </div>
              </div>
            )}

            {/* Step 3: Investment Profile */}
            {step === 3 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5 text-purple-400" />
                  Investment Profile
                </h3>

                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Initial Balance: ${formData.balance.toLocaleString()}
                  </label>
                  <input
                    type="range"
                    min="100"
                    max="10000"
                    step="100"
                    value={formData.balance}
                    onChange={(e) => setFormData({...formData, balance: Number(e.target.value)})}
                    className="w-full"
                    disabled={loading}
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>$100</span>
                    <span>$10,000</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Risk Tolerance: {formData.risk_tolerance}/10
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={formData.risk_tolerance}
                    onChange={(e) => setFormData({...formData, risk_tolerance: Number(e.target.value)})}
                    className="w-full"
                    disabled={loading}
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Conservative</span>
                    <span>Aggressive</span>
                  </div>
                  <div className="mt-2 text-xs text-gray-400 text-center">
                    {formData.risk_tolerance <= 3 ? '🛡️ Low Risk - Safe investments' : 
                     formData.risk_tolerance <= 6 ? '⚖️ Moderate Risk - Balanced approach' : 
                     '🚀 High Risk - Aggressive trading'}
                  </div>
                </div>

                <div className="flex gap-3 mt-6">
                  <button
                    type="button"
                    onClick={prevStep}
                    disabled={loading}
                    className="flex-1 py-3 bg-slate-800 rounded-xl font-semibold hover:bg-slate-700 transition-all disabled:opacity-50"
                  >
                    ← Back
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 py-4 bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 rounded-xl font-bold hover:shadow-2xl hover:shadow-purple-500/50 disabled:opacity-50 transition-all hover:scale-105 disabled:hover:scale-100 flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <UserPlus className="w-5 h-5" />
                        Create Account
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-400 text-sm">
              Already have an account?{' '}
              <Link href="/login" className="text-purple-400 hover:text-purple-300 font-semibold transition-colors">
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Back to Home */}
        <div className="mt-6 text-center">
          <Link href="/" className="text-sm text-gray-500 hover:text-gray-300 transition-colors">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}