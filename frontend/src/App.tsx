import { BrowserRouter as Router, Routes, Route, Navigate, useParams } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { MarketingLanguageProvider } from './i18n/MarketingLanguageProvider'
import { ProtectedRoute } from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import LandingPage from './pages/LandingPage'
import DashboardPage from './pages/DashboardPage'
import AgentsPage from './pages/AgentsPage'
import AgentBuilderPage from './pages/AgentBuilderPage'
import SettingsPage from './pages/SettingsPage'
import AdminPage from './pages/AdminPage'
import AdminRoute from './components/admin/AdminRoute'
import IntegrationsPage from './pages/IntegrationsPage'
import IntegrationDetailsPage from './pages/IntegrationDetailsPage'
import IntegrationInstallPage from './pages/IntegrationInstallPage'
import IntegrationConfigurationPage from './pages/IntegrationConfigurationPage'
import IntegrationSuccessPage from './pages/IntegrationSuccessPage'
import IntegrationCreatePage from './pages/IntegrationCreatePage'
import CommunicationChannelsPage from './pages/CommunicationChannelsPage'
import ChannelConfigurationPage from './pages/ChannelConfigurationPage'
import WebChatConfigurationPage from './pages/WebChatConfigurationPage'
import UsagePage from './pages/UsagePage'
import ProfileOnboardingPage from './pages/ProfileOnboardingPage'
import FuzzyOnboardingPage from './pages/FuzzyOnboardingPage'
import AgentSuitePage from './pages/AgentSuitePage'
import PricingPage from './pages/PricingPage'
import DocsPage from './pages/DocsPage'
import TermsPage from './pages/TermsPage'
import PrivacyPage from './pages/PrivacyPage'
import { StudioShell } from './components/studio/StudioShell'
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
            <ThemeProvider>
                <AuthProvider>
                    <MarketingLanguageProvider>
                        <Router>
                            <div className="min-h-screen">
                                <Routes>
                            <Route path="/" element={<LandingPage />} />
                            <Route path="/pricing" element={<PricingPage />} />
                            <Route path="/docs" element={<DocsPage />} />
                            <Route path="/terms" element={<TermsPage />} />
                            <Route path="/privacy" element={<PrivacyPage />} />
                            <Route path="/login" element={<LoginPage />} />
                            <Route path="/signup" element={<LoginPage />} />

                            <Route
                                path="/app/onboarding/profile"
                                element={
                                    <ProtectedRoute>
                                        <ProfileOnboardingPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/app/onboarding/fuzzy"
                                element={
                                    <ProtectedRoute>
                                        <FuzzyOnboardingPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route path="/app/onboarding" element={<Navigate to="/app/onboarding/profile" replace />} />

                            <Route
                                path="/app/admin"
                                element={
                                    <AdminRoute>
                                        <Navigate to="/app/admin/dashboard" replace />
                                    </AdminRoute>
                                }
                            />

                            <Route
                                path="/app/admin/:mode"
                                element={
                                    <AdminRoute>
                                        <AdminPage />
                                    </AdminRoute>
                                }
                            />

                            <Route
                                path="/app/admin/:mode/:integrationId"
                                element={
                                    <AdminRoute>
                                        <AdminPage />
                                    </AdminRoute>
                                }
                            />

                            <Route
                                path="/app"
                                element={
                                    <ProtectedRoute>
                                        <StudioShell />
                                    </ProtectedRoute>
                                }
                            >
                                <Route index element={<DashboardPage />} />
                                <Route path="dashboard" element={<DashboardPage />} />
                                <Route path="agents" element={<AgentsPage />} />
                                <Route path="agents/new" element={<AgentBuilderPage />} />
                                <Route path="agents/:id/edit" element={<AgentBuilderPage />} />
                                <Route path="agents/:id/suite" element={<AgentSuitePage />} />
                                <Route path="settings" element={<SettingsPage />} />
                                <Route path="integrations" element={<IntegrationsPage />} />
                                <Route path="integrations/create" element={<IntegrationCreatePage />} />
                                <Route path="integrations/:id" element={<IntegrationDetailsPage />} />
                                <Route path="integrations/:id/install" element={<IntegrationInstallPage />} />
                                <Route path="integrations/:id/configure" element={<IntegrationConfigurationPage />} />
                                <Route path="integrations/:id/success" element={<IntegrationSuccessPage />} />
                                <Route path="channels" element={<CommunicationChannelsPage />} />
                                <Route path="channels/:id" element={<ChannelConfigurationPage />} />
                                <Route path="webchat/:id" element={<WebChatConfigurationPage />} />
                                <Route path="usage" element={<UsagePage />} />
                            </Route>

                            <Route path="/dashboard" element={<Navigate to="/app" replace />} />
                            <Route path="/agents" element={<Navigate to="/app/agents" replace />} />
                            <Route path="/agents/new" element={<Navigate to="/app/agents/new" replace />} />
                            <Route path="/agents/:id/edit" element={<LegacyAgentEditRedirect />} />
                            <Route path="/settings" element={<Navigate to="/app/settings" replace />} />
                            <Route path="/admin/*" element={<Navigate to="/app/admin" replace />} />

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
                    </MarketingLanguageProvider>
                </AuthProvider>
            </ThemeProvider>
        </QueryClientProvider>
    )
}

export default App

const LegacyAgentEditRedirect = () => {
    const { id } = useParams()
    return <Navigate to={`/app/agents/${id}/edit`} replace />
}
