import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(`${API_URL}/api/auth/refresh`, {
          refresh_token: refreshToken
        })

        const { access_token } = response.data
        localStorage.setItem('access_token', access_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.clear()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// ==================== CHAT ENDPOINTS ====================

export const sendChatMessage = async (data) => {
  try {
    const response = await api.post('/api/chat/', data)
    return response.data
  } catch (error) {
    console.error('Chat API Error:', error)
    throw error
  }
}

export const getQuickAdvice = async (symbol, userRisk = 5) => {
  try {
    const response = await api.post('/api/chat/quick-advice', {
      symbol,
      user_risk_tolerance: userRisk
    })
    return response.data
  } catch (error) {
    console.error('Quick Advice Error:', error)
    throw error
  }
}

export const getSmartAllocation = async (amount, userRisk = 5) => {
  try {
    const response = await api.post('/api/chat/smart-allocation', {
      amount,
      user_risk_tolerance: userRisk
    })
    return response.data
  } catch (error) {
    console.error('Smart Allocation Error:', error)
    throw error
  }
}

// ==================== COINS ENDPOINTS ====================

export const getCoinPrices = async (symbols = null) => {
  try {
    const url = symbols 
      ? `/api/coins/prices?symbols=${symbols}` 
      : '/api/coins/prices'
    const response = await api.get(url)
    return response.data
  } catch (error) {
    console.error('Get Prices Error:', error)
    throw error
  }
}

export const getCoinDetails = async (symbol) => {
  try {
    const response = await api.get(`/api/coins/${symbol}`)
    return response.data
  } catch (error) {
    console.error('Get Coin Details Error:', error)
    throw error
  }
}

export const getTopCoins = async (limit = 50) => {
  try {
    const response = await api.get(`/api/coins/?limit=${limit}`)
    return response.data
  } catch (error) {
    console.error('Get Top Coins Error:', error)
    throw error
  }
}

export const getRiskAnalysis = async (symbol) => {
  try {
    const response = await api.get(`/api/coins/risk/${symbol}`)
    return response.data
  } catch (error) {
    console.error('Get Risk Analysis Error:', error)
    throw error
  }
}

export const getMarketSummary = async () => {
  try {
    const response = await api.get('/api/coins/market/summary')
    return response.data
  } catch (error) {
    console.error('Get Market Summary Error:', error)
    throw error
  }
}

// ==================== NEWS ENDPOINTS ====================

export const getLatestNews = async (limit = 5, filter = 'hot') => {
  try {
    const response = await api.get(`/api/news/latest?limit=${limit}&filter=${filter}`)
    return response.data
  } catch (error) {
    console.error('Get Latest News Error:', error)
    // Return empty news array if error
    return { news: [] }
  }
}

// ==================== TRADING ENDPOINTS ====================

export const executeBuy = async (data) => {
  try {
    const response = await api.post('/api/trading/buy', data)
    return response.data
  } catch (error) {
    console.error('Execute Buy Error:', error)
    throw error
  }
}

export const executeSell = async (data) => {
  try {
    const response = await api.post('/api/trading/sell', data)
    return response.data
  } catch (error) {
    console.error('Execute Sell Error:', error)
    throw error
  }
}

export const simulateBuy = async (data) => {
  try {
    const response = await api.post('/api/trading/simulate-buy', data)
    return response.data
  } catch (error) {
    console.error('Simulate Buy Error:', error)
    throw error
  }
}

export const getPositionSize = async (balance, riskTolerance, symbol) => {
  try {
    const response = await api.post('/api/trading/position-size', {
      balance,
      risk_tolerance: riskTolerance,
      symbol
    })
    return response.data
  } catch (error) {
    console.error('Get Position Size Error:', error)
    throw error
  }
}

// ==================== PORTFOLIO ENDPOINTS ====================

export const getPortfolio = async (userId) => {
  try {
    const response = await api.get(`/api/portfolio/${userId}`)
    return response.data
  } catch (error) {
    console.error('Get Portfolio Error:', error)
    throw error
  }
}

export const addHolding = async (data) => {
  try {
    const response = await api.post('/api/portfolio/add-holding', data)
    return response.data
  } catch (error) {
    console.error('Add Holding Error:', error)
    throw error
  }
}

export const getPortfolioPerformance = async (userId) => {
  try {
    const response = await api.get(`/api/portfolio/${userId}/performance`)
    return response.data
  } catch (error) {
    console.error('Get Portfolio Performance Error:', error)
    throw error
  }
}

// ==================== USER ENDPOINTS ====================

export const registerUser = async (data) => {
  try {
    const response = await api.post('/api/users/register', data)
    return response.data
  } catch (error) {
    console.error('Register User Error:', error)
    throw error
  }
}

export const getUserProfile = async (userId) => {
  try {
    const response = await api.get(`/api/users/${userId}`)
    return response.data
  } catch (error) {
    console.error('Get User Profile Error:', error)
    throw error
  }
}

export const updateUserProfile = async (userId, data) => {
  try {
    const response = await api.put(`/api/users/${userId}`, data)
    return response.data
  } catch (error) {
    console.error('Update User Profile Error:', error)
    throw error
  }
}

export const getUserBalance = async (userId) => {
  try {
    const response = await api.get(`/api/users/${userId}/balance`)
    return response.data
  } catch (error) {
    console.error('Get User Balance Error:', error)
    throw error
  }
}

// ==================== HEALTH CHECK ====================

export const checkHealth = async () => {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    console.error('Health Check Error:', error)
    throw error
  }
}

export default api