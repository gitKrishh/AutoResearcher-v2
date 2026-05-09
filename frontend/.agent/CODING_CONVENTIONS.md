# CODING_CONVENTIONS.md — AutoResearcher Frontend
> Strict code style and engineering rules for the `frontend/` service.
> These rules are specific to React + TypeScript + Tailwind.
> Also follow root `/.agent/CODING_CONVENTIONS.md` for project-wide rules.

---

## 1. TypeScript Rules

**Strict mode is mandatory. Zero tolerance for `any`.**

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

```typescript
// ✅ Correct — explicit interface, typed props
interface PaperCardProps {
  paper: Paper
  isExpanded?: boolean
  onExpand: (id: string) => void
}

// ❌ Wrong — any, untyped props
const PaperCard = ({ paper, onExpand }: any) => { ... }
```

- Use `interface` for component props and object shapes
- Use `type` for unions, intersections, and aliases
- Use `unknown` instead of `any` when type is genuinely unknown — then narrow with guards
- Always type the return value of hooks explicitly

```typescript
// ✅ Typed hook return
function useResearch(): {
  report: FinalReport | null
  isLoading: boolean
  error: string | null
  startResearch: (topic: string) => Promise<void>
} { ... }
```

---

## 2. Component Rules

### Structure (every component follows this order)

```typescript
// 1. Imports
import { useState } from 'react'
import { Paper } from '@/types/paper'
import { cn } from '@/lib/utils'

// 2. Types / Interfaces
interface PaperCardProps {
  paper: Paper
  className?: string
}

// 3. Component function
export function PaperCard({ paper, className }: PaperCardProps) {
  // 3a. Hooks
  const [isExpanded, setIsExpanded] = useState(false)

  // 3b. Derived state / computed values
  const shortAbstract = paper.abstract.slice(0, 200)

  // 3c. Handlers
  const handleToggle = () => setIsExpanded(prev => !prev)

  // 3d. JSX
  return (
    <div className={cn('rounded-lg border p-4', className)}>
      ...
    </div>
  )
}
```

### Rules
- **Functional components only** — no class components
- **One component per file** — no multiple exports in one file
- **Named exports** — not default exports (except pages)
- Props interface defined directly above the component function
- `className` prop on every component that renders a root div — use `cn()` to merge

---

## 3. File and Folder Naming

| Item | Convention | Example |
|------|-----------|---------|
| Component files | `PascalCase.tsx` | `PaperCard.tsx` |
| Hook files | `camelCase.ts` | `useResearch.ts` |
| Service files | `camelCase.ts` | `apiService.ts` |
| Type files | `camelCase.ts` | `paper.ts`, `api.ts` |
| Utility files | `camelCase.ts` | `utils.ts` |
| Test files | `ComponentName.test.tsx` | `PaperCard.test.tsx` |
| Page files | `PascalCase.tsx` | `HomePage.tsx`, `ResultsPage.tsx` |

- Pages use **default exports** (React Router convention)
- Everything else uses **named exports**

---

## 4. Tailwind CSS Rules

- **Tailwind only** — no CSS modules, no styled-components, no inline `style={{}}`
- Use `cn()` utility (from `lib/utils.ts`) for conditional classes

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

```tsx
// ✅ Correct — conditional classes via cn()
<div className={cn(
  'rounded-lg border p-4 transition-colors',
  isActive && 'border-blue-500 bg-blue-50',
  hasError && 'border-red-500 bg-red-50',
  className
)}>

// ❌ Wrong — inline style
<div style={{ borderColor: isActive ? 'blue' : 'gray' }}>

// ❌ Wrong — string concatenation
<div className={`rounded-lg ${isActive ? 'border-blue-500' : ''}`}>
```

### Class Ordering Convention (follow Prettier Tailwind plugin order)
1. Layout (display, position, flex, grid)
2. Sizing (w-, h-, max-w-)
3. Spacing (p-, m-, gap-)
4. Typography (text-, font-, leading-)
5. Colors (bg-, text-, border-)
6. Effects (shadow-, opacity-, transition-)
7. Responsive prefixes last (`md:`, `lg:`)

---

## 5. Hooks Conventions

### Custom Hook Rules
- Hook name always starts with `use`
- One hook per concern — do not combine unrelated state
- Return an object (not an array) unless it's a simple value pair

```typescript
// ✅ Correct — returns named object
function useResearch() {
  const [report, setReport] = useState<FinalReport | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const startResearch = async (topic: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await apiService.runResearch(topic)
      setReport(response.data.data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Research failed')
    } finally {
      setIsLoading(false)
    }
  }

  return { report, isLoading, error, startResearch }
}

// ❌ Wrong — array return for complex hook
function useResearch() {
  return [report, isLoading, error, startResearch]
}
```

### Always Handle Three States
Every data-fetching hook must expose:
- `isLoading: boolean`
- `error: string | null`
- `data: T | null`

Never render a component without handling all three.

---

## 6. API Service Conventions

```typescript
// services/apiService.ts
import axios, { AxiosResponse } from 'axios'
import type { APIResponse, Paper, FinalReport } from '@/types'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120_000,           // 2 min — research pipeline is slow
  headers: { 'Content-Type': 'application/json' },
})

// Response interceptor — unwrap data or throw typed error
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.error?.message ?? error.message
    throw new Error(message)
  }
)

export const apiService = {
  healthCheck: (): Promise<AxiosResponse<APIResponse<{ status: string }>>> =>
    api.get('/health'),

  searchPapers: (
    query: string,
    maxResults = 10
  ): Promise<AxiosResponse<APIResponse<Paper[]>>> =>
    api.post('/search', { query, max_results: maxResults }),

  runResearch: (
    topic: string,
    maxPapers = 10
  ): Promise<AxiosResponse<APIResponse<FinalReport>>> =>
    api.post('/research', { topic, max_papers: maxPapers }),
}
```

Rules:
- All API calls defined here — **nowhere else**
- Always set `timeout` — research pipeline takes time
- Use an axios interceptor for error normalization
- Match request/response types exactly to backend Pydantic schemas

---

## 7. Type Definitions

Types mirror backend Pydantic schemas exactly:

```typescript
// types/api.ts
export interface APIError {
  code: string
  message: string
  detail?: string
}

export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: APIError
}

// types/paper.ts
export interface Paper {
  id: string
  title: string
  abstract: string
  authors: string[]
  pdf_url: string
  published: string
  source: 'arxiv' | 'semantic_scholar'
}

export interface PaperAnalysis extends Paper {
  summary: string
  methodology: string
  datasets: string
  key_findings: string
  limitations: string
  contribution: string
}

// types/research.ts
export interface InsightReport {
  research_gaps: string[]
  contradictions: string[]
  trends: string[]
  future_directions: string[]
}

export interface FinalReport {
  topic: string
  paper_count: number
  papers: PaperAnalysis[]
  literature_review: string
  insights: InsightReport | null
  generated_at: string
}
```

- Keep types in sync with backend schemas — update both together when schemas change
- Use `snake_case` for API types (to match JSON) — convert to `camelCase` in components if needed
- Export all types from `src/types/index.ts` barrel file

---

## 8. React Router Conventions

```typescript
// Navigating with state
const navigate = useNavigate()
navigate('/research', { state: { topic: 'AI agents' } })

// Reading state in destination page
const location = useLocation()
const { topic } = location.state as { topic: string }
```

- Pages are lazy-loaded with `React.lazy()` + `Suspense` for performance
- Use `useNavigate` (not `<Link>`) for programmatic navigation after actions
- Use `<Link>` for static navigation links in the nav
- Always handle the case where `location.state` is null (user navigated directly)

---

## 9. Error and Loading State Patterns

### Every data-fetching component follows this pattern:

```tsx
function ResearchPage() {
  const { report, isLoading, error, startResearch } = useResearch()

  if (isLoading) return <LoadingSpinner message="Running research pipeline..." />
  if (error) return <ErrorMessage message={error} onRetry={() => startResearch(topic)} />
  if (!report) return <EmptyState message="No research started yet." />

  return <ReportView report={report} />
}
```

- Never render partial UI when in loading or error state
- `LoadingSpinner`, `ErrorMessage`, `EmptyState` are shared components in `components/common/`
- Always provide a retry mechanism on error when possible

---

## 10. Import Conventions

```typescript
// Order (separated by blank lines):
// 1. React
import { useState, useEffect } from 'react'

// 2. Third-party
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'

// 3. Internal — absolute (via @ alias)
import { apiService } from '@/services/apiService'
import type { Paper } from '@/types'
import { cn } from '@/lib/utils'

// 4. Internal — relative (same folder / sibling)
import { AgentStep } from './AgentStep'
```

- Use `@/` absolute imports for everything outside the current folder
- Use relative imports only for files in the same folder
- Type-only imports use `import type` — keeps runtime bundle clean

---

## 11. Prettier Config

```json
// .prettierrc
{
  "semi": false,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

`prettier-plugin-tailwindcss` auto-sorts class names — install it and let it run.

---

## 12. Testing Conventions

```typescript
// PaperCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { PaperCard } from './PaperCard'
import { mockPaper } from '@/test/fixtures'

describe('PaperCard', () => {
  it('renders paper title', () => {
    render(<PaperCard paper={mockPaper} onExpand={vi.fn()} />)
    expect(screen.getByText(mockPaper.title)).toBeInTheDocument()
  })

  it('calls onExpand with paper id when clicked', () => {
    const onExpand = vi.fn()
    render(<PaperCard paper={mockPaper} onExpand={onExpand} />)
    fireEvent.click(screen.getByRole('button', { name: /expand/i }))
    expect(onExpand).toHaveBeenCalledWith(mockPaper.id)
  })
})
```

Rules:
- Use `screen.getByRole` over `getByTestId` where possible — tests user-visible behavior
- Mock `apiService` at module level with `vi.mock('@/services/apiService')`
- Create `src/test/fixtures.ts` with mock data objects for reuse across tests
- Don't test implementation details — test what the user sees and can interact with
