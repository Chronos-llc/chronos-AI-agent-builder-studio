# Admin Authentication and RBAC System Documentation

## Overview

The Chronos AI Agent Builder Studio implements a comprehensive Role-Based Access Control (RBAC) system for admin users. This system provides fine-grained permission management and audit logging for all admin actions.

## Architecture

### Database Models

#### AdminRole
Defines admin roles with associated permissions:
- `SUPER_ADMIN`: Full system access with all permissions
- `ADMIN`: Manage users, agents, and marketplace
- `MODERATOR`: Review and approve marketplace listings
- `SUPPORT`: Access support tickets and user data

#### AdminPermission
Defines granular permissions organized by resource and action:
- **User Management**: `manage_users`, `view_users`, `ban_users`
- **Agent Management**: `manage_agents`, `view_agents`, `delete_agents`
- **Marketplace Management**: `manage_marketplace`, `approve_listings`, `reject_listings`, `feature_listings`
- **Support Management**: `manage_support`, `view_support_tickets`, `respond_to_tickets`
- **System Management**: `manage_system`, `view_analytics`, `manage_settings`
- **Audit**: `view_audit_logs`

#### AdminUser
Links regular users to admin roles and tracks admin-specific data.

#### AdminAuditLog
Tracks all admin actions for compliance and security auditing.

## Backend Implementation

### RBAC Middleware (`backend/app/core/rbac.py`)

#### Key Functions

**`get_admin_user()`**
- Dependency that validates admin access
- Returns AdminUser with role and permissions loaded
- Raises 403 if user is not an admin or role is inactive

**`check_admin_permission()`**
- Checks if admin user has specific permission
- Super admins automatically have all permissions
- Returns boolean indicating permission status

**`log_admin_action()`**
- Logs admin actions to audit log
- Captures IP address, user agent, and action details
- Supports success/failure status tracking

#### Permission Decorators

**`@require_permission(permission)`**
- Decorator to require specific permission for endpoint
- Automatically checks permission and raises 403 if denied

**`@require_role(role)`**
- Decorator to require specific role for endpoint
- Super admins can access all role-restricted endpoints

#### AdminPermissionChecker Class

Helper class for checking permissions:
```python
checker = AdminPermissionChecker(admin_user)
checker.has_permission(PermissionEnum.MANAGE_USERS)
checker.has_any_permission([perm1, perm2])
checker.has_all_permissions([perm1, perm2])
checker.is_super_admin()
checker.get_permissions()
```

### API Endpoints (`backend/app/api/admin_auth.py`)

#### Admin User Management

**GET `/api/v1/admin/me`**
- Get current admin user information
- Returns admin profile with role and permissions

**GET `/api/v1/admin/me/permissions`**
- Get current admin user permissions
- Returns list of permission strings

**GET `/api/v1/admin/users`**
- List all admin users (requires `manage_users`)
- Supports filtering by active status and role

**POST `/api/v1/admin/users`**
- Create new admin user (requires `manage_users`)
- Assigns role and optional notes

**PATCH `/api/v1/admin/users/{id}`**
- Update admin user (requires `manage_users`)
- Can update role, active status, and notes

**DELETE `/api/v1/admin/users/{id}`**
- Delete admin user (requires `manage_users`)
- Cannot delete own admin account

#### Role Management

**GET `/api/v1/admin/roles`**
- List all admin roles with permissions
- Available to all admin users

#### Audit Logs

**GET `/api/v1/admin/audit-logs`**
- List audit logs (requires `view_audit_logs`)
- Supports filtering by action and resource type

**GET `/api/v1/admin/stats`**
- Get admin statistics
- Returns counts of admins and recent actions

## Frontend Implementation

### AdminAuthContext (`frontend/src/contexts/AdminAuthContext.tsx`)

React context providing admin authentication state and permission checking.

#### Context Values

```typescript
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
```

#### Usage

```tsx
import { AdminAuthProvider } from './contexts/AdminAuthContext';

function App() {
  return (
    <AdminAuthProvider>
      {/* Your app components */}
    </AdminAuthProvider>
  );
}
```

### AdminProtectedRoute Component

Protects routes requiring admin access and specific permissions.

#### Props

```typescript
interface AdminProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission?: Permission;
  requiredPermissions?: Permission[];
  requireAll?: boolean; // If true, requires all permissions
  fallbackPath?: string;
}
```

#### Usage

```tsx
import AdminProtectedRoute from './components/admin/AdminProtectedRoute';

// Require single permission
<AdminProtectedRoute requiredPermission="manage_users">
  <UserManagement />
</AdminProtectedRoute>

// Require any of multiple permissions
<AdminProtectedRoute 
  requiredPermissions={["view_users", "manage_users"]}
  requireAll={false}
>
  <UserList />
</AdminProtectedRoute>

// Require all permissions
<AdminProtectedRoute 
  requiredPermissions={["manage_marketplace", "feature_listings"]}
  requireAll={true}
>
  <FeaturedListings />
</AdminProtectedRoute>
```

### useAdminAuth Hook

Custom hook for accessing admin authentication context.

```tsx
import { useAdminAuth } from './hooks/useAdminAuth';

function MyComponent() {
  const { 
    adminUser, 
    permissions, 
    hasPermission,
    isSuperAdmin 
  } = useAdminAuth();

  if (!hasPermission('manage_users')) {
    return <div>Access denied</div>;
  }

  return <div>Welcome, {adminUser?.username}</div>;
}
```

### Admin Service (`frontend/src/services/adminService.ts`)

Service for making API calls to admin endpoints.

```typescript
import adminService from './services/adminService';

// Get current admin
const admin = await adminService.getCurrentAdmin();

// List admin users
const admins = await adminService.listAdminUsers({ is_active: true });

// Create admin user
const newAdmin = await adminService.createAdminUser({
  user_id: 123,
  role_id: 2,
  notes: 'New moderator'
});

// Get audit logs
const logs = await adminService.listAuditLogs({ limit: 50 });
```

## Database Migration

Run the migration to create admin tables:

```bash
cd backend
alembic upgrade head
```

The migration creates:
- `admin_roles` table with default roles
- `admin_permissions` table with default permissions
- `admin_role_permissions` association table
- `admin_users` table
- `admin_audit_logs` table

## Security Considerations

1. **Permission Checking**: All admin endpoints check permissions before allowing access
2. **Audit Logging**: All admin actions are logged with IP address and user agent
3. **Role Hierarchy**: Super admins have all permissions automatically
4. **Self-Protection**: Admins cannot delete their own admin account
5. **Token-Based Auth**: Uses existing JWT authentication system
6. **Active Status**: Inactive admin users cannot access admin endpoints

## Role Permissions Matrix

| Permission | Super Admin | Admin | Moderator | Support |
|-----------|-------------|-------|-----------|---------|
| manage_users | ✓ | ✓ | ✗ | ✗ |
| view_users | ✓ | ✓ | ✓ | ✓ |
| ban_users | ✓ | ✓ | ✗ | ✗ |
| manage_agents | ✓ | ✓ | ✗ | ✗ |
| view_agents | ✓ | ✓ | ✓ | ✓ |
| delete_agents | ✓ | ✓ | ✗ | ✗ |
| manage_marketplace | ✓ | ✓ | ✗ | ✗ |
| approve_listings | ✓ | ✓ | ✓ | ✗ |
| reject_listings | ✓ | ✓ | ✓ | ✗ |
| feature_listings | ✓ | ✓ | ✗ | ✗ |
| manage_support | ✓ | ✗ | ✗ | ✓ |
| view_support_tickets | ✓ | ✗ | ✓ | ✓ |
| respond_to_tickets | ✓ | ✗ | ✓ | ✓ |
| manage_system | ✓ | ✗ | ✗ | ✗ |
| view_analytics | ✓ | ✓ | ✗ | ✗ |
| manage_settings | ✓ | ✗ | ✗ | ✗ |
| view_audit_logs | ✓ | ✗ | ✗ | ✗ |

## Creating Your First Admin User

After running migrations, you need to manually create the first admin user in the database:

```sql
-- First, find the user ID you want to make an admin
SELECT id, email, username FROM users WHERE email = 'admin@example.com';

-- Get the super_admin role ID
SELECT id, name FROM admin_roles WHERE name = 'SUPER_ADMIN';

-- Create the admin user (replace user_id and role_id with actual values)
INSERT INTO admin_users (user_id, role_id, is_active, notes)
VALUES (1, 1, true, 'Initial super admin');
```

Alternatively, create a script to do this programmatically.

## Best Practices

1. **Principle of Least Privilege**: Assign the minimum role needed for each admin
2. **Regular Audits**: Review audit logs regularly for suspicious activity
3. **Role Reviews**: Periodically review admin users and their roles
4. **Deactivate, Don't Delete**: Deactivate admin users instead of deleting to preserve audit trail
5. **Document Changes**: Use the notes field to document why admin access was granted
6. **Monitor Failed Attempts**: Watch for repeated permission denied errors in logs

## Extending the System

### Adding New Permissions

1. Add to `PermissionEnum` in `backend/app/models/admin.py`
2. Update `ROLE_PERMISSIONS` mapping in `backend/app/core/rbac.py`
3. Add to migration in `backend/alembic/versions/admin_roles.py`
4. Update frontend `Permission` type in `frontend/src/contexts/AdminAuthContext.tsx`

### Adding New Roles

1. Add to `AdminRoleEnum` in `backend/app/models/admin.py`
2. Add role permissions to `ROLE_PERMISSIONS` in `backend/app/core/rbac.py`
3. Add to migration in `backend/alembic/versions/admin_roles.py`

### Custom Permission Checks

```python
from app.core.rbac import get_admin_user, check_admin_permission

@router.get("/custom-endpoint")
async def custom_endpoint(
    admin_user: AdminUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    # Custom permission logic
    has_perm1 = await check_admin_permission(admin_user, PermissionEnum.MANAGE_USERS, db)
    has_perm2 = await check_admin_permission(admin_user, PermissionEnum.VIEW_ANALYTICS, db)
    
    if not (has_perm1 and has_perm2):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Your endpoint logic
    return {"message": "Success"}
```

## Troubleshooting

### Admin User Cannot Access Endpoints

1. Check if admin user exists in `admin_users` table
2. Verify `is_active` is `true`
3. Check if role is assigned and active
4. Verify JWT token is valid and not expired

### Permission Denied Errors

1. Check role permissions in `ROLE_PERMISSIONS` mapping
2. Verify admin user has correct role assigned
3. Check audit logs for permission check failures

### Audit Logs Not Recording

1. Verify `log_admin_action()` is called in endpoint
2. Check database connection
3. Verify admin_user_id is valid

## API Response Examples

### Get Current Admin User

```json
{
  "id": 1,
  "user_id": 5,
  "role_id": 1,
  "is_active": true,
  "notes": "System administrator",
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": "2026-01-10T12:00:00Z",
  "email": "admin@example.com",
  "username": "admin",
  "full_name": "Admin User",
  "role_name": "super_admin",
  "role_display_name": "Super Administrator"
}
```

### Get Permissions

```json
[
  "manage_users",
  "view_users",
  "ban_users",
  "manage_agents",
  "view_agents",
  "delete_agents",
  "manage_marketplace",
  "approve_listings",
  "reject_listings",
  "feature_listings",
  "manage_support",
  "view_support_tickets",
  "respond_to_tickets",
  "manage_system",
  "view_analytics",
  "manage_settings",
  "view_audit_logs"
]
```

### Audit Log Entry

```json
{
  "id": 123,
  "admin_user_id": 1,
  "action": "create_admin_user",
  "resource_type": "admin_user",
  "resource_id": 5,
  "details": "{\"user_id\": 10, \"role_id\": 3}",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "status": "success",
  "created_at": "2026-01-10T12:30:00Z",
  "admin_username": "admin",
  "admin_email": "admin@example.com"
}
```
