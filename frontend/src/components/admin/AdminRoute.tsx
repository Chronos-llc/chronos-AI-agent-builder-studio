import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

interface AdminRouteProps {
  children: React.ReactNode
}

const AdminRoute: React.FC<AdminRouteProps> = ({ children }) => {
  const { user, loading, sessionContext, sessionContextLoading } = useAuth()

  if (loading || sessionContextLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    )
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
