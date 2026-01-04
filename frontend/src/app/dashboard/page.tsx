'use client'

import { useEffect, useState } from 'react'
import { supabase } from '../../lib/supabase.ts'
import { User } from '@supabase/supabase-js'

const Dashboard = () => {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    const getUser = async () => {
      const { data } = await supabase.auth.getUser()
      setUser(data.user)
    }
    getUser()
  }, [])

  if (!user) return <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">Loading...</div>

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-x-hidden">
      <main className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12 animate-fade-in">
        <header className="mb-10">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-3">Welcome to Your Dashboard</h1>
          <p className="text-slate-400 text-base sm:text-lg">Manage and analyze your resumes with AI-powered insights</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white/10 backdrop-blur-xl p-6 sm:p-8 rounded-2xl border border-white/20 shadow-xl hover:shadow-2xl hover:scale-[1.01] transition-all duration-300 animate-slide-up">
            <div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-blue-500/20">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white mb-3">Upload Resume</h2>
            <p className="text-slate-300 mb-8 text-base sm:text-lg leading-relaxed">Upload your resume and get instant AI-powered analysis for ATS compatibility.</p>
            <a
              href="/upload"
              className="inline-flex items-center justify-center bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-8 rounded-xl shadow-lg shadow-blue-500/30 transition-all duration-300 hover:translate-y-[-2px]"
            >
              Start Uploading
            </a>
          </div>

          <div className="bg-white/10 backdrop-blur-xl p-6 sm:p-8 rounded-2xl border border-white/20 shadow-xl hover:shadow-2xl hover:scale-[1.01] transition-all duration-300 animate-slide-up [animation-delay:100ms]">
            <div className="w-14 h-14 bg-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-purple-500/20">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white mb-3">View Results</h2>
            <p className="text-slate-300 mb-8 text-base sm:text-lg leading-relaxed">Check your latest analysis results and personalized career recommendations.</p>
            <a
              href="/results"
              className="inline-flex items-center justify-center bg-purple-600 hover:bg-purple-500 text-white font-bold py-3 px-8 rounded-xl shadow-lg shadow-purple-500/30 transition-all duration-300 hover:translate-y-[-2px]"
            >
              View Results
            </a>
          </div>
        </div>

        <section className="mt-12 bg-white/10 backdrop-blur-xl p-6 sm:p-8 rounded-2xl border border-white/20 shadow-xl animate-slide-up [animation-delay:200ms]">
          <h2 className="text-2xl font-bold text-white mb-6">Account Information</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col p-4 sm:p-5 bg-white/5 rounded-xl border border-white/10">
              <span className="text-slate-400 text-sm mb-1 uppercase tracking-wider font-semibold">Email Address</span>
              <span className="text-white font-semibold text-base sm:text-lg break-all">{user.email}</span>
            </div>
            <div className="flex flex-col p-4 sm:p-5 bg-white/5 rounded-xl border border-white/10">
              <span className="text-slate-400 text-sm mb-1 uppercase tracking-wider font-semibold">Account Status</span>
              <span className="text-green-400 font-bold text-base sm:text-lg">Active</span>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default Dashboard