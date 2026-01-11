# Chronos AI Agent Builder Studio - Admin Studio

## Overview

The Admin Studio is a unified administrative interface for managing all aspects of the Chronos AI Agent Builder platform. It implements a mode-switching architecture that allows administrators to seamlessly switch between different administrative functions without navigating to separate applications.

## Architecture

The admin studio follows a unified layout with mode switching rather than separate studios. This provides:

- **Single Entry Point**: All admin functions accessible from one interface
- **Consistent UX**: Unified navigation and layout across all admin modes
- **Efficient Workflow**: Quick mode switching without page reloads
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Components

### Core Components

#### 1. AdminStudioLayout

**File**: `AdminStudioLayout.tsx`

The main layout component that orchestrates the entire admin interface.

**Features**:

- Responsive sidebar navigation
- Mode switching interface
- Header with search and notifications
- Dynamic content area based on selected mode

**Usage**:

```tsx
import { AdminStudioLayout } from './components/admin/AdminStudioLayout'

function AdminPage() {
    return <AdminStudioLayout />
}
```

#### 2. AdminHeader

**File**: `AdminHeader.tsx`

Top navigation bar with user controls and notifications.

**Features**:

- Global search functionality
- Alert notifications with unread count
- User profile dropdown
- Responsive mobile menu

**Props**:

```typescript
{
    user: AdminUser
    alerts?: AdminAlert[]
    onSearch?: (query: string) => void
}
```

#### 3. AdminNavigation

**File**: `AdminNavigation.tsx`

Collapsible sidebar navigation with hierarchical menu structure.

**Features**:

- Expandable/collapsible menu items
- Active state highlighting
- Icon-based navigation
- Default navigation structure

**Props**:

```typescript
{
    items: AdminNavigationItem[]
    activeItemId?: string
    onNavigate: (path: string) => void
}
```

#### 4. ModeSwitcher

**File**: `ModeSwitcher.tsx`

Quick mode switching interface displayed prominently in the layout.

**Features**:

- Visual mode selection
- Icon-based mode identification
- Tooltips with mode descriptions
- Responsive grid layout

**Props**:

```typescript
{
    currentMode: AdminMode
    onModeChange: (mode: AdminMode) => void
}
```

#### 5. AdminDashboard

**File**: `AdminDashboard.tsx`

Main dashboard view with statistics and quick actions.

**Features**:

- System statistics cards
- Recent activity feed
- Quick action buttons
- System health indicators

**Props**:

```typescript
{
    statistics: AdminStatistics
    recentActivity?: Activity[]
    quickActions?: QuickAction[]
}
```

## Admin Modes

The admin studio supports the following modes:

### 1. Meta Agents (`meta-agents`)

Manage meta agents and their configurations.

### 2. Subagents (`subagents`)

Create and manage subagents for meta agents.

### 3. Marketplace (`marketplace`)

Administer marketplace listings, categories, and tags.

### 4. Skills (`skills`)

Manage agent skills and capabilities library.

### 5. Platform Updates (`platform-updates`)

Handle platform updates, versioning, and changelog.

### 6. Support (`support`)

Manage support tickets and knowledge base.

### 7. Payments (`payments`)

Handle billing, transactions, and subscriptions.

## Type Definitions

**File**: `frontend/src/types/admin.ts`

Key types include:

```typescript
type AdminMode = 
    'meta-agents' | 
    'subagents' | 
    'marketplace' | 
    'skills' | 
    'platform-updates' | 
    'support' | 
    'payments'

interface AdminUser {
    id: string
    name: string
    email: string
    role: 'admin' | 'super-admin' | 'moderator'
    permissions: string[]
    last_login: string
    status: 'active' | 'inactive' | 'suspended'
}

interface AdminStatistics {
    total_users: number
    active_agents: number
    marketplace_listings: number
    pending_support_tickets: number
    revenue: number
    system_health: 'good' | 'warning' | 'critical'
}
```

## Styling

**File**: `AdminStudio.css`

The admin studio has its own styling to differentiate it from the user studio:

- Custom color scheme
- Smooth animations for mode switching
- Responsive breakpoints
- Custom scrollbar styling

## Routing

The admin studio is accessible at `/admin/*` and requires authentication.

**App.tsx Integration**:

```tsx
<Route
    path="/admin/*"
    element={
        <ProtectedRoute>
            <AdminPage />
        </ProtectedRoute>
    }
/>
```

## Responsive Design

The admin studio is fully responsive:

- **Desktop (≥768px)**: Full sidebar navigation visible
- **Mobile (<768px)**: Collapsible sidebar, hamburger menu
- **Tablet**: Adaptive layout with optimized spacing

## Future Enhancements

The current implementation provides the foundation for:

1. **Mode-Specific Components**: Each mode will have dedicated components
2. **Real-time Updates**: WebSocket integration for live data
3. **Advanced Analytics**: Detailed charts and reporting
4. **Bulk Operations**: Multi-select and batch actions
5. **Role-Based Access**: Granular permission controls per mode

## Development Notes

- All components use TypeScript with strict typing
- Follows existing UI patterns from the component library
- Uses Tailwind CSS for styling
- Implements proper error boundaries (to be added)
- Supports dark/light theme (inherited from app theme)

## Testing

To test the admin studio:

1. Navigate to `/admin` after authentication
2. Try switching between different modes
3. Test responsive behavior by resizing the browser
4. Verify navigation and search functionality

## Contributing

When adding new admin modes:

1. Add the mode type to `AdminMode` in `types/admin.ts`
2. Add mode configuration to `ModeSwitcher.tsx`
3. Add navigation items to `AdminNavigation.tsx`
4. Implement mode-specific component
5. Add mode rendering logic to `AdminStudioLayout.tsx`
