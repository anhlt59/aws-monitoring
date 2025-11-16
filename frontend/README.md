# AWS Monitoring Frontend

Vue 3 + TypeScript + Vite frontend for AWS Monitoring application.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run test` - Run tests
- `npm run test:ui` - Run tests with UI
- `npm run test:coverage` - Generate coverage report
- `npm run lint` - Lint code
- `npm run lint:fix` - Fix linting issues
- `npm run format` - Format code with Prettier
- `npm run type-check` - Check TypeScript types

## Project Structure

```
frontend/
├── src/
│   ├── core/              # Domain layer (types, enums, constants)
│   ├── api/               # Infrastructure layer (HTTP client, API services)
│   ├── composables/       # Application logic
│   ├── store/             # Global state management (Pinia)
│   ├── components/        # Presentation layer
│   ├── pages/             # Route entry points
│   ├── router/            # Routing configuration
│   ├── styles/            # Global styles
│   └── utils/             # Utility functions
├── tests/                 # Test files
└── public/                # Static assets
```

## Development

### Backend Integration

The frontend expects the backend API to be running on `http://localhost:3001/api` during development. This is configured in `.env.development`.

To start the backend:

```bash
cd /home/user/aws-monitoring
make start          # Start LocalStack
make deploy-local   # Deploy backend stacks
```

### Environment Variables

- `.env.development` - Development environment variables
- `.env.production` - Production environment variables

## Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Next-generation frontend tooling
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Vitest** - Unit testing framework

## Documentation

See the `docs/` directory in the project root for comprehensive documentation:

- `frontend-overview.md` - Architecture overview
- `frontend-quick-start.md` - Detailed setup guide
- `frontend-design.md` - Complete design documentation
- `frontend-implementation-guide.md` - Implementation examples
- `frontend-types-reference.md` - TypeScript type definitions
