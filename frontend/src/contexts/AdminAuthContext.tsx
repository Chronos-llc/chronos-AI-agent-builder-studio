import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

// Types
export interface AdminUser {
  id: number;
  user_id: number;
  role_id: number | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
  email: string;
  username: string;
  full_name: string | null;
  role_name: string | null;
  role_display_name: string | null;
}

export interface AdminRole {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  is_active: boolean;
  permissions: string[];
}

export type Permission = 
  | 'manage_users'
  | 'view_users'
  | 'ban_users'
  | 'manage_agents'
  | 'view_agents'
  | 'delete_agents'
  | 'manage_marketplace'
  | 'approve_listings'
  | 'reject_listings'
  | 'feature_listings'
  | 'manage_support'
  | 'view_support_tickets'
  | 'respond_to_tickets'
  | 'manage_system'
  | 'view_analytics'
  | 'manage_settings'
  | 'view_audit_logs';

interface AdminAuthContextType {
  adminUser: AdminUser | null;
  permissions: Permission[];
  isLoading: boolean;
  isAdmin: boolean;
  isSuperAdmin: boolean;
  hasPermission: (permission: Permission) => boolean;
  hasAnyPermission: (permissions: Permission[]) => boolean;
  hasAllPermissions: (permissions: Permission[]) => boolean;
  refreshAdminUser: () => Promise<void>;
  logout: () => void;
}

const AdminAuthContext = createContext<AdminAuthContextType | undefined>(undefined);

interface AdminAuthProviderProps {
  children: ReactNode;
}

export const AdminAuthProvider: React.FC<AdminAuthProviderProps> = ({ children }) => {
  const [adminUser, setAdminUser] = useState<AdminUser | null>(null);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Get API base URL from environment
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Fetch admin user data
  const fetchAdminUser = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      // Fetch admin user info
      const userResponse = await axios.get(`${API_BASE_URL}/api/v1/admin/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setAdminUser(userResponse.data);

      // Fetch admin permissions
      const permissionsResponse = await axios.get(`${API_BASE_URL}/api/v1/admin/me/permissions`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setPermissions(permissionsResponse.data);
    } catch (error) {
      console.error('Failed to fetch admin user:', error);
      setAdminUser(null);
      setPermissions([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Refresh admin user data
  const refreshAdminUser = async () => {
    setIsLoading(true);
    await fetchAdminUser();
  };

  // Logout
  const logout = () => {
    setAdminUser(null);
    setPermissions([]);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  // Check if user has specific permission
  const hasPermission = (permission: Permission): boolean => {
    return permissions.includes(permission);
  };

  // Check if user has any of the specified permissions
  const hasAnyPermission = (perms: Permission[]): boolean => {
    return perms.some(perm => permissions.includes(perm));
  };

  // Check if user has all of the specified permissions
  const hasAllPermissions = (perms: Permission[]): boolean => {
    return perms.every(perm => permissions.includes(perm));
  };

  // Check if user is admin
  const isAdmin = adminUser !== null && adminUser.is_active;

  // Check if user is super admin
  const isSuperAdmin = adminUser?.role_name === 'super_admin';

  // Fetch admin user on mount
  useEffect(() => {
    fetchAdminUser();
  }, []);

  const value: AdminAuthContextType = {
    adminUser,
    permissions,
    isLoading,
    isAdmin,
    isSuperAdmin,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    refreshAdminUser,
    logout,
  };

  return <AdminAuthContext.Provider value={value}>{children}</AdminAuthContext.Provider>;
};

// Custom hook to use admin auth context
export const useAdminAuth = () => {
  const context = useContext(AdminAuthContext);
  if (context === undefined) {
    throw new Error('useAdminAuth must be used within an AdminAuthProvider');
  }
  return context;
};

export default AdminAuthContext;
