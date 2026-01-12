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

export const getChatHistory = async (userId, limit = 10) => {
  try {
    const response = await api.get(`/api/chat/history/${userId}?limit=${limit}`)
    return response.data
  } catch (error) {
    console.error('Get Chat History Error:', error)
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

export const getCurrentPrice = async (symbol) => {
  try {
    const response = await api.get(`/api/trading/price/${symbol}`)
    return response.data
  } catch (error) {
    console.error('Get Current Price Error:', error)
    throw error
  }
}

export const checkStopLoss = async (data) => {
  try {
    const response = await api.post('/api/trading/stop-loss-check', data)
    return response.data
  } catch (error) {
    console.error('Check Stop Loss Error:', error)
    throw error
  }
}

export const getTradingFees = async () => {
  try {
    const response = await api.get('/api/trading/fees')
    return response.data
  } catch (error) {
    console.error('Get Trading Fees Error:', error)
    throw error
  }
}

// ==================== PORTFOLIO ENDPOINTS ====================

export const getPortfolio = async (userId) => {
  try {
    console.log('📊 API Call: getPortfolio for user:', userId)
    console.log('📍 Endpoint: /api/portfolio/' + userId)
    const response = await api.get(`/api/portfolio/${userId}`)
    console.log('✅ Portfolio response:', response.data)
    return response.data
  } catch (error) {
    console.error('❌ Portfolio Error:', error.response?.status, error.response?.data || error.message)
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

export const removeHolding = async (userId, symbol, quantity = null) => {
  try {
    const url = quantity 
      ? `/api/portfolio/${userId}/holdings/${symbol}?quantity=${quantity}`
      : `/api/portfolio/${userId}/holdings/${symbol}`
    const response = await api.delete(url)
    return response.data
  } catch (error) {
    console.error('Remove Holding Error:', error)
    throw error
  }
}

export const getPortfolioPerformance = async (userId) => {
  try {
    // ✅ FIXED: URL changed from /portfolio/ to /users/ AND parameter is userId (lowercase i)
    const response = await api.get(`/api/users/${userId}/performance`)
    return response.data
  } catch (error) {
    // Silently handle 404 - endpoint is optional
    if (error.response?.status === 404) {
      console.log('ℹ️ Performance endpoint not available')
      return null
    }
    // Log other errors
    console.error('❌ Performance Error:', error.response?.status, error.response?.data || error.message)
    throw error
  }
}

export const getPortfolioAlerts = async (userId) => {
  try {
    const response = await api.get(`/api/portfolio/${userId}/alerts`)
    return response.data
  } catch (error) {
    console.error('Get Portfolio Alerts Error:', error)
    throw error
  }
}

export const getPortfolioSummary = async (userId) => {
  try {
    const response = await api.get(`/api/portfolio/${userId}/summary`)
    return response.data
  } catch (error) {
    console.error('Get Portfolio Summary Error:', error)
    throw error
  }
}

export const suggestRebalancing = async (userId) => {
  try {
    const response = await api.post(`/api/portfolio/${userId}/rebalance`)
    return response.data
  } catch (error) {
    console.error('Suggest Rebalancing Error:', error)
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
    console.log('👤 API Call: getUserProfile for user:', userId)
    console.log('📍 Endpoint: /api/users/' + userId)
    const response = await api.get(`/api/users/${userId}`)
    console.log('✅ User profile response:', response.data)
    return response.data
  } catch (error) {
    console.error('❌ User Profile Error:', error.response?.status, error.response?.data || error.message)
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
    console.log('💰 API Call: getUserBalance for user:', userId)
    console.log('📍 Endpoint: /api/users/' + userId + '/balance')
    const response = await api.get(`/api/users/${userId}/balance`)
    console.log('✅ Balance response:', response.data)
    return response.data
  } catch (error) {
    console.error('❌ Balance Error:', error.response?.status, error.response?.data || error.message)
    throw error
  }
}

export const updateUserBalance = async (userId, amount, operation = 'set') => {
  try {
    const response = await api.post(`/api/users/${userId}/balance`, {
      amount,
      operation
    })
    return response.data
  } catch (error) {
    console.error('Update User Balance Error:', error)
    throw error
  }
}

export const deleteUser = async (userId) => {
  try {
    const response = await api.delete(`/api/users/${userId}`)
    return response.data
  } catch (error) {
    console.error('Delete User Error:', error)
    throw error
  }
}

export const listUsers = async (limit = 10, offset = 0) => {
  try {
    const response = await api.get(`/api/users/?limit=${limit}&offset=${offset}`)
    return response.data
  } catch (error) {
    console.error('List Users Error:', error)
    throw error
  }
}

// ==================== NEWS ENDPOINTS ====================

export const getLatestNews = async (limit = 10, filter = 'hot') => {
  try {
    const response = await api.get(`/api/news/latest?limit=${limit}&filter=${filter}`)
    return response.data
  } catch (error) {
    console.error('Get Latest News Error:', error)
    return { news: [] }
  }
}

export const getNewsByCoin = async (symbol, limit = 10) => {
  try {
    const response = await api.get(`/api/news/by-coin/${symbol}?limit=${limit}`)
    return response.data
  } catch (error) {
    console.error('Get News By Coin Error:', error)
    return { news: [] }
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

export const checkAPIStatus = async () => {
  try {
    const response = await api.get('/api/status')
    return response.data
  } catch (error) {
    console.error('API Status Error:', error)
    throw error
  }
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Quick helper to check if backend is online
 */
export const isBackendOnline = async () => {
  try {
    await checkHealth()
    return true
  } catch (error) {
    return false
  }
}

/**
 * Quick helper to get user's complete data
 */
export const getUserCompleteData = async (userId) => {
  try {
    console.log('📦 Fetching complete user data for:', userId)
    const [profile, portfolio, alerts] = await Promise.all([
      getUserProfile(userId),
      getPortfolio(userId),
      getPortfolioAlerts(userId)
    ])
    
    console.log('✅ Complete user data fetched')
    return {
      profile,
      portfolio,
      alerts
    }
  } catch (error) {
    console.error('❌ Get User Complete Data Error:', error)
    throw error
  }
}

/**
 * Quick helper to get market overview
 */
export const getMarketOverview = async () => {
  try {
    const [summary, topCoins, news] = await Promise.all([
      getMarketSummary(),
      getTopCoins(10),
      getLatestNews(5, 'hot')
    ])
    
    return {
      summary,
      topCoins,
      news
    }
  } catch (error) {
    console.error('Get Market Overview Error:', error)
    throw error
  }
}

// Export default api instance
export default api