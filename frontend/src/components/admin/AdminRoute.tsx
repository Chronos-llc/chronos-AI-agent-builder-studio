import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { PlatformLoadingScreen } from '../loading/PlatformLoadingScreen'

interface AdminRouteProps {
  children: React.ReactNode
}

const AdminRoute: React.FC<AdminRouteProps> = ({ children }) => {
  const { user, loading, sessionContext, sessionContextLoading } = useAuth()

  if (loading || sessionContextLoading) {
    return <PlatformLoadingScreen />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (!sessionContext?.is_admin || sessionContext?.is_impersonating) {
    return <Navigate to="/app" replace />
  }

  return <>{children}</>
}

export default AdminRoute
