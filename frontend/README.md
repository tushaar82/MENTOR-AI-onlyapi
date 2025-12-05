# Mentor AI Frontend

A modern, AI-powered learning platform built with Next.js, TypeScript, and Tailwind CSS.

## Features

### Authentication
- User registration and login with email/password
- Role-based access (Student/Parent)
- JWT token management with automatic refresh
- Protected routes with middleware
- Persistent authentication state

### UI/UX
- Modern neumorphism design
- Responsive layout
- Beautiful gradient backgrounds
- Smooth animations and transitions
- Accessible components with ARIA labels

### Technology Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Shadcn UI
- **Form Handling**: React Hook Form with Zod validation
- **Icons**: Lucide React
- **Authentication**: JWT-based custom implementation

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── auth/              # Authentication pages
│   │   │   ├── login/         # Login page
│   │   │   └── register/      # Registration page
│   │   ├── dashboard/         # Protected dashboard
│   │   ├── layout.tsx         # Root layout with AuthProvider
│   │   ├── page.tsx          # Landing page
│   │   └── globals.css       # Global styles
│   ├── components/            # Reusable components
│   │   ├── auth/             # Authentication components
│   │   │   ├── LoginForm.tsx  # Login form component
│   │   │   └── RegisterForm.tsx # Registration form
│   │   └── ui/               # UI components
│   │       ├── button.tsx     # Button component
│   │       ├── card.tsx       # Card component
│   │       ├── input.tsx      # Input component
│   │       ├── label.tsx      # Label component
│   │       ├── tabs.tsx       # Tabs component
│   │       └── neumorph-button.tsx # Custom neumorphic button
│   ├── context/              # React contexts
│   │   └── AuthContext.tsx   # Authentication context
│   ├── lib/                  # Utility libraries
│   │   ├── auth/             # Authentication utilities
│   │   │   ├── api.ts        # API client
│   │   │   └── utils.ts      # Auth helper functions
│   │   └── utils.ts          # General utilities
│   ├── types/                # TypeScript type definitions
│   │   └── auth.ts           # Auth-related types
│   └── middleware.ts         # Next.js middleware for route protection
├── .env.local               # Environment variables
├── components.json           # Shadcn UI configuration
├── package.json             # Dependencies and scripts
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json           # TypeScript configuration
```

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local` with your configuration:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Authentication Flow

### Registration
1. Navigate to `/auth/register`
2. Select role (Student or Parent)
3. Fill in personal information
4. Create password
5. Submit form

### Login
1. Navigate to `/auth/login`
2. Enter email and password
3. Submit form
4. Redirect to dashboard

### Protected Routes
- Dashboard and other protected routes require authentication
- Middleware redirects unauthenticated users to login
- Authenticated users are redirected from auth pages to dashboard

## API Integration

The frontend is configured to work with the backend API at `http://localhost:8000`. Key endpoints:

- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Token refresh

## UI Components

### Neumorphic Design
- Custom `NeumorphButton` component with variants
- Gradient backgrounds and shadows
- Smooth hover animations
- Glass morphism effects

### Form Components
- Integrated with React Hook Form
- Zod schema validation
- Real-time error feedback
- Accessible form controls

## Deployment

### Build for Production
```bash
npm run build
```

### Start Production Server
```bash
npm start
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
