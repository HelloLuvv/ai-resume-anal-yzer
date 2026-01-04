'use client'

import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { supabase } from '@/lib/supabase'
import axios from 'axios'
import { useRouter } from 'next/navigation'

const Upload = () => {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const [fileName, setFileName] = useState('')
  const router = useRouter()

  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setError('')
    setFileName(file.name)
    setUploading(true)
    setProgress(10)

    const { data, error: authError } = await supabase.auth.getUser()
    if (authError || !data.user) {
      setError('Please login to continue')
      setUploading(false)
      return
    }

    const formData = new FormData()
    formData.append('resume', file)

    setProgress(30)

    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session?.access_token) {
        setError('Session expired. Please login again.')
        setUploading(false)
        return
      }

      const uploadRes = await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/upload-resume`, formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      setProgress(50)

      const resumeId = uploadRes.data.resume_id

      const authHeaders = {
        'Authorization': `Bearer ${session.access_token}`
      }

      const analyzeRes = await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/analyze-resume`, { resume_id: resumeId }, { headers: authHeaders })
      setProgress(70)

      const scoreRes = await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/ats-score`, { resume_id: resumeId }, { headers: authHeaders })
      setProgress(90)

      const jobRes = await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/job-recommendations`, { resume_id: resumeId }, { headers: authHeaders })
      setProgress(100)

      const analysisData = {
        skills: analyzeRes.data.skills,
        education: analyzeRes.data.education,
        experience: analyzeRes.data.experience,
        suggestions: analyzeRes.data.suggestions,
        atsScore: scoreRes.data.score,
        jobs: jobRes.data.jobs
      }
      localStorage.setItem('analysis', JSON.stringify(analysisData))
      
      setTimeout(() => {
        router.push('/results')
      }, 500)
    } catch (error: any) {
      const errorMessage = error?.response?.data?.error || error?.message || 'Failed to process resume. Please try again.'
      setError(errorMessage)
      console.error(error)
      setUploading(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop, 
    accept: { 
      'application/pdf': ['.pdf'], 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] 
    },
    disabled: uploading
  })

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-x-hidden p-4 sm:p-8 flex items-center justify-center">
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        @keyframes pulse-ring {
          0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
          70% { box-shadow: 0 0 0 15px rgba(59, 130, 246, 0); }
          100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
        }
        .animate-float { animation: float 3s ease-in-out infinite; }
        .animate-pulse-ring { animation: pulse-ring 2s infinite; }
      `}</style>
      
      <div className="w-full max-w-md animate-slide-up">
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl p-8 sm:p-10 border border-white/20 hover:border-white/30 transition-all duration-500">
          <div className="text-center mb-8">
            <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">Upload Resume</h1>
            <p className="text-slate-300 text-sm sm:text-base">Analyze and optimize your resume instantly</p>
          </div>

          <div
            {...getRootProps()}
            className={`relative group cursor-pointer transition-all duration-300 ${
              uploading ? 'opacity-60 cursor-not-allowed' : ''
            }`}
          >
            <input {...getInputProps()} />
            <div
              className={`border-2 border-dashed rounded-xl p-8 sm:p-12 text-center transition-all duration-300 ${
                isDragActive
                  ? 'border-blue-400 bg-blue-400/10 scale-105'
                  : 'border-slate-400/30 bg-slate-400/5 group-hover:bg-slate-400/10 group-hover:border-slate-300/50'
              }`}
            >
              <div className={`mb-4 ${isDragActive ? 'animate-float' : ''}`}>
                <svg
                  className={`w-12 h-12 sm:w-16 sm:h-16 mx-auto transition-colors duration-300 ${
                    isDragActive ? 'text-blue-400 animate-pulse-ring' : 'text-slate-300 group-hover:text-slate-200'
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>

              <div>
                {isDragActive ? (
                  <p className="text-blue-400 font-semibold text-base sm:text-lg">Drop your resume here</p>
                ) : (
                  <>
                    <p className="text-slate-200 font-semibold text-base sm:text-lg mb-1">Drag & drop your resume</p>
                    <p className="text-slate-400 text-sm">or click to browse (PDF or DOCX)</p>
                  </>
                )}
              </div>
            </div>
          </div>

          {fileName && !uploading && (
            <div className="mt-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
              <p className="text-green-400 text-sm text-center truncate">✓ {fileName} selected</p>
            </div>
          )}

          {uploading && (
            <div className="mt-8 space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-slate-300 text-sm font-medium">Processing resume...</p>
                  <p className="text-blue-400 text-sm font-semibold">{progress}%</p>
                </div>
                <div className="w-full bg-slate-700/50 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-blue-400 to-blue-600 h-2 rounded-full transition-all duration-300 shadow-lg shadow-blue-500/50"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
              </div>
              <div className="flex justify-center">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></span>
                  <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                  <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg animate-in fade-in slide-in-from-top-2">
              <p className="text-red-400 text-sm text-center">{error}</p>
            </div>
          )}
        </div>

        <p className="text-slate-400 text-xs sm:text-sm text-center mt-6">
          Your resume will be analyzed using AI to provide personalized insights
        </p>
      </div>
    </div>
  )
}

export default Upload