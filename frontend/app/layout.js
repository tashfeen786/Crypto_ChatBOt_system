import './globals.css'
import { Inter } from 'next/font/google'
import { AuthProvider } from '@/contexts/AuthContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Crypto AI Advisor - Investment Chatbot',
  description: 'AI-powered cryptocurrency investment advisor',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <AuthProvider>
          <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  )
}