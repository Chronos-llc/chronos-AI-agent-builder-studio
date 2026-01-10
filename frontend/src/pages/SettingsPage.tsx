import React, { useState } from 'react'
import { User, Key, Bell, Shield } from 'lucide-react'
import PersonalAccessTokens from '../components/PersonalAccessTokens'

const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'tokens' | 'notifications' | 'security'>('profile')

  return (
    <div className="page-container">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-64 space-y-1">
          <button
            onClick={() => setActiveTab('profile')}
            className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'profile' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'
            }`}
          >
            <User className="w-4 h-4" />
            <span>Profile</span>
          </button>
          <button
            onClick={() => setActiveTab('tokens')}
            className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'tokens' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'
            }`}
          >
            <Key className="w-4 h-4" />
            <span>Access Tokens</span>
          </button>
          <button
            onClick={() => setActiveTab('notifications')}
            className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'notifications' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'
            }`}
          >
            <Bell className="w-4 h-4" />
            <span>Notifications</span>
          </button>
          <button
            onClick={() => setActiveTab('security')}
            className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'security' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'
            }`}
          >
            <Shield className="w-4 h-4" />
            <span>Security</span>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'profile' && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold mb-4">Profile Settings</h2>
              <p className="text-muted-foreground">
                Profile settings will be implemented in the next phase
              </p>
            </div>
          )}

          {activeTab === 'tokens' && <PersonalAccessTokens />}

          {activeTab === 'notifications' && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold mb-4">Notification Settings</h2>
              <p className="text-muted-foreground">
                Notification settings will be implemented in the next phase
              </p>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold mb-4">Security Settings</h2>
              <p className="text-muted-foreground">
                Security settings will be implemented in the next phase
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SettingsPage
