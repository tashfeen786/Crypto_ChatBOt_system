'use client'

import { createContext, useContext, useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

const AuthContext = createContext()
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        setLoading(false)
        return
      }

      // Verify token with backend /me endpoint
      const response = await axios.get(`${API_URL}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.data) {
        const userData = {
          user_id: response.data.user_id,
          email: response.data.email,
          username: response.data.username || response.data.name || 'User',
          name: response.data.name || response.data.username || 'User',
          balance: response.data.balance || 1000,
          risk_tolerance: response.data.risk_tolerance || 5
        }
        
        setUser(userData)
        localStorage.setItem('user', JSON.stringify(userData))
        console.log('✅ User authenticated:', userData)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      // Clear invalid token
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      console.log('🔐 Attempting login...', { email })
      
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        email,
        password
      })

      const { access_token, refresh_token, user: userData } = response.data

      if (access_token && userData) {
        // Store tokens
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        
        // Format user data
        const userInfo = {
          user_id: userData.user_id,
          email: userData.email,
          username: userData.name || 'User',
          name: userData.name || 'User',
          balance: userData.balance || 1000,
          risk_tolerance: userData.risk_tolerance || 5
        }
        
        localStorage.setItem('user', JSON.stringify(userInfo))
        setUser(userInfo)
        
        console.log('✅ Login successful:', userInfo)
        
        // Redirect to dashboard
        setTimeout(() => {
          router.push('/')
          router.refresh()
        }, 100)
        
        return { success: true }
      }
    } catch (error) {
      console.error('❌ Login error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  const signup = async (userData) => {
    try {
      console.log('📝 Attempting signup...', { email: userData.email })
      
      const response = await axios.post(`${API_URL}/api/auth/signup`, {
        name: userData.name,
        email: userData.email,
        password: userData.password,
        balance: userData.balance || 1000,
        risk_tolerance: userData.risk_tolerance || 5
      })

      const { access_token, refresh_token, user: newUser } = response.data

      if (access_token && newUser) {
        // Store tokens
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        
        // Format user data
        const userInfo = {
          user_id: newUser.user_id,
          email: newUser.email,
          username: newUser.name || 'User',
          name: newUser.name || 'User',
          balance: newUser.balance || 1000,
          risk_tolerance: newUser.risk_tolerance || 5
        }
        
        localStorage.setItem('user', JSON.stringify(userInfo))
        setUser(userInfo)
        
        console.log('✅ Signup successful:', userInfo)
        
        // Redirect to dashboard
        setTimeout(() => {
          router.push('/')
          router.refresh()
        }, 100)
        
        return { success: true }
      }
    } catch (error) {
      console.error('❌ Signup error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Signup failed' 
      }
    }
  }

  const logout = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      if (token) {
        await axios.post(`${API_URL}/api/auth/logout`, {}, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear all auth data
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      
      setUser(null)
      router.push('/login')
    }
  }

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      login, 
      signup, 
      logout,
      checkAuth 
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}