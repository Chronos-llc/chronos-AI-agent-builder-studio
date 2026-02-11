import { useEffect, useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, loading } = useAuth()
  const location = useLocation()
  const [onboardingLoading, setOnboardingLoading] = useState(true)
  const [onboardingCompleted, setOnboardingCompleted] = useState(true)

  useEffect(() => {
    const fetchProfile = async () => {
      if (!user) {
        setOnboardingLoading(false)
        return
      }
      setOnboardingLoading(true)
      try {
        const response = await fetch('/api/v1/users/me/profile')
        if (!response.ok) {
          setOnboardingCompleted(false)
        } else {
          const profile = await response.json()
          setOnboardingCompleted(Boolean(profile?.onboarding_completed))
        }
      } catch {
        setOnboardingCompleted(false)
      } finally {
        setOnboardingLoading(false)
      }
    }
    fetchProfile()
  }, [user])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (onboardingLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  const onOnboardingPage = location.pathname.startsWith('/app/onboarding')
  if (!onboardingCompleted && !onOnboardingPage) {
    return <Navigate to="/app/onboarding" replace />
  }
  if (onboardingCompleted && onOnboardingPage) {
    return <Navigate to="/app" replace />
  }

  return <>{children}</>
}
