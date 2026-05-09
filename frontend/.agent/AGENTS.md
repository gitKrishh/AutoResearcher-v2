# AGENTS.md — AutoResearcher Frontend
> AI Operating Manual for the `frontend/` service.
> Read this before writing or modifying any frontend code.
> For project-wide rules, see root `/.agent/AGENTS.md`.

---

## 1. Service Purpose

The frontend is the **user interface** of AutoResearcher.

It is a React single-page application that:
- Accepts a research topic from the user
- Displays real-time pipeline progress as agents run
- Shows paper search results, summaries, and comparisons
- Renders the final generated literature review
- Allows the user to ask follow-up questions (RAG)

The frontend is a **thin client**. It holds no business logic. All intelligence lives in the backend. The frontend's only job is to display data and relay user input.

---

## 2. Tech Stack (Frontend Only)

| Concern           | Technology                              |
|-------------------|-----------------------------------------|
| Framework         | React 18 + TypeScript                   |
| Build Tool        | Vite                                    |
| Routing           | React Router v6                         |
| State Management  | React Context + `useState` / `useReducer` (no Redux unless scale demands it) |
| HTTP Client       | Axios                                   |
| Styling           | Tailwind CSS v3                         |
| Component Library | shadcn/ui (Radix UI primitives)         |
| Markdown Render   | `react-markdown` + `remark-gfm`         |
| Icons             | Lucide React                            |
| Testing           | Vitest + React Testing Library          |
| Linting           | ESLint (TypeScript rules)               |
| Formatting        | Prettier                                |

---

## 3. Folder Structure

```
frontend/
│
├── .agent/                          ← YOU ARE HERE
│   ├── AGENTS.md
│   ├── CONTEXT.md
│   └── CODING_CONVENTIONS.md
│
├── src/
│   ├── main.tsx                     ← React root, router setup
│   ├── App.tsx                      ← top-level layout, route definitions
│   │
│   ├── pages/                       ← one component per route
│   │   ├── HomePage.tsx             ← / — landing + search input
│   │   ├── ResearchPage.tsx         ← /research — pipeline progress view
│   │   └── ResultsPage.tsx          ← /results — final report view
│   │
│   ├── components/
│   │   ├── common/                  ← reusable across pages
│   │   │   ├── Layout.tsx           ← nav + page wrapper
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorMessage.tsx
│   │   │   └── EmptyState.tsx
│   │   │
│   │   ├── search/
│   │   │   ├── SearchBar.tsx        ← topic input + submit button
│   │   │   └── SearchSuggestions.tsx
│   │   │
│   │   ├── research/
│   │   │   ├── PipelineTracker.tsx  ← shows agent progress steps
│   │   │   ├── AgentStep.tsx        ← individual step (pending/active/done)
│   │   │   └── PaperCard.tsx        ← paper title, abstract, summary
│   │   │
│   │   └── results/
│   │       ├── ReportView.tsx       ← renders final literature review (markdown)
│   │       ├── PaperList.tsx        ← list of all analyzed papers
│   │       ├── InsightPanel.tsx     ← research gaps, trends, contradictions
│   │       └── CitationList.tsx     ← formatted citations
│   │
│   ├── hooks/
│   │   ├── useResearch.ts           ← main research flow state + API calls
│   │   ├── usePapers.ts             ← paper list state
│   │   └── useSearch.ts             ← search input state
│   │
│   ├── services/
│   │   └── apiService.ts            ← ALL axios calls — the only file that talks to backend
│   │
│   ├── types/
│   │   ├── paper.ts                 ← Paper, PaperAnalysis, ProcessedPaper
│   │   ├── research.ts              ← ResearchRequest, FinalReport, InsightReport
│   │   └── api.ts                   ← APIResponse<T>, APIError
│   │
│   ├── context/
│   │   └── ResearchContext.tsx      ← global research session state (if needed)
│   │
│   └── lib/
│       └── utils.ts                 ← cn() helper, formatters, date utils
│
├── public/
│   └── favicon.ico
│
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── .eslintrc.cjs
├── .prettierrc
├── package.json
└── Dockerfile
```

---

## 4. Page Definitions

### `HomePage` (`/`)
- Clean landing page with a centered search input
- User types a research topic and submits
- On submit: navigate to `/research` and trigger the research pipeline
- Show example topics as suggestions

### `ResearchPage` (`/research`)
- Shows live pipeline progress: each agent step as a visual tracker
- Displays papers as they are discovered (streaming feel)
- Progress steps: Planning → Searching → Downloading PDFs → Analyzing → Writing
- On completion: show "View Report" button → navigate to `/results`

### `ResultsPage` (`/results`)
- Full literature review rendered from markdown
- Sidebar: list of papers analyzed (PaperList)
- Tabs or sections: Report | Papers | Insights | Citations
- Allow user to ask a follow-up question (RAG query input)

---

## 5. Component Responsibilities

| Component          | Responsibility                                              |
|--------------------|-------------------------------------------------------------|
| `SearchBar`        | Controlled input + submit. Emits query string. No API calls.|
| `PipelineTracker`  | Displays agent pipeline steps with status icons. Read-only. |
| `AgentStep`        | Single step UI: pending / active (spinner) / done / error.  |
| `PaperCard`        | Displays paper title, authors, date, abstract, summary.     |
| `ReportView`       | Renders `literature_review` markdown string via react-markdown.|
| `InsightPanel`     | Displays gaps, trends, contradictions in organized sections. |
| `CitationList`     | Formatted citation list from paper metadata.               |

**Rule:** A component does one thing. If a component needs data from the API, it uses a hook — not a direct axios call.

---

## 6. Data Flow

```
User Input (SearchBar)
    ↓
useResearch hook
    ↓
apiService.runResearch(topic)     ← only place that calls backend
    ↓
Backend POST /api/research
    ↓
FinalReport response
    ↓
ResearchContext (global state)
    ↓
Pages + Components (read-only display)
```

**Never call `apiService` directly from a component.** Always go through a hook.

---

## 7. API Integration

All backend calls live exclusively in `src/services/apiService.ts`:

```typescript
// services/apiService.ts

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

export const apiService = {
  searchPapers: (query: string, maxResults = 10) =>
    axios.post<APIResponse<Paper[]>>(`${BASE_URL}/search`, { query, max_results: maxResults }),

  runResearch: (topic: string, maxPapers = 10) =>
    axios.post<APIResponse<FinalReport>>(`${BASE_URL}/research`, { topic, max_papers: maxPapers }),

  getPaper: (id: string) =>
    axios.get<APIResponse<Paper>>(`${BASE_URL}/papers/${id}`),

  healthCheck: () =>
    axios.get<APIResponse<{ status: string }>>(`${BASE_URL}/health`),
}
```

---

## 8. State Management Philosophy

- **Local state** (`useState`): UI-only state — input values, toggles, open/close
- **Custom hooks**: data fetching state — loading, error, data
- **React Context**: shared session state that multiple pages need (current report, current papers)
- **No Redux** unless the app grows significantly beyond MVP

```
Local state  →  hook state  →  context
(input)         (API data)     (cross-page)
```

---

## 9. Environment Variables

```env
# frontend/.env
VITE_API_URL=http://localhost:8000/api
```

All env vars must start with `VITE_` to be accessible in Vite.
Never put secrets in the frontend — it all becomes public in the browser.

---

## 10. What NOT To Do (Frontend)

- ❌ Never call `axios` directly inside a component — use hooks
- ❌ Never put business logic in components — that belongs in hooks or services
- ❌ Never use `any` type in TypeScript
- ❌ Never hardcode the backend URL — use `import.meta.env.VITE_API_URL`
- ❌ Never use class components — functional components + hooks only
- ❌ Never use inline styles — Tailwind classes only
- ❌ Never ignore loading and error states — always handle all three: loading / error / data
- ❌ Never store sensitive data in `localStorage`
- ❌ Never import from a sibling page — use shared `components/common/` instead

---

## 11. Testing Requirements

- Every component has a `.test.tsx` file colocated next to it
- Every custom hook has a test in `hooks/__tests__/`
- Mock all API calls via `vi.mock('../services/apiService')`
- Test **user interactions**, not implementation: "when user clicks submit, loading state shows"
- Run with: `npm run test`
- All tests must pass before marking a frontend phase complete in `CONTEXT.md`
