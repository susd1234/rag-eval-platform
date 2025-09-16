# AI SME Evaluation Platform - React Frontend

A modern, eye-catching React frontend for the AI Assisted SME Evaluation Platform, inspired by NVIDIA's design patterns.

## Features

- **Modern UI Design**: NVIDIA-inspired dark theme with green accent colors
- **Responsive Layout**: Optimized for desktop, tablet, and mobile devices
- **Real-time System Status**: Live monitoring of backend services and agents
- **Interactive Evaluation Form**: Multi-metric selection with validation
- **Animated Results Display**: Beautiful visualization of evaluation results
- **Loading States**: Engaging loading animations with agent status
- **Error Handling**: Comprehensive error display and recovery

## Technology Stack

- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Lucide React** for icons
- **Axios** for API communication

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running on port 9777

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Building for Production

```bash
npm run build
```

This builds the app for production to the `build` folder.

## API Integration

The frontend connects to the FastAPI backend running on port 9777. The following endpoints are used:

- `POST /evaluation/evaluate` - Submit evaluation request
- `GET /evaluation/status/{id}` - Get evaluation status
- `GET /evaluation/system/health` - Get system health
- `GET /evaluation/metrics` - Get metrics information
- `POST /evaluation/test` - Test evaluation with sample data

## Design System

### Color Palette

- **Primary Green**: #76B900 (NVIDIA Green)
- **Dark Background**: #0D1117
- **Secondary Background**: #161B22
- **Accent Colors**: Various shades of gray and green

### Components

- **Cards**: Rounded corners with subtle borders and hover effects
- **Buttons**: Primary (green) and secondary (dark) variants
- **Input Fields**: Dark theme with green focus states
- **Badges**: Color-coded metric ratings (Platinum, Gold, Silver, Bronze)

### Animations

- **Fade In/Out**: Smooth transitions between states
- **Scale Effects**: Hover and click animations
- **Loading Spinners**: Custom animated loading states
- **Staggered Animations**: Sequential element animations

## Project Structure

```
src/
├── components/          # React components
│   ├── Header.tsx      # Navigation header
│   ├── EvaluationForm.tsx # Main evaluation form
│   ├── ResultsDisplay.tsx # Results visualization
│   ├── LoadingSpinner.tsx # Loading animations
│   └── SystemStatus.tsx   # System health display
├── services/           # API services
│   └── api.ts         # Axios configuration and API calls
├── types/             # TypeScript type definitions
│   └── evaluation.ts  # Evaluation-related types
├── App.tsx           # Main application component
├── index.css         # Global styles and Tailwind imports
└── index.tsx         # Application entry point
```

## Development

### Available Scripts

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App (one-way operation)

### Code Style

- TypeScript for type safety
- Functional components with hooks
- Tailwind CSS for styling
- Framer Motion for animations
- ESLint for code quality

## Contributing

1. Follow the existing code style
2. Use TypeScript for all new components
3. Add proper error handling
4. Include loading states for async operations
5. Test on multiple screen sizes

## License

This project is part of the AI SME Evaluation Platform.