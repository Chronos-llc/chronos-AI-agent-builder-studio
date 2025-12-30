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

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => void
  updateUser: (userData: Partial<User>) => Promise<void>
}

interface RegisterData {
  email: string
  username: string
  full_name?: string
  password: string
  password_confirm: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL
axios.defaults.headers.common['Content-Type'] = 'application/json'

// Add auth token to requests
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
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
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken
          })

          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          // Retry original request
          return axios(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (token) {
        const response = await axios.get('/api/v1/auth/me')
        setUser(response.data)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const response = await axios.post('/api/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      const { access_token, refresh_token } = response.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Get user info
      const userResponse = await axios.get('/api/v1/auth/me')
      setUser(userResponse.data)

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

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    toast.success('Logged out successfully')
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
    loading,
    login,
    register,
    logout,
    updateUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}