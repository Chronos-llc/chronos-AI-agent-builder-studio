# Environment Configuration Plan for Chronos AI Agent Builder Studio

## Overview

This plan outlines the steps to:
1. Fix all hardcoded endpoints in both frontend and backend
2. Create proper .env.example files with comprehensive documentation
3. Provide hosting recommendations for both frontend and backend

## Current State Analysis

### Frontend
- No .env file exists in the frontend directory
- Services use relative paths or hardcoded `http://localhost:8000`
- adminService.ts uses `import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'`
- Other services (marketplaceService.ts, fuzzyService.ts, etc.) use relative paths like `/api/marketplace`

### Backend
- Has .env and .env.example files
- Configuration is managed in `backend/app/core/config.py`
- Some defaults are hardcoded (e.g., database URL, Redis URL)

## Action Items

### 1. Create Frontend Environment Files

#### 1.1 Create `frontend/.env`
```env
# Frontend Environment Configuration for Chronos AI Agent Builder Studio

# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000

# Application Settings
VITE_APP_NAME=Chronos AI Agent Builder Studio
VITE_ENVIRONMENT=development
VITE_DEBUG=true

# Feature Flags
VITE_ENABLE_MARKETPLACE=true
VITE_ENABLE_FUZZY_TOOLS=true
VITE_ENABLE_META_AGENT=true
VITE_ENABLE_PLATFORM_UPDATES=true
VITE_ENABLE_SUPPORT_SYSTEM=true

# Storage Settings
VITE_LOCAL_STORAGE_PREFIX=chronos_

# UI Settings
VITE_THEME=light
VITE_LANGUAGE=en
```

#### 1.2 Create `frontend/.env.example`
```env
# Frontend Environment Configuration for Chronos AI Agent Builder Studio
# Copy this file to .env and update the values according to your environment

# API Configuration
# Base URL for the backend API
VITE_API_BASE_URL=http://localhost:8000

# WebSocket Configuration
# Base URL for WebSocket connections
VITE_WS_BASE_URL=ws://localhost:8000

# Application Settings
VITE_APP_NAME=Chronos AI Agent Builder Studio
VITE_ENVIRONMENT=development
VITE_DEBUG=true

# Feature Flags
VITE_ENABLE_MARKETPLACE=true
VITE_ENABLE_FUZZY_TOOLS=true
VITE_ENABLE_META_AGENT=true
VITE_ENABLE_PLATFORM_UPDATES=true
VITE_ENABLE_SUPPORT_SYSTEM=true

# Storage Settings
VITE_LOCAL_STORAGE_PREFIX=chronos_

# UI Settings
VITE_THEME=light
VITE_LANGUAGE=en
```

### 2. Fix Frontend Hardcoded Endpoints

#### 2.1 Update Services to Use Environment Variables

**File: `frontend/src/services/adminService.ts`**
```typescript
// Current
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// No change needed - already uses environment variable
```

**File: `frontend/src/services/marketplaceService.ts`**
```typescript
// Current
const API_BASE = '/api/marketplace';

// Update to
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api/marketplace`;
```

**File: `frontend/src/services/fuzzyService.ts`**
```typescript
// Current
const API_BASE = '/api/fuzzy-tools';

// Update to
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api/fuzzy-tools`;
```

**File: `frontend/src/services/configManagementService.ts`**
```typescript
// Check and update similar to above
```

**File: `frontend/src/services/metaAgentService.ts`**
```typescript
// Check and update similar to above
```

**File: `frontend/src/services/paymentService.ts`**
```typescript
// Check and update similar to above
```

**File: `frontend/src/services/platformUpdatesService.ts`**
```typescript
// Check and update similar to above
```

**File: `frontend/src/services/skillsService.ts`**
```typescript
// Check and update similar to above
```

**File: `frontend/src/services/supportService.ts`**
```typescript
// Check and update similar to above
```

**File: `frontend/src/services/systemOptimizationService.ts`**
```typescript
// Check and update similar to above
```

**File: `frontend/src/services/workflowGenerationService.ts`**
```typescript
// Check and update similar to above
```

#### 2.2 Update WebSocket Hook

**File: `frontend/src/hooks/useWebSocket.ts`**
```typescript
// When using the hook, pass the WebSocket URL from environment variable
const wsUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';
```

### 3. Update Backend Configuration

#### 3.1 Check for Hardcoded Endpoints in Backend

**File: `backend/app/core/config.py`**
- Check for any hardcoded external API endpoints
- Ensure all configurable values are properly exposed as environment variables

#### 3.2 Update Backend .env.example

Add any missing configuration options with documentation

### 4. Hosting Recommendations

#### 4.1 Frontend Hosting Options

1. **Vercel** (Recommended)
   - Easy deployment from Git
   - Automatic SSL
   - Serverless functions
   - Great for React/Vite apps

2. **Netlify**
   - Simple to deploy
   - Free tier available
   - CDN and edge functions

3. **AWS S3 + CloudFront**
   - Scalable
   - Cost-effective for large apps
   - Requires more configuration

4. **GitHub Pages**
   - Free for public repositories
   - Good for static sites

#### 4.2 Backend Hosting Options

1. **Render** (Recommended for Small/Medium Apps)
   - Easy deployment
   - PostgreSQL and Redis available
   - Free tier available

2. **Heroku**
   - Simple deployment
   - Add-ons for databases
   - Free tier available

3. **AWS Elastic Beanstalk**
   - Scalable
   - Good for production apps
   - Requires more configuration

4. **DigitalOcean App Platform**
   - Modern deployment platform
   - PostgreSQL and Redis available
   - Competitive pricing

5. **Docker + Kubernetes**
   - For complex, scalable applications
   - Requires significant DevOps expertise

#### 4.3 Database Hosting

1. **Supabase** (PostgreSQL)
   - Open source
   - Real-time capabilities
   - Free tier available

2. **Neon** (PostgreSQL)
   - Serverless PostgreSQL
   - Free tier available

3. **AWS RDS**
   - Managed PostgreSQL/MySQL
   - Scalable
   - Enterprise-grade

4. **Redis Labs**
   - Managed Redis
   - Free tier available

#### 4.4 Environment Variable Management

- Use .gitignore to exclude .env files
- Use environment variable management tools like:
  - Vercel Environment Variables
  - Netlify Environment Variables
  - AWS Secrets Manager
  - Doppler

### 5. Implementation Steps

1. Create frontend .env and .env.example files
2. Update all frontend service files to use environment variables
3. Check backend for hardcoded endpoints
4. Update backend config.py if needed
5. Update backend .env.example with comprehensive documentation
6. Test the changes locally
7. Update deployment scripts if needed

## Verification

- Test all API endpoints are working correctly
- Test WebSocket connections
- Verify all features function in development environment
- Test production build
