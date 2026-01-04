'use client'

import { useState } from 'react'
import { supabase } from '../../lib/supabase.ts'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleLogin = async () => {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) {
      alert(error.message)
    } else {
      window.location.href = '/dashboard'
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-x-hidden p-4">
      <div className="bg-white/10 backdrop-blur-xl p-6 sm:p-8 rounded-2xl shadow-2xl w-full max-w-md border border-white/20 animate-slide-up">
        <h2 className="text-2xl sm:text-3xl font-bold mb-6 text-white text-center">Login</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-3 rounded-xl bg-slate-900/50 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 rounded-xl bg-slate-900/50 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
          </div>
          <button
            onClick={handleLogin}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 rounded-xl shadow-lg shadow-blue-500/30 transition-all duration-300 mt-2"
          >
            Login
          </button>
        </div>
        <p className="mt-6 text-center text-slate-400">
          Don&apos;t have an account?{' '}
          <a href="/signup" className="text-blue-400 hover:text-blue-300 transition-colors font-medium">
            Sign up
          </a>
        </p>
      </div>
    </div>
  )
}

export default Login