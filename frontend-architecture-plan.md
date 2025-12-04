# Mentor AI Frontend Architecture Plan

## Project Overview

This document outlines the architecture for building two separate Next.js applications for the Mentor AI EdTech Platform:
1. **Parent Application** - For parents to manage their child's learning journey
2. **Student Application** - For students to access learning materials and take tests

## Technology Stack

### Core Framework
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **React 18** with Server Components

### UI Components & Styling
- **Aceternity UI** (https://ui.aceternity.com/components) for beautiful UI components
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Lucide React** for icons

### API & Data Management
- **Axios** for HTTP requests
- **React Query (TanStack Query)** for server state management
- **Zustand** for client state management
- **React Hook Form** for form handling
- **Zod** for schema validation

### Internationalization
- **next-i18next** for multilingual support
- **English and Hindi** (initially)

### Development Tools
- **ESLint** for code linting
- **Prettier** for code formatting
- **Husky** for git hooks
- **Jest & Testing Library** for testing

## Project Structure

```
frontend/
├── shared/                    # Shared code between both apps
│   ├── components/           # Reusable UI components
│   ├── hooks/               # Custom hooks
│   ├── utils/               # Utility functions
│   ├── types/               # TypeScript type definitions
│   ├── constants/           # App constants
│   └── api/                 # API layer and configurations
├── parent-app/               # Parent Next.js application
│   ├── app/                 # App Router pages
│   ├── components/          # Parent-specific components
│   ├── hooks/               # Parent-specific hooks
│   └── public/              # Static assets
└── student-app/              # Student Next.js application
    ├── app/                 # App Router pages
    ├── components/          # Student-specific components
    ├── hooks/               # Student-specific hooks
    └── public/              # Static assets
```

## Authentication Architecture

### JWT Token Management
- Access tokens (short-lived: 24 hours)
- Refresh tokens (long-lived: 30 days)
- Automatic token refresh on expiry
- Secure token storage in httpOnly cookies

### Auth Flow
1. User login with email/password or Google OAuth
2. Receive access and refresh tokens
3. Store tokens securely
4. Include access token in API requests
5. Refresh token automatically when needed
6. Logout clears all tokens

## API Integration Strategy

### Base Configuration
```typescript
// shared/api/axios.ts
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
  withCredentials: true,
});

// Request interceptor for auth token
apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await refreshToken();
      return apiClient.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

### API Services Structure
```typescript
// shared/api/services/auth.ts
export const authService = {
  login: (credentials: LoginCredentials) => 
    apiClient.post('/api/auth/login/email', credentials),
  
  register: (userData: RegisterData) => 
    apiClient.post('/api/auth/register/simple', userData),
  
  refreshToken: () => 
    apiClient.post('/api/auth/refresh'),
  
  logout: () => 
    apiClient.post('/api/auth/logout'),
};
```

## Component Architecture

### Shared Component Library
```typescript
// shared/components/ui/
├── Button.tsx
├── Input.tsx
├── Card.tsx
├── Modal.tsx
├── Loading.tsx
├── ErrorBoundary.tsx
└── index.ts
```

### Feature-Specific Components
```typescript
// parent-app/components/
├── auth/
├── dashboard/
├── child-management/
├── analytics/
└── payments/

// student-app/components/
├── auth/
├── dashboard/
├── tests/
├── study-center/
└── gamification/
```

## State Management

### Server State (React Query)
```typescript
// shared/hooks/queries/useAuth.ts
export const useAuth = () => {
  return useQuery({
    queryKey: ['auth'],
    queryFn: authService.getCurrentUser,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
```

### Client State (Zustand)
```typescript
// shared/store/authStore.ts
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  login: (user) => set({ user, isAuthenticated: true }),
  logout: () => set({ user: null, isAuthenticated: false }),
}));
```

## Internationalization Implementation

### Configuration
```typescript
// next-i18next.config.js
module.exports = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'hi'],
  },
  backend: {
    loadPath: '/locales/{{lng}}/{{ns}}.json',
  },
};
```

### Language Switcher Component
```typescript
// shared/components/LanguageSwitcher.tsx
import { useRouter } from 'next/router';
import { useTranslation } from 'next-i18next';

export const LanguageSwitcher = () => {
  const router = useRouter();
  const { t } = useTranslation('common');
  
  const changeLanguage = (locale: string) => {
    router.push(router.asPath, router.asPath, { locale });
  };
  
  return (
    <div>
      <button onClick={() => changeLanguage('en')}>English</button>
      <button onClick={() => changeLanguage('hi')}>हिंदी</button>
    </div>
  );
};
```

## Parent Application Features

### 1. Authentication Flow
- Email/Password login
- Google OAuth integration
- Email verification
- Password reset

### 2. Dashboard
- Child overview cards
- Learning progress summary
- Recent activities
- Quick actions

### 3. Child Management
- Add/edit child profile
- Exam selection
- Subject preferences
- Learning goals

### 4. Analytics & Reports
- Performance charts
- Progress reports
- Strength/weakness analysis
- Time spent tracking

### 5. Payments & Subscriptions
- Subscription plans
- Payment gateway integration
- Transaction history
- Invoice management

## Student Application Features

### 1. Authentication Flow
- Student login with parent credentials
- Profile selection (if multiple children)

### 2. Dashboard
- Daily learning plan
- Progress overview
- Upcoming tests
- Achievement badges

### 3. Diagnostic Tests
- Test interface
- Timer functionality
- Question navigation
- Result analysis

### 4. Study Center
- Learning materials
- Video lessons
- Practice questions
- Bookmark system

### 5. AI Features
- Vidhya AI chat interface
- Personalized recommendations
- Doubt resolution
- Study suggestions

### 6. Gamification
- Achievement system
- Daily challenges
- Learning streaks
- Points and rewards

## Responsive Design Strategy

### Breakpoints
- Mobile: 320px - 768px
- Tablet: 768px - 1024px
- Desktop: 1024px+

### Mobile-First Approach
- Progressive enhancement
- Touch-friendly interfaces
- Optimized performance
- PWA capabilities

## Error Handling & User Feedback

### Error Boundaries
```typescript
// shared/components/ErrorBoundary.tsx
export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }

    return this.props.children;
  }
}
```

### Toast Notifications
- Success messages
- Error alerts
- Loading indicators
- Progress updates

## Testing Strategy

### Unit Tests
- Component testing with React Testing Library
- Hook testing
- Utility function testing

### Integration Tests
- API integration testing
- User flow testing
- Cross-component interactions

### E2E Tests
- Critical user journeys
- Authentication flows
- Payment processes

## Deployment Configuration

### Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
NEXT_PUBLIC_RAZORPAY_KEY=your_razorpay_key
```

### Build Optimization
- Code splitting by routes
- Image optimization
- Bundle analysis
- Performance monitoring

## Security Considerations

### Data Protection
- HTTPS enforcement
- XSS prevention
- CSRF protection
- Input sanitization

### Authentication Security
- Secure token storage
- Session management
- Rate limiting
- Account lockout

## Performance Optimization

### Code Splitting
- Dynamic imports
- Route-based splitting
- Component lazy loading

### Caching Strategy
- API response caching
- Static asset caching
- Browser caching

### Image Optimization
- Next.js Image component
- Responsive images
- WebP format support

## Accessibility Features

### WCAG 2.1 Compliance
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support

### Focus Management
- Skip links
- Focus indicators
- Modal focus trapping

## Analytics & Monitoring

### User Analytics
- Page views
- User engagement
- Feature usage
- Conversion tracking

### Performance Monitoring
- Core Web Vitals
- Error tracking
- API performance
- Resource loading

## Implementation Timeline

### Phase 1: Foundation (Week 1-2)
- Project setup and configuration
- Authentication system
- Basic UI components
- API integration layer

### Phase 2: Core Features (Week 3-4)
- Parent app dashboard
- Student app dashboard
- Child management
- Basic test interface

### Phase 3: Advanced Features (Week 5-6)
- Study center
- AI features integration
- Analytics and reports
- Payment system

### Phase 4: Polish & Launch (Week 7-8)
- Responsive design
- Performance optimization
- Testing and bug fixes
- Deployment preparation

## Conclusion

This architecture provides a solid foundation for building scalable, maintainable, and user-friendly frontend applications for the Mentor AI EdTech Platform. The separation of parent and student applications allows for tailored user experiences while maintaining code reusability through shared components and utilities.