'use client'

import { useEffect } from 'react'
import { supabase } from '../lib/supabase.ts'

export default function Home() {
  useEffect(() => {
    const checkUser = async () => {
      const { data } = await supabase.auth.getUser()
      if (data.user) {
        window.location.href = '/dashboard'
      } else {
        window.location.href = '/login'
      }
    }
    checkUser()
  }, [])

  return <div>Loading...</div>
}
