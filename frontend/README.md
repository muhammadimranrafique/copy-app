# SchoolCopy - Business Management System

A modern business management web application for School Copy Manufacturing companies. This app manages clients (schools/dealers), products, orders, payments, inventory, and expenses, and generates profit/loss reports.

## Features

- **Dashboard**: Comprehensive business overview with key metrics
- **Leaders Management**: Manage schools and dealers with their information and balances
- **Products Management**: Track products, inventory, pricing, and margins
- **Orders Management**: Process and track customer orders
- **Payments**: Record and track payment transactions
- **Settings**: Configure business information and currency settings
- **Responsive Design**: Optimized for both desktop and mobile devices

## Tech Stack

- **React** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Radix UI** for accessible components
- **React Router** for navigation
- **Sonner** for toast notifications
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and visit `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── components/         # Reusable components
│   ├── Layout.tsx      # Main layout with sidebar
│   ├── StatCard.tsx    # Statistics card component
│   ├── WelcomeAlert.tsx
│   ├── ProtectedRoute.tsx
│   └── ui/             # UI primitives (buttons, cards, etc.)
├── pages/              # Page components
│   ├── Login.tsx
│   ├── Dashboard.tsx
│   ├── Leaders.tsx
│   ├── Products.tsx
│   ├── Orders.tsx
│   ├── Payments.tsx
│   └── Settings.tsx
├── hooks/              # Custom React hooks
│   └── useCurrency.ts  # Currency formatting hook
├── lib/                # Utility functions
│   ├── utils.ts
│   ├── mock-auth.tsx   # Mock authentication
│   └── mock-data.ts    # Mock data for development
├── App.tsx             # Main app component
├── main.tsx            # Application entry point
└── index.css           # Global styles
```

## Key Features

### Authentication
- Mock authentication system for development
- Session management with localStorage

### Currency Management
- Multi-currency support (PKR, INR, USD, EUR, GBP)
- Configurable currency symbols
- Automatic currency formatting

### Responsive Design
- Mobile-first approach
- Breakpoints for tablet and desktop
- Touch-friendly interface

### UI Components
- Modern, clean interface
- Accessible components (ARIA-compliant)
- Smooth animations and transitions
- Dark mode ready (CSS variables)

## Development Notes

This application currently uses mock data and authentication for development purposes. To integrate with a real backend:

1. Replace `src/lib/mock-auth.tsx` with actual authentication
2. Replace `src/lib/mock-data.ts` with API calls
3. Update SDK imports in pages to use real SDKs

## Environment Variables

Create a `.env` file in the root directory for environment-specific configuration:

```env
VITE_API_URL=your_api_url_here
```

## License

MIT License - feel free to use this project for your business needs.

## Support

For issues and questions, please open an issue on the repository.
