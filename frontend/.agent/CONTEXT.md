# CONTEXT.md — AutoResearcher Frontend
> Live memory and logbook for the `frontend/` service.
> Update after every meaningful frontend change.
> For project-wide progress, also update root `/.agent/CONTEXT.md`.

---

## Service Status

**Phase:** Pre-development
**Last Updated:** <!-- fill in each session -->
**Node Version:** 20+ (LTS)
**React Version:** 18
**Vite Version:** 5+

---

## Environment Setup Status

```
[ ] Node 20+ installed
[ ] npm install completed (no errors)
[ ] .env file created with VITE_API_URL
[ ] Dev server starts: npm run dev → localhost:5173
[ ] Backend is reachable from frontend (CORS working)
[ ] TypeScript compiles with no errors: npm run type-check
[ ] Linter passes: npm run lint
```

---

## Current Progress

### Phase 1 — Project Scaffold
```
[ ] Vite + React + TypeScript project initialized
[ ] Tailwind CSS configured (tailwind.config.ts + postcss)
[ ] shadcn/ui initialized and base components added
[ ] React Router v6 installed and configured
[ ] Axios installed
[ ] Lucide React installed
[ ] react-markdown + remark-gfm installed
[ ] ESLint + Prettier configured
[ ] Base folder structure created (pages/, components/, hooks/, services/, types/)
[ ] index.html and App.tsx cleaned up
[ ] Dockerfile written
```

### Phase 2 — Types + API Service
```
[ ] src/types/api.ts — APIResponse<T>, APIError
[ ] src/types/paper.ts — Paper, PaperAnalysis, ProcessedPaper
[ ] src/types/research.ts — ResearchRequest, FinalReport, InsightReport
[ ] src/services/apiService.ts — all API functions defined
[ ] apiService tested manually against running backend
[ ] Health check passes: apiService.healthCheck() → 200
```

### Phase 3 — Layout + Routing
```
[ ] src/App.tsx — route definitions (/, /research, /results)
[ ] src/components/common/Layout.tsx — nav + page wrapper
[ ] All three pages scaffold created (empty components)
[ ] Navigation between pages working
[ ] 404 fallback route added
```

### Phase 4 — Home Page
```
[ ] SearchBar component built
[ ] Controlled input with validation (no empty submit)
[ ] Submit navigates to /research with topic in state/params
[ ] Example topic suggestions shown
[ ] Responsive on mobile
[ ] Loading state on submit
```

### Phase 5 — Research Page (Pipeline Tracker)
```
[ ] PipelineTracker component built
[ ] AgentStep component — pending / active / done / error states
[ ] useResearch hook — triggers POST /api/research on page load
[ ] Pipeline steps render in order with status updates
[ ] PaperCard component — shows paper title, authors, abstract
[ ] Papers appear as they are returned from backend
[ ] Error state handled (shows error message + retry button)
[ ] On complete: "View Report" button navigates to /results
```

### Phase 6 — Results Page (Report View)
```
[ ] ReportView component — renders markdown with react-markdown
[ ] Markdown styled with Tailwind Typography plugin
[ ] PaperList component — all analyzed papers in sidebar/list
[ ] InsightPanel component — gaps, trends, contradictions
[ ] CitationList component — formatted citations
[ ] Tabs: Report | Papers | Insights | Citations
[ ] Follow-up question input (RAG query)
[ ] Empty states handled for each section
```

### Phase 7 — Polish + UX
```
[ ] Loading skeleton screens (not just spinners)
[ ] Toast notifications for errors
[ ] Responsive layout verified on mobile
[ ] Page titles set via React Router
[ ] Favicon and basic branding
[ ] Console errors cleared
[ ] TypeScript strict mode passing
[ ] All tests passing
```

---

## Decisions Taken

| Date | Decision | Reason |
|------|----------|--------|
| — | React + Vite + TypeScript | Faster than CRA, professional, better DX than Streamlit |
| — | Tailwind CSS for styling | Faster iteration, consistent spacing, no CSS files to manage |
| — | shadcn/ui for components | Accessible Radix primitives, copy-paste friendly, no lock-in |
| — | React Router v6 for navigation | Standard, well-documented, nested routes support |
| — | Axios over fetch | Better error handling, interceptors, cleaner syntax |
| — | No Redux | App is small enough for Context + hooks; add Zustand if needed |
| — | react-markdown for report rendering | LLM outputs markdown; needs a proper renderer |

---

## Known Bugs / Issues

| ID  | Description | Status | Component | Notes |
|-----|-------------|--------|-----------|-------|
| —   | —           | —      | —         | —     |

---

## Implementation Notes

> Add technical notes here as you discover them during development.

### Vite + TypeScript Setup
- Use `"strict": true` in `tsconfig.json`
- Set `"baseUrl": "src"` for absolute imports (`@/components/...`)
- Configure `resolve.alias` in `vite.config.ts` for `@` → `src/`

```typescript
// vite.config.ts
import path from 'path'
export default defineConfig({
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') }
  }
})
```

### Tailwind Setup
- Install: `tailwindcss`, `postcss`, `autoprefixer`
- Add `@tailwindcss/typography` for markdown prose styling
- Configure `content` in `tailwind.config.ts` to include `./src/**/*.{ts,tsx}`

### shadcn/ui Setup
- Init with: `npx shadcn-ui@latest init`
- Base components to install first: `button`, `input`, `card`, `badge`, `tabs`, `toast`
- Components land in `src/components/ui/` — do not edit them directly

### React Router v6 Pattern
```typescript
// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/research" element={<ResearchPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
```

### Passing Research Topic Between Pages
- Pass topic via React Router `state`: `navigate('/research', { state: { topic } })`
- Read in ResearchPage: `const { state } = useLocation()`
- Store final report in `ResearchContext` so ResultsPage can access it

### react-markdown Usage
```tsx
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

<ReactMarkdown
  remarkPlugins={[remarkGfm]}
  className="prose prose-neutral max-w-none"
>
  {report.literature_review}
</ReactMarkdown>
```

---

## Component Checklist

| Component            | Built | Tested | Notes |
|----------------------|-------|--------|-------|
| Layout               | [ ]   | [ ]    | |
| SearchBar            | [ ]   | [ ]    | |
| PipelineTracker      | [ ]   | [ ]    | |
| AgentStep            | [ ]   | [ ]    | |
| PaperCard            | [ ]   | [ ]    | |
| ReportView           | [ ]   | [ ]    | |
| PaperList            | [ ]   | [ ]    | |
| InsightPanel         | [ ]   | [ ]    | |
| CitationList         | [ ]   | [ ]    | |
| LoadingSpinner       | [ ]   | [ ]    | |
| ErrorMessage         | [ ]   | [ ]    | |
| EmptyState           | [ ]   | [ ]    | |

---

## Package Versions (lock these)

```json
{
  "react": "^18.3.0",
  "react-dom": "^18.3.0",
  "react-router-dom": "^6.24.0",
  "axios": "^1.7.0",
  "react-markdown": "^9.0.0",
  "remark-gfm": "^4.0.0",
  "lucide-react": "^0.400.0",
  "tailwindcss": "^3.4.0",
  "@tailwindcss/typography": "^0.5.0"
}
```

---

## Test Results

| Date | Suite | Passed | Failed | Notes |
|------|-------|--------|--------|-------|
| —    | —     | —      | —      | —     |

---

## Next Steps

1. Run `npm create vite@latest frontend -- --template react-ts`
2. Install all dependencies listed above
3. Configure Tailwind, ESLint, Prettier, path aliases
4. Init shadcn/ui and install base components
5. Create `src/types/` files — mirror backend Pydantic schemas first
6. Build `apiService.ts` and test against the running backend health endpoint
