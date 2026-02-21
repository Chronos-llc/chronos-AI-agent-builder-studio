import { useEffect, useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { PlatformLoadingScreen } from '@/components/loading/PlatformLoadingScreen'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, loading, sessionContext, sessionContextLoading } = useAuth()
  const location = useLocation()
  const [onboardingLoading, setOnboardingLoading] = useState(true)
  const [onboardingCompleted, setOnboardingCompleted] = useState(false)
  const [fuzzyOnboardingState, setFuzzyOnboardingState] = useState<'pending' | 'completed' | 'skipped'>('pending')
  const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`).replace(/\/$/, '')

  useEffect(() => {
    const fetchOnboardingStatus = async () => {
      if (!user) {
        setOnboardingLoading(false)
        return
      }
      setOnboardingLoading(true)
      try {
        const token = localStorage.getItem('chronos_access_token') || localStorage.getItem('access_token')
        const response = await fetch(`${apiBaseUrl}/api/v1/users/me/onboarding/status`, {
          credentials: 'include',
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        })
        if (!response.ok) {
          setOnboardingCompleted(false)
          setFuzzyOnboardingState('pending')
        } else {
          const statusPayload = await response.json()
          setOnboardingCompleted(Boolean(statusPayload?.onboarding_completed))
          const fuzzyState = statusPayload?.fuzzy_onboarding_state
          if (fuzzyState === 'completed' || fuzzyState === 'skipped' || fuzzyState === 'pending') {
            setFuzzyOnboardingState(fuzzyState)
          } else {
            setFuzzyOnboardingState(statusPayload?.onboarding_completed ? 'completed' : 'pending')
          }
        }
      } catch {
        // Fail closed to preserve onboarding gating.
        setOnboardingCompleted(false)
        setFuzzyOnboardingState('pending')
      } finally {
        setOnboardingLoading(false)
      }
    }
    fetchOnboardingStatus()
  }, [apiBaseUrl, user])

  if (loading) {
    return <PlatformLoadingScreen />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (onboardingLoading || sessionContextLoading) {
    return <PlatformLoadingScreen />
  }

  const onOnboardingPage = location.pathname.startsWith('/app/onboarding')
  const onProfileOnboardingPage = location.pathname.startsWith('/app/onboarding/profile')
  const onFuzzyOnboardingPage = location.pathname.startsWith('/app/onboarding/fuzzy')
  const onAdminPage = location.pathname.startsWith('/app/admin')

  if (sessionContext?.is_admin && !sessionContext?.is_impersonating && !onAdminPage) {
    return <Navigate to="/app/admin" replace />
  }

  if (!onboardingCompleted) {
    if (onAdminPage) return <>{children}</>
    if (!onProfileOnboardingPage) {
      return <Navigate to="/app/onboarding/profile" replace />
    }
    return <>{children}</>
  }

  if (fuzzyOnboardingState === 'pending') {
    if (onAdminPage) return <>{children}</>
    if (!onFuzzyOnboardingPage) {
      return <Navigate to="/app/onboarding/fuzzy" replace />
    }
    return <>{children}</>
  }

  if (onOnboardingPage) {
    return <Navigate to="/app" replace />
  }

  return <>{children}</>
}
