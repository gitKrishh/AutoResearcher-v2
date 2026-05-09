# AGENTS.md — AutoResearcher Scripts
> AI Operating Manual for the `scripts/` directory.
> Read this before writing or modifying any script.
> For project-wide rules, see root `/.agent/AGENTS.md`.

---

## 1. Purpose of This Directory

`scripts/` contains **one-off and operational utility scripts** that support the project but are not part of the running application.

Scripts are for:
- Dev environment setup and teardown
- Data seeding and FAISS index management
- Batch processing and bulk operations
- Health checks and smoke tests against live services
- CI/CD helpers (build, lint, test, deploy)
- Database/index migrations

Scripts are **not** for:
- Application business logic (that belongs in `backend/app/`)
- Tests (that belongs in `tests/`)
- Frontend tooling (that belongs in `frontend/`)

---

## 2. Folder Structure

```
scripts/
│
├── .agent/                        ← YOU ARE HERE
│   └── AGENTS.md
│
├── setup/
│   ├── install_deps.sh            ← install backend + frontend dependencies
│   ├── setup_env.sh               ← copy .env.example → .env, prompt for keys
│   └── init_vector_store.py       ← initialize empty FAISS index on disk
│
├── data/
│   ├── seed_papers.py             ← fetch + embed a default set of papers into FAISS
│   ├── clear_vector_store.py      ← wipe FAISS index and metadata
│   └── export_papers.py           ← dump all indexed paper metadata to JSON
│
├── ops/
│   ├── health_check.py            ← ping /api/health and all external APIs
│   ├── benchmark_pipeline.py      ← time the full research pipeline end-to-end
│   └── rebuild_index.py           ← re-embed all cached PDFs and rebuild FAISS
│
└── ci/
    ├── lint.sh                    ← run Black + Ruff + mypy + ESLint
    ├── test.sh                    ← run pytest + vitest
    └── build.sh                   ← build Docker images
```

---

## 3. Script Categories

### `setup/` — Run once during initial project setup
These scripts get a developer from zero to a running local environment.
They are safe to re-run (idempotent where possible).

| Script | When to Use |
|--------|------------|
| `install_deps.sh` | Fresh clone — install all Python and Node dependencies |
| `setup_env.sh` | First time — create `.env` from `.env.example` |
| `init_vector_store.py` | First time — create empty FAISS index directory and files |

### `data/` — Manage the vector store and paper data
These scripts manipulate the FAISS index and cached PDFs.
**Always back up `vector_store/` before running destructive scripts.**

| Script | When to Use |
|--------|------------|
| `seed_papers.py` | Populate the index with a known set of papers for dev/demo |
| `clear_vector_store.py` | Wipe the index completely and start fresh |
| `export_papers.py` | Export all indexed paper metadata for inspection/backup |

### `ops/` — Operational checks and maintenance
Use during development to benchmark and verify system behavior.

| Script | When to Use |
|--------|------------|
| `health_check.py` | Verify backend + all external APIs are reachable |
| `benchmark_pipeline.py` | Measure end-to-end pipeline latency |
| `rebuild_index.py` | Rebuild FAISS from scratch using all cached PDFs in `data/pdfs/` |

### `ci/` — CI/CD automation
Run by CI pipelines or locally before pushing.

| Script | When to Use |
|--------|------------|
| `lint.sh` | Before every commit — runs all linters |
| `test.sh` | Before every push — runs full test suite |
| `build.sh` | Before deployment — builds Docker images |

---

## 4. Script Rules

- **Every Python script has a `main()` function** and `if __name__ == "__main__":` guard
- **Every script has a docstring** at the top explaining: what it does, when to use it, and any side effects
- **Shell scripts are POSIX-compatible** — use `#!/usr/bin/env bash` and `set -euo pipefail`
- **Destructive scripts prompt for confirmation** before executing (unless `--force` flag is passed)
- **Scripts never import from `backend/app/`** — they are standalone; duplicate any needed logic
- **All scripts are runnable from the project root**: `python scripts/data/seed_papers.py`
- **Scripts log progress** to stdout with clear step indicators — not silent

---

## 5. Python Script Template

```python
#!/usr/bin/env python3
"""
Script: seed_papers.py
Purpose: Fetch a default set of papers from arXiv and embed them into the FAISS index.
When to use: After clearing the vector store, or for initial dev/demo setup.
Side effects: Writes to vector_store/ and data/pdfs/
Usage: python scripts/data/seed_papers.py [--topic "AI agents"] [--count 10]
"""

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="AI agents in software engineering")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    if not args.force:
        confirm = input(f"Seed {args.count} papers for topic '{args.topic}'? [y/N] ")
        if confirm.lower() != "y":
            logger.info("Aborted.")
            sys.exit(0)

    logger.info("Starting paper seeding...")
    # ... script logic here ...
    logger.info("Done.")


if __name__ == "__main__":
    main()
```

---

## 6. Shell Script Template

```bash
#!/usr/bin/env bash
# Script: lint.sh
# Purpose: Run all linters for backend (Black, Ruff, mypy) and frontend (ESLint, tsc)
# Usage: bash scripts/ci/lint.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "==> Running backend linters..."
cd "$ROOT_DIR/backend"
black --check app/ tests/
ruff check app/ tests/
mypy app/

echo "==> Running frontend linters..."
cd "$ROOT_DIR/frontend"
npm run lint
npm run type-check

echo "==> All linters passed."
```

---

## 7. What NOT To Do

- ❌ Do not put application logic in scripts — it belongs in `backend/app/`
- ❌ Do not hardcode API keys in scripts — read from `.env` or environment
- ❌ Do not run destructive scripts without a confirmation prompt or `--force` flag
- ❌ Do not silently fail — always log what is happening
- ❌ Do not write scripts that only work on one OS — keep them portable
