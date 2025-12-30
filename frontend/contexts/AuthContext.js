'use client'

import { createContext, useContext, useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

const AuthContext = createContext({})

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check if user is logged in on mount
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const userData = localStorage.getItem('user')
      
      if (token && userData) {
        setUser(JSON.parse(userData))
      }
    } catch (error) {
      console.error('Auth check failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      console.log('🔐 Attempting login...', { email })
      
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })

      console.log('📥 Response status:', response.status)

      if (!response.ok) {
        const error = await response.json()
        console.error('❌ Login error:', error)
        throw new Error(error.detail || 'Login failed')
      }

      const data = await response.json()
      console.log('✅ Login response received')
      
      // Store tokens and user data
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      localStorage.setItem('userId', data.user.user_id)
      
      setUser(data.user)
      
      console.log('✅ Login successful, redirecting...')
      
      // Force redirect
      setTimeout(() => {
        router.push('/')
        router.refresh()
      }, 100)
      
      return { success: true }
    } catch (error) {
      console.error('❌ Login error:', error)
      return { success: false, error: error.message }
    }
  }

  const signup = async (userData) => {
    try {
      console.log('📝 Attempting signup...', { email: userData.email })
      
      const response = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(userData)
      })

      console.log('📥 Response status:', response.status)

      if (!response.ok) {
        const error = await response.json()
        console.error('❌ Signup error:', error)
        throw new Error(error.detail || 'Signup failed')
      }

      const data = await response.json()
      console.log('✅ Signup response received')
      
      // Store tokens and user data
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      localStorage.setItem('userId', data.user.user_id)
      
      setUser(data.user)
      
      console.log('✅ Signup successful, redirecting...')
      
      // Force redirect
      setTimeout(() => {
        router.push('/')
        router.refresh()
      }, 100)
      
      return { success: true }
    } catch (error) {
      console.error('❌ Signup error:', error)
      return { success: false, error: error.message }
    }
  }

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      
      if (refreshToken) {
        await fetch('http://localhost:8000/api/auth/logout', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({ refresh_token: refreshToken })
        })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear all auth data
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      localStorage.removeItem('userId')
      
      setUser(null)
      router.push('/login')
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)