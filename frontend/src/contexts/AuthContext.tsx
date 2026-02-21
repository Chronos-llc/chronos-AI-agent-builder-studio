import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'
import { toast } from 'react-hot-toast'

interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  is_verified: boolean
  is_superuser: boolean
  theme: string
  language: string
  created_at: string
  updated_at: string
}

export interface SessionContext {
  user: User
  is_admin: boolean
  is_impersonating: boolean
  impersonator_user_id?: number | null
  impersonator_admin_user_id?: number | null
}

interface AuthContextType {
  user: User | null
  sessionContext: SessionContext | null
  loading: boolean
  sessionContextLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => Promise<void>
  updateUser: (userData: Partial<User>) => Promise<void>
  refreshSessionContext: () => Promise<void>
  setAccessToken: (token: string | null) => void
}

interface RegisterData {
  email: string
  username: string
  full_name?: string
  password: string
  password_confirm: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)
const ACCESS_TOKEN_KEY = 'chronos_access_token'
const LEGACY_ACCESS_TOKEN_KEY = 'access_token'

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL
axios.defaults.headers.common['Content-Type'] = 'application/json'
axios.defaults.withCredentials = true  // Send cookies with requests

const setAuthHeader = (token: string | null) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete axios.defaults.headers.common['Authorization']
  }
}

// Add auth token to requests (if not already in cookies)
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY) || localStorage.getItem(LEGACY_ACCESS_TOKEN_KEY)
    if (token) {
      config.headers = config.headers ?? {}
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Handle token refresh
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshResponse = await axios.post('/api/v1/auth/refresh', {})
        const refreshedAccessToken = refreshResponse.data?.access_token
        if (refreshedAccessToken) {
          localStorage.setItem(ACCESS_TOKEN_KEY, refreshedAccessToken)
          localStorage.setItem(LEGACY_ACCESS_TOKEN_KEY, refreshedAccessToken)
          setAuthHeader(refreshedAccessToken)
        }

        // Retry original request
        return axios(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem(ACCESS_TOKEN_KEY)
        localStorage.removeItem(LEGACY_ACCESS_TOKEN_KEY)
        setAuthHeader(null)
        // Refresh failed, redirect to login
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [sessionContext, setSessionContext] = useState<SessionContext | null>(null)
  const [loading, setLoading] = useState(true)
  const [sessionContextLoading, setSessionContextLoading] = useState(true)

  useEffect(() => {
    const existingToken = localStorage.getItem(ACCESS_TOKEN_KEY) || localStorage.getItem(LEGACY_ACCESS_TOKEN_KEY)
    setAuthHeader(existingToken)
    checkAuth()
  }, [])

  const setAccessToken = (token: string | null) => {
    if (token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, token)
      localStorage.setItem(LEGACY_ACCESS_TOKEN_KEY, token)
      setAuthHeader(token)
      return
    }
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(LEGACY_ACCESS_TOKEN_KEY)
    setAuthHeader(null)
  }

  const fetchSessionContext = async () => {
    setSessionContextLoading(true)
    try {
      const response = await axios.get('/api/v1/auth/session-context')
      setSessionContext(response.data)
      if (response.data?.user) {
        setUser(response.data.user)
      }
    } catch (error) {
      setSessionContext(null)
      throw error
    } finally {
      setSessionContextLoading(false)
    }
  }

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/v1/auth/me')
      setUser(response.data)
      await fetchSessionContext()
    } catch (error) {
      console.error('Auth check failed:', error)
      setSessionContext(null)
      setSessionContextLoading(false)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const formData = new URLSearchParams()
      formData.set('username', email)
      formData.set('password', password)

      // Persist access token for bearer-auth endpoints (cookie remains fallback)
      const tokenResponse = await axios.post('/api/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      const accessToken = tokenResponse.data?.access_token
      if (accessToken) {
        setAccessToken(accessToken)
      }

      // Get user info
      const userResponse = await axios.get('/api/v1/auth/me')
      setUser(userResponse.data)
      await fetchSessionContext()

      toast.success('Login successful!')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed'
      toast.error(message)
      throw new Error(message)
    }
  }

  const register = async (userData: RegisterData) => {
    try {
      await axios.post('/api/v1/auth/register', userData)
      toast.success('Registration successful! Please login.')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed'
      toast.error(message)
      throw new Error(message)
    }
  }

  const logout = async () => {
    try {
      await axios.post('/api/v1/auth/logout')
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      setAccessToken(null)
      setUser(null)
      setSessionContext(null)
      setSessionContextLoading(false)
      toast.success('Logged out successfully')
    }
  }

  const updateUser = async (userData: Partial<User>) => {
    try {
      const response = await axios.put('/api/v1/users/me', userData)
      setUser(response.data)
      toast.success('Profile updated successfully')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Update failed'
      toast.error(message)
      throw new Error(message)
    }
  }

  const value = {
    user,
    sessionContext,
    loading,
    sessionContextLoading,
    login,
    register,
    logout,
    updateUser,
    refreshSessionContext: fetchSessionContext,
    setAccessToken,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
