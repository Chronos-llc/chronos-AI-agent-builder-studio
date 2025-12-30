import React from 'react'
import { useAuth } from '@/contexts/AuthContext'

const DashboardPage: React.FC = () => {
    const { user, logout } = useAuth()

    return (
        <div className="min-h-screen bg-background">
            <header className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center">
                            <h1 className="text-2xl font-bold text-gray-900">
                                Chronos AI Agent Builder Studio
                            </h1>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-gray-700">Welcome, {user?.full_name || user?.username}</span>
                            <button
                                onClick={logout}
                                className="btn btn-outline"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div className="px-4 py-6 sm:px-0">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <div className="card p-6">
                            <h3 className="text-lg font-medium mb-2">Total Agents</h3>
                            <p className="text-3xl font-bold text-primary">0</p>
                            <p className="text-sm text-gray-500">No agents created yet</p>
                        </div>

                        <div className="card p-6">
                            <h3 className="text-lg font-medium mb-2">Active Agents</h3>
                            <p className="text-3xl font-bold text-green-600">0</p>
                            <p className="text-sm text-gray-500">Currently running</p>
                        </div>

                        <div className="card p-6">
                            <h3 className="text-lg font-medium mb-2">Total Usage</h3>
                            <p className="text-3xl font-bold text-blue-600">0</p>
                            <p className="text-sm text-gray-500">API calls this month</p>
                        </div>
                    </div>

                    <div className="mt-8">
                        <div className="card p-6">
                            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                <button className="btn btn-primary p-4 text-left">
                                    <div>
                                        <h3 className="font-medium">Create Agent</h3>
                                        <p className="text-sm opacity-75">Build a new AI agent</p>
                                    </div>
                                </button>

                                <button className="btn btn-secondary p-4 text-left">
                                    <div>
                                        <h3 className="font-medium">View Agents</h3>
                                        <p className="text-sm opacity-75">Manage existing agents</p>
                                    </div>
                                </button>

                                <button className="btn btn-outline p-4 text-left">
                                    <div>
                                        <h3 className="font-medium">Integrations</h3>
                                        <p className="text-sm opacity-75">Connect external services</p>
                                    </div>
                                </button>

                                <button className="btn btn-outline p-4 text-left">
                                    <div>
                                        <h3 className="font-medium">Settings</h3>
                                        <p className="text-sm opacity-75">Configure preferences</p>
                                    </div>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    )
}

export default DashboardPage