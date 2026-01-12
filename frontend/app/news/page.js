'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { ArrowLeft, Newspaper, ExternalLink, TrendingUp } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function NewsPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('hot')

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
    if (user) {
      fetchNews()
    }
  }, [user, authLoading, router, filter])

  const fetchNews = async () => {
    setLoading(true)
    try {
      const response = await axios.get(
        `${API_URL}/api/news/latest`,
        {
          params: { limit: 20, filter },
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )
      setNews(response.data.news || [])
      setLoading(false)
    } catch (err) {
      console.error('News fetch error:', err)
      setLoading(false)
    }
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Newspaper className="w-8 h-8" />
          </div>
          <p className="text-white">Loading news...</p>
        </div>
      </div>
    )
  }

  if (!user) return null

  const filters = [
    { id: 'hot', label: '🔥 Hot', icon: '🔥' },
    { id: 'rising', label: '📈 Rising', icon: '📈' },
    { id: 'bullish', label: '🐂 Bullish', icon: '🐂' },
    { id: 'bearish', label: '🐻 Bearish', icon: '🐻' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => router.push('/')}
            className="p-2 glass rounded-xl hover:bg-slate-800 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-400" />
          </button>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
              Crypto News
            </h1>
            <p className="text-gray-400 text-sm mt-1">Stay updated with latest market news</p>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          {filters.map(f => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={`px-4 py-2 rounded-xl font-semibold transition-all whitespace-nowrap ${
                filter === f.id
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : 'glass text-gray-400 hover:text-white'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* News Grid */}
        <div className="space-y-4">
          {loading ? (
            [1, 2, 3].map(i => (
              <div key={i} className="glass rounded-xl p-4 animate-pulse">
                <div className="h-4 bg-slate-700 rounded w-3/4 mb-2" />
                <div className="h-3 bg-slate-700 rounded w-1/2" />
              </div>
            ))
          ) : news.length === 0 ? (
            <div className="text-center py-12 glass rounded-2xl">
              <Newspaper className="w-16 h-16 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400">No news available</p>
            </div>
          ) : (
            news.map((item, i) => (
              <a
                key={i}
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block glass rounded-xl p-4 hover:bg-slate-800/50 transition-all group"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-white font-semibold mb-2 group-hover:text-purple-400 transition-colors line-clamp-2">
                      {item.title}
                    </h3>
                    {item.description && (
                      <p className="text-gray-400 text-sm line-clamp-2 mb-2">
                        {item.description}
                      </p>
                    )}
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span>{item.source}</span>
                      <span>•</span>
                      <span>{timeAgo(item.published_at)}</span>
                    </div>
                    {item.currencies && item.currencies.length > 0 && (
                      <div className="flex gap-1 mt-2">
                        {item.currencies.slice(0, 5).map(coin => (
                          <span key={coin} className="px-2 py-0.5 bg-purple-500/20 rounded text-xs text-purple-300">
                            {coin}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <ExternalLink className="w-5 h-5 text-gray-500 group-hover:text-purple-400 transition-colors flex-shrink-0" />
                </div>
              </a>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

function timeAgo(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now - date) / 1000)
  
  if (seconds < 60) return `${seconds}s ago`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}