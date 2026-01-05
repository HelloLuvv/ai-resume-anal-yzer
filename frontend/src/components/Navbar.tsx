'use client'

import { useEffect, useState } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { User } from '@supabase/supabase-js'

const Navbar = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const pathname = usePathname()
  const router = useRouter()

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
      setLoading(false)
    }
    getUser()
  }, [])

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    router.push('/login')
  }

  const isAuthPage = pathname === '/login' || pathname === '/signup'

  if (isAuthPage || loading || !user) {
    return null
  }

  return (
    <nav className="bg-white/10 backdrop-blur-xl border-b border-white/20 shadow-xl sticky top-0 z-50 animate-fade-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2 group cursor-pointer hide-logo-mobile" onClick={() => router.push('/dashboard')}>
            <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300 flex-shrink-0">
              <span className="text-white font-bold">R</span>
            </div>
            <h1 className="text-lg sm:text-xl font-bold text-white group-hover:text-blue-400 transition-colors duration-300 truncate hidden xs:block">Resume Analyzer</h1>
          </div>

          <div className="flex items-center space-x-1 sm:space-x-2 flex-1 sm:flex-none justify-end sm:justify-start">
            <div className="flex items-center space-x-1 sm:space-x-2">
              <a
                href="/upload"
                className={`px-2 sm:px-4 py-2 rounded-lg transition-all duration-300 text-xs sm:text-base font-medium hover:scale-105 active:scale-95 ${
                  pathname === '/upload'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                    : 'text-slate-300 hover:bg-white/10 hover:text-white'
                }`}
              >
                Upload
              </a>
              <a
                href="/results"
                className={`px-2 sm:px-4 py-2 rounded-lg transition-all duration-300 text-xs sm:text-base font-medium hover:scale-105 active:scale-95 ${
                  pathname === '/results'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                    : 'text-slate-300 hover:bg-white/10 hover:text-white'
                }`}
              >
                Results
              </a>
              <a
                href="/dashboard"
                className={`px-2 sm:px-4 py-2 rounded-lg transition-all duration-300 text-xs sm:text-base font-medium hover:scale-105 active:scale-95 ${
                  pathname === '/dashboard'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                    : 'text-slate-300 hover:bg-white/10 hover:text-white'
                }`}
              >
                Dashboard
              </a>
            </div>

            <div className="flex items-center ml-2 sm:ml-4">
              <button
                onClick={handleSignOut}
                className="px-2 sm:px-4 py-2 bg-red-600/10 hover:bg-red-600/20 text-red-300 hover:text-red-200 rounded-lg transition-all duration-300 text-xs sm:text-base font-medium border border-red-500/20 hover:border-red-500/40 hover:scale-105 active:scale-95"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
