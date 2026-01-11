import axios from 'axios';
import { AdminUser, AdminRole, Permission } from '../contexts/AdminAuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Get auth headers
const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
        Authorization: `Bearer ${token}`,
    };
};

// Admin user endpoints
export const adminService = {
    // Get current admin user
    getCurrentAdmin: async (): Promise<AdminUser> => {
        const response = await axios.get(`${API_BASE_URL}/api/v1/admin/me`, {
            headers: getAuthHeaders(),
        });
        return response.data;
    },

    // Get current admin permissions
    getCurrentAdminPermissions: async (): Promise<Permission[]> => {
        const response = await axios.get(`${API_BASE_URL}/api/v1/admin/me/permissions`, {
            headers: getAuthHeaders(),
        });
        return response.data;
    },

    // List all admin users
    listAdminUsers: async (params?: {
        skip?: number;
        limit?: number;
        is_active?: boolean;
        role_name?: string;
    }): Promise<AdminUser[]> => {
        const response = await axios.get(`${API_BASE_URL}/api/v1/admin/users`, {
            headers: getAuthHeaders(),
            params,
        });
        return response.data;
    },

    // Create admin user
    createAdminUser: async (data: {
        user_id: number;
        role_id: number;
        notes?: string;
    }): Promise<AdminUser> => {
        const response = await axios.post(`${API_BASE_URL}/api/v1/admin/users`, data, {
            headers: getAuthHeaders(),
        });
        return response.data;
    },

    // Update admin user
    updateAdminUser: async (
        adminUserId: number,
        data: {
            role_id?: number;
            is_active?: boolean;
            notes?: string;
        }
    ): Promise<AdminUser> => {
        const response = await axios.patch(
            `${API_BASE_URL}/api/v1/admin/users/${adminUserId}`,
            data,
            {
                headers: getAuthHeaders(),
            }
        );
        return response.data;
    },

    // Delete admin user
    deleteAdminUser: async (adminUserId: number): Promise<void> => {
        await axios.delete(`${API_BASE_URL}/api/v1/admin/users/${adminUserId}`, {
            headers: getAuthHeaders(),
        });
    },

    // List all roles
    listRoles: async (): Promise<AdminRole[]> => {
        const response = await axios.get(`${API_BASE_URL}/api/v1/admin/roles`, {
            headers: getAuthHeaders(),
        });
        return response.data;
    },

    // List audit logs
    listAuditLogs: async (params?: {
        skip?: number;
        limit?: number;
        action?: string;
        resource_type?: string;
    }): Promise<any[]> => {
        const response = await axios.get(`${API_BASE_URL}/api/v1/admin/audit-logs`, {
            headers: getAuthHeaders(),
            params,
        });
        return response.data;
    },

    // Get admin stats
    getAdminStats: async (): Promise<{
        total_admins: number;
        active_admins: number;
        total_audit_logs: number;
        recent_actions: number;
    }> => {
        const response = await axios.get(`${API_BASE_URL}/api/v1/admin/stats`, {
            headers: getAuthHeaders(),
        });
        return response.data;
    },
};

export default adminService;
