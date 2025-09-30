# Perplexity-like UI

This is a React-based frontend for the Perplexity-like search engine.

## Features

- Perplexity-style UI with dark theme
- Real-time search with citations
- Responsive design
- Support for multiple search modes (Explore, Summarize, Learn)
- Advanced filters (language, time range, domain inclusion/exclusion)
- Strict mode and local LLM toggle
- Copy to clipboard functionality

## Development

### Prerequisites

- Node.js (v16 or higher)
- npm

### Installation

```bash
npm install
```

### Development Server

```bash
npm run dev
```

The development server will start on http://localhost:5173

### Build

```bash
npm run build
```

The build output will be in the `dist` directory.

## Docker

The UI is also containerized using Docker and can be run as part of the docker-compose setup:

```bash
docker-compose up -d
```

The web UI will be available at http://localhost:3000

## Environment Variables

- `VITE_API_BASE`: The base URL for the API (default: http://localhost:8080)

## Dependencies

- React + Vite
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Lucide React icons