'use client'

import { useEffect, useState } from 'react'

interface AnalysisData {
  atsScore: number
  skills: string[]
  education: string[]
  experience: {
    dates: string[]
    roles: string[]
  }
  suggestions: string[]
  jobs: string[]
}

const Results = () => {
  const [data, setData] = useState<AnalysisData | null>(null)

  useEffect(() => {
    const analysis = localStorage.getItem('analysis')
    if (analysis) {
      const parsed = JSON.parse(analysis)
      setTimeout(() => setData(parsed), 0)
    }
  }, [])

  if (!data) return <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">Loading...</div>

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-x-hidden">
      <main className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12 animate-fade-in">
        <header className="mb-10">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-3">Analysis Results</h1>
          <p className="text-slate-400 text-base sm:text-lg">Your resume analysis is complete. Here&apos;s what we found:</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div className="bg-white/10 backdrop-blur-xl p-6 rounded-2xl border border-white/20 shadow-xl md:col-span-1 lg:col-span-1 animate-slide-up">
            <h2 className="text-2xl font-bold text-white mb-6">ATS Score</h2>
            <div className="flex flex-col items-center justify-center">
              <div className="relative w-32 h-32 mb-4">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8" />
                  <circle
                    cx="60"
                    cy="60"
                    r="54"
                    fill="none"
                    stroke="url(#gradient)"
                    strokeWidth="8"
                    strokeDasharray={`${(data.atsScore / 100) * 339.3} 339.3`}
                    strokeLinecap="round"
                    className="transition-all duration-1000 ease-out"
                  />
                  <defs>
                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#3b82f6" />
                      <stop offset="100%" stopColor="#10b981" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-3xl font-bold text-white">{data.atsScore}</span>
                </div>
              </div>
              <p className="text-slate-300 text-center">out of 100</p>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl p-6 rounded-2xl border border-white/20 shadow-xl md:col-span-1 animate-slide-up [animation-delay:100ms]">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center">
              <span className="inline-block w-1 h-6 bg-blue-500 rounded mr-2"></span>
              Skills
            </h2>
            <div className="space-y-2">
              {data.skills.map((skill, i) => (
                <div key={i} className="bg-white/5 rounded-lg p-3 border border-white/10 hover:bg-white/10 transition-colors">
                  <p className="text-slate-200">{skill}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl p-6 rounded-2xl border border-white/20 shadow-xl md:col-span-1 animate-slide-up [animation-delay:200ms]">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center">
              <span className="inline-block w-1 h-6 bg-purple-500 rounded mr-2"></span>
              Education
            </h2>
            <div className="space-y-2">
              {data.education.map((edu, i) => (
                <div key={i} className="bg-white/5 rounded-lg p-3 border border-white/10 hover:bg-white/10 transition-colors">
                  <p className="text-slate-200">{edu}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl p-6 rounded-2xl border border-white/20 shadow-xl md:col-span-1 lg:col-span-2 animate-slide-up [animation-delay:300ms]">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center">
              <span className="inline-block w-1 h-6 bg-orange-500 rounded mr-2"></span>
              Experience
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-semibold text-slate-300 mb-2">Dates</h3>
                <div className="space-y-2">
                  {data.experience.dates.map((date, i) => (
                    <div key={i} className="bg-white/5 rounded-lg p-3 border border-white/10 hover:bg-white/10 transition-colors">
                      <p className="text-slate-200">{date}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-300 mb-2">Roles</h3>
                <div className="space-y-2">
                  {data.experience.roles.map((role, i) => (
                    <div key={i} className="bg-white/5 rounded-lg p-3 border border-white/10 hover:bg-white/10 transition-colors">
                      <p className="text-slate-200">{role}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl p-6 rounded-2xl border border-white/20 shadow-xl md:col-span-1 lg:col-span-2 animate-slide-up [animation-delay:400ms]">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center">
              <span className="inline-block w-1 h-6 bg-yellow-500 rounded mr-2"></span>
              Suggestions
            </h2>
            <div className="space-y-2">
              {data.suggestions.map((sug, i) => (
                <div key={i} className="bg-white/5 rounded-lg p-3 border border-white/10 hover:bg-white/10 transition-colors">
                  <p className="text-slate-200">{sug}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl p-6 rounded-2xl border border-white/20 shadow-xl md:col-span-1 lg:col-span-1 animate-slide-up [animation-delay:500ms]">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center">
              <span className="inline-block w-1 h-6 bg-green-500 rounded mr-2"></span>
              Recommendations
            </h2>
            <div className="space-y-2">
              {data.jobs.map((job, i) => (
                <div key={i} className="bg-white/5 rounded-lg p-3 border border-white/10 hover:bg-white/10 transition-colors">
                  <p className="text-slate-200 text-sm">{job}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-8 flex justify-center animate-fade-in [animation-delay:800ms] [animation-fill-mode:backwards]">
          <a href="/upload" className="bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-8 rounded-xl shadow-lg shadow-blue-500/30 transition-all duration-300 hover:scale-105">
            Analyze Another Resume
          </a>
        </div>
      </main>
    </div>
  )
}

export default Results