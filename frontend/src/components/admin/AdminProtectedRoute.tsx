import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAdminAuth, Permission } from '../../contexts/AdminAuthContext';

interface AdminProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission?: Permission;
  requiredPermissions?: Permission[];
  requireAll?: boolean; // If true, requires all permissions; if false, requires any permission
  fallbackPath?: string;
}

const AdminProtectedRoute: React.FC<AdminProtectedRouteProps> = ({
  children,
  requiredPermission,
  requiredPermissions,
  requireAll = false,
  fallbackPath = '/login',
}) => {
  const { isAdmin, isLoading, hasPermission, hasAnyPermission, hasAllPermissions } = useAdminAuth();
  const location = useLocation();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Redirect to login if not an admin
  if (!isAdmin) {
    return <Navigate to={fallbackPath} state={{ from: location }} replace />;
  }

  // Check single permission
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600">
            You don't have permission to access this page.
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Required permission: <code className="bg-gray-100 px-2 py-1 rounded">{requiredPermission}</code>
          </p>
        </div>
      </div>
    );
  }

  // Check multiple permissions
  if (requiredPermissions && requiredPermissions.length > 0) {
    const hasAccess = requireAll
      ? hasAllPermissions(requiredPermissions)
      : hasAnyPermission(requiredPermissions);

    if (!hasAccess) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-600">
              You don't have the required permissions to access this page.
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Required permissions ({requireAll ? 'all' : 'any'}):
            </p>
            <ul className="text-sm text-gray-500 mt-1">
              {requiredPermissions.map((perm) => (
                <li key={perm}>
                  <code className="bg-gray-100 px-2 py-1 rounded">{perm}</code>
                </li>
              ))}
            </ul>
          </div>
        </div>
      );
    }
  }

  // Render children if all checks pass
  return <>{children}</>;
};

export default AdminProtectedRoute;
