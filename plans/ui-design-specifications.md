# Chronos AI Agent Builder Studio - UI/UX Design Specifications

## Design System Overview

Based on the reference images, the interface follows a modern, clean design with:

### Visual Design Principles

- **Clean Minimalism**: White backgrounds with subtle shadows and rounded corners
- **Card-based Layout**: Information organized in distinct cards with clear boundaries
- **Consistent Spacing**: Uniform padding and margins throughout the interface
- **Modern Typography**: Clean, readable fonts with proper hierarchy
- **Subtle Interactions**: Smooth hover effects and transitions

### Color Scheme

- **Primary Background**: Clean white (#FFFFFF)
- **Card Backgrounds**: White with subtle shadows
- **Primary Text**: Dark gray/black for maximum readability
- **Secondary Text**: Medium gray for supporting information
- **Accent Colors**: Blue for primary actions, green for success states
- **Border Colors**: Light gray (#E5E7EB) for subtle separation

### Component Styling

- **Cards**: Rounded corners (8px), subtle box-shadow, clean padding
- **Buttons**: Rounded corners (6px), clear hover states, consistent sizing
- **Input Fields**: Clean borders, focus states, proper validation styling
- **Navigation**: Clean, intuitive iconography with text labels

## Layout Structure

### Main Layout

```
┌─────────────────────────────────────────────────────────┐
│                    Top Header                           │
│  [Logo] [Navigation Items]           [User Menu]       │
├─────────────────────────────────────────────────────────┤
│                        │                                │
│      Sidebar           │        Main Content           │
│    Navigation          │         Area                   │
│                        │                                │
│  • Dashboard           │   ┌─────────────────────────┐   │
│  • Actions             │   │                         │   │
│  • Hooks               │   │    Page Content         │   │
│  • Versions            │   │                         │   │
│  • Integrations        │   │                         │   │
│  • Bot Settings        │   │                         │   │
│                        │   └─────────────────────────┘   │
└─────────────────────────┴────────────────────────────────┘
```

### Page-Specific Layouts

#### 1. Dashboard/Home Page

- **Welcome Section**: User greeting and quick stats
- **Recent Agents**: Card grid showing recently created/edited agents
- **Quick Actions**: Prominent buttons for common tasks
- **Activity Feed**: Recent activity across the platform

#### 2. Actions Page

```
┌─────────────────────────────────────────────────────────┐
│ Actions Management                                      │
├─────────────────────────────────────────────────────────┤
│ [Create New Action] [Search] [Filter]                   │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Custom Action│ │ AI Generated │ │  Template   │        │
│ │             │ │             │ │             │        │
│ │ [Edit] [Del]│ │ [Edit] [Del]│ │ [Use] [Del] │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
└─────────────────────────────────────────────────────────┘
```

#### 3. Hooks Page

```
┌─────────────────────────────────────────────────────────┐
│ Hooks Management                                        │
├─────────────────────────────────────────────────────────┤
│ [Create Hook] [Search] [Filter by Trigger Type]        │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Before Agent Startup                                │ │
│ │ Trigger: Agent Start                                │ │
│ │ [Edit] [Delete] [Toggle Active]                     │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ After Action Execution                              │ │
│ │ Trigger: Action Complete                            │ │
│ │ [Edit] [Delete] [Toggle Active]                     │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 4. Integrations Hub

```
┌─────────────────────────────────────────────────────────┐
│ Chronos Integrations Hub                                │
├─────────────────────────────────────────────────────────┤
│ [Browse All] [Installed] [Updates Available]            │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Telegram    │ │ OpenAI      │ │ File System │        │
│ │ Bot         │ │ Provider    │ │ MCP Server  │        │
│ │             │ │             │ │             │        │
│ │ [Install]   │ │ [Install]   │ │ [Install]   │        │
│ │ [Details]   │ │ [Details]   │ │ [Details]   │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
└─────────────────────────────────────────────────────────┘
```

#### 5. Bot Settings Page

```
┌─────────────────────────────────────────────────────────┐
│ Bot Settings                                            │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Basic Information                                    │ │
│ │ Bot Name: [________________]                         │ │
│ │ Description: [________________________]             │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Workflow Options                                     │ │
│ │ Inactivity Timeout: [30] seconds                    │ │
│ │ Node Repetition Limit: [3] minutes                  │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Chronos Client                                       │ │
│ │ ☑ Enable Chronos Client Integration                 │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ LLM Configuration                                    │ │
│ │ Default Fast LLM: [OpenAI GPT-4] ▼                  │ │
│ │ Default Best LLM: [OpenAI GPT-4] ▼                  │ │
│ │ Autonomous LLM: [Claude-3] ▼                        │ │
│ │ RAG LLM: [Custom RAG Model] ▼                       │ │
│ │ Fallback LLM: [GPT-3.5] ▼                           │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Configuration Variables                              │ │
│ │ [Add Variable]                                       │ │
│ │ VAR_NAME    value    [Delete]                       │ │
│ │ ANOTHER_VAR value    [Delete]                       │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 6. Version Management

```
┌─────────────────────────────────────────────────────────┐
│ Agent Versions                                          │
├─────────────────────────────────────────────────────────┤
│ [Create Version] [Compare Versions]                     │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ v1.2.3 - Current                                     │ │
│ │ Created: Dec 28, 2024 3:47 PM                       │ │
│ │ Changes: Added Telegram integration                  │ │
│ │ [Rollback] [View Details] [Export]                   │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ v1.2.2                                               │ │
│ │ Created: Dec 27, 2024 10:15 AM                      │ │
│ │ Changes: Updated LLM configuration                   │ │
│ │ [Rollback] [View Details] [Export]                   │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Component Specifications

### Cards

```css
.card {
  background: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 16px;
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

### Buttons

```css
.btn-primary {
  background: #3B82F6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-primary:hover {
  background: #2563EB;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #F9FAFB;
  border-color: #9CA3AF;
}
```

### Input Fields

```css
.input-field {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.input-field:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
```

### Navigation

```css
.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: #6B7280;
  text-decoration: none;
  border-radius: 6px;
  margin-bottom: 4px;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: #F3F4F6;
  color: #111827;
}

.nav-item.active {
  background: #EBF8FF;
  color: #1E40AF;
}
```

## Responsive Design

### Breakpoints

- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### Mobile Adaptations

- Collapsible sidebar navigation
- Stack cards vertically
- Simplified navigation menu
- Touch-friendly button sizes (minimum 44px)

### Tablet Adaptations

- Adjust card grid columns
- Maintain readable text sizes
- Optimize touch interactions

## Accessibility Features

### Color Contrast

- Minimum 4.5:1 contrast ratio for normal text
- Minimum 3:1 contrast ratio for large text
- Support for color blindness

### Keyboard Navigation

- Full keyboard navigation support
- Visible focus indicators
- Logical tab order

### Screen Reader Support

- Proper ARIA labels
- Semantic HTML structure
- Alternative text for images

### Visual Accessibility

- Support for reduced motion preferences
- Scalable fonts and UI elements
- High contrast mode support

## Interactive Elements

### Loading States

- Skeleton loading for cards and lists
- Progress indicators for long operations
- Smooth transitions between states

### Feedback Messages

- Success notifications (green)
- Error messages (red)
- Warning notifications (yellow)
- Info messages (blue)

### Form Validation

- Real-time validation feedback
- Clear error messages
- Visual indicators for required fields
- Success states for valid inputs

## Performance Considerations

### Loading Optimization

- Lazy loading for images and components
- Code splitting for route-based chunks
- Preloading for critical resources

### Caching Strategy

- API response caching
- Static asset caching
- Intelligent cache invalidation

### Bundle Optimization

- Tree shaking for unused code
- Asset compression and minification
- Critical CSS inlining

This design specification ensures a modern, accessible, and performant user experience that aligns with the visual references provided.
