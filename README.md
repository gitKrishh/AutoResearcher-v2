# 🧬 AutoResearcher

**AutoResearcher** is a production-grade, autonomous AI scientific assistant designed to accelerate academic research. It uses a multi-agent orchestration pipeline to transform a simple research topic into a comprehensive, synthesized literature review with deep insights, sourced from real-world papers.

![AutoResearcher UI](https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&q=80&w=1200)

## 🚀 Key Features

- **Multi-Agent Orchestration**: A chain of 7 specialized AI agents (Planner, Searcher, PDF, Embedding, Analysis, Insight, Writer) working in sync.
- **RAG-Powered Intelligence**: Uses Retrieval-Augmented Generation (RAG) with FAISS vector storage to ground all answers in actual academic literature.
- **Deep Insights Dashboard**: Automatically identifies research gaps, contradictions, and future trends across multiple papers.
- **Interactive Pipeline Tracker**: Real-time visual feedback of the autonomous agent pipeline as it works.
- **Contextual Chat**: Ask follow-up questions about the synthesized research using the integrated RAG chat panel.
- **Premium UI/UX**: Modern, responsive design with Dark Mode support, glassmorphism, and smooth animations.

## 🛠️ Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Orchestration**: Custom Stateless Multi-Agent System
- **LLMs**: [NVIDIA NIM](https://www.nvidia.com/en-us/ai-data-science/generative-ai/nim/) (Llama 3.1 70B Instruct)
- **Embeddings**: [Sentence-Transformers](https://www.sbert.net/) (all-MiniLM-L6-v2)
- **Vector Store**: [FAISS](https://github.com/facebookresearch/faiss)
- **Search**: [arXiv API](https://arxiv.org/help/api/index)

### Frontend
- **Framework**: [React 19](https://react.dev/) + [Vite](https://vitejs.dev/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Components**: [shadcn/ui](https://ui.shadcn.com/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **State Management**: React Hooks + Session Storage

---

## 🏗️ Architecture: The Agent Pipeline

1.  **Planner Agent**: Decomposes the research topic into specific, optimized search queries.
2.  **Search Agent**: Fetches the most relevant recent papers from academic repositories (arXiv).
3.  **PDF Agent**: Downloads and extracts clean text from scientific PDFs.
4.  **Embedding Agent**: Vectorizes the extracted text and populates the FAISS vector store.
5.  **Analysis Agent**: Performs deep-reading of each paper to extract structured findings.
6.  **Insight Agent**: Compares findings across papers to identify trends and gaps.
7.  **Writer Agent**: Synthesizes everything into a professional, markdown-formatted literature review.

---

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- [NVIDIA API Key](https://build.nvidia.com/meta/llama-3_1-70b-instruct) (for LLM inference)

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:
```env
OPENAI_API_KEY=your_nvapi_key
NVIDIA_API_KEY=your_nvapi_key
NVIDIA_MODEL=meta/llama-3.1-70b-instruct
CORS_ORIGINS=["http://localhost:5173"]
```

Run the backend:
```bash
python -m uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

Run the frontend:
```bash
npm run dev
```

---

## 🧪 Testing

The project includes a comprehensive suite of unit and integration tests for the backend agents and API routers.

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

---

## 🛡️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

---
Built with ❤️ by the AutoResearcher Team.
