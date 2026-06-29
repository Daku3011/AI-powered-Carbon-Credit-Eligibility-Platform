# Frontend - Carbon Intelligence Platform

Next.js 16 application for the AI-powered Carbon Intelligence Platform.

## Tech Stack

- **Framework**: Next.js 16 (React 19, TypeScript)
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui (base-ui based)
- **Charts**: ApexCharts (react-apexcharts)
- **Icons**: Lucide React

## Getting Started

```bash
# Install dependencies
npm install

# Start development server (port 3000)
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

## Pages

| Route                    | Description                                  |
|--------------------------|----------------------------------------------|
| `/`                      | Home page with feature cards                 |
| `/calculator`            | Carbon calculator with OCR upload            |
| `/calculator/results`    | Emissions summary, eligibility score, roadmap|
| `/marketplace`           | Decarbonization project marketplace          |
| `/dashboard`             | Benchmarking charts (bar, donut, line)       |
| `/chatbot`               | AI Carbon Consultant chat interface          |

## Project Structure

```
src/
├── app/                  # Page routes (App Router)
│   ├── layout.tsx        # Root layout with Navbar
│   ├── page.tsx          # Home page
│   ├── globals.css       # Global styles
│   ├── calculator/       # Calculator pages
│   ├── marketplace/      # Marketplace page
│   ├── dashboard/        # Dashboard page
│   └── chatbot/          # Chatbot page
├── components/
│   ├── navbar.tsx        # Navigation bar
│   └── ui/               # shadcn/ui components
└── lib/
    ├── api.ts            # API client (configurable base URL)
    └── utils.ts          # cn() utility
```

## Environment Variables

| Variable              | Default               | Description                    |
|-----------------------|-----------------------|--------------------------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL          |

## API Client

The frontend API client is at `src/lib/api.ts` and provides typed functions:

- `calculateScore(data)` - POST /api/calculator/score
- `getMarketplaceProjects()` - GET /api/marketplace
- `queryChatbot(data)` - POST /api/chatbot/query
- `uploadOcr(file)` - POST /api/ocr (multipart)
- `exportReport(data, format)` - POST /api/reports/export

## UI Components

This project uses shadcn/ui components based on base-ui. Key components:

- `Button`, `Card`, `Input`, `Label`, `Select`, `Tabs`, `Badge`, `Textarea`
- Charts: `react-apexcharts` (bar, donut, line)
- Icons: `lucide-react`
