import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import AgentsPage from './pages/AgentsPage'
import AgentBuilderPage from './pages/AgentBuilderPage'
import SettingsPage from './pages/SettingsPage'
import AdminPage from './pages/AdminPage'
import './App.css'

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
            refetchOnWindowFocus: false,
        },
    },
})

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <Router>
                    <div className="min-h-screen bg-background">
                        <Routes>
                            <Route path="/login" element={<LoginPage />} />
                            <Route
                                path="/"
                                element={
                                    <ProtectedRoute>
                                        <DashboardPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/dashboard"
                                element={
                                    <ProtectedRoute>
                                        <DashboardPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/agents"
                                element={
                                    <ProtectedRoute>
                                        <AgentsPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/agents/new"
                                element={
                                    <ProtectedRoute>
                                        <AgentBuilderPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/agents/:id/edit"
                                element={
                                    <ProtectedRoute>
                                        <AgentBuilderPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/settings"
                                element={
                                    <ProtectedRoute>
                                        <SettingsPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/admin/*"
                                element={
                                    <ProtectedRoute>
                                        <AdminPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route path="*" element={<Navigate to="/" replace />} />
                        </Routes>
                        <Toaster
                            position="top-right"
                            toastOptions={{
                                duration: 4000,
                                style: {
                                    background: 'hsl(var(--card))',
                                    color: 'hsl(var(--card-foreground))',
                                    border: '1px solid hsl(var(--border))',
                                },
                            }}
                        />
                    </div>
                </Router>
            </AuthProvider>
        </QueryClientProvider>
    )
}

export default App