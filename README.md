# RepoGuide

> Understand any codebase like someone who built it explained it to you.

## What is RepoGuide?

RepoGuide is an AI-powered GitHub repository tutor that helps developers understand unfamiliar codebases.

Give it a GitHub repository and ask questions about how the code works, how different files interact, or why certain implementation patterns are used. Answers are generated only from code actually retrieved from the repository — RepoGuide doesn't invent files, functions, or behavior.

### Perfect for

* **Learning frameworks** — Explore real-world projects using FastAPI, LangChain, Next.js, and more
* **Understanding architecture** — Learn how different parts of a codebase fit together
* **Onboarding** — Understand an unfamiliar codebase faster
* **Reverse engineering** — Trace how functionality works across a repository

## How It Works

RepoGuide uses Retrieval-Augmented Generation (RAG) designed for codebase understanding.

### 1. Index

The user provides a GitHub repository URL.

RepoGuide downloads the repository archive, filters it to source/config/docs files, and skips build output, vendor directories, and lockfiles.

### 2. Chunk & Embed

Source files are split into code-aware chunks (language-aware splitting where supported).

Each chunk is stored with metadata:

* File path
* Start and end line
* Repository (owner + repo)
* Commit SHA (so source links stay valid as branches move)

The chunks are embedded with a local model (`all-MiniLM-L6-v2`, 384-dim) and stored in ChromaDB.

### 3. Ask

The user asks a question about the repository.

### 4. Retrieve & Expand

The question is embedded and relevant code chunks are retrieved using semantic similarity search. Each retrieved chunk is expanded with its **before and after neighbors** in the same file (by line number) so the model has surrounding context.

### 5. Rerank

All candidates (retrieved + neighbors) are rescored against the question by the [Jina AI reranker](https://jina.ai/reranker/), and the top 8 most relevant chunks are kept — shrinking the context to the smallest useful set.

### 6. Generate

The retained code is provided to the Gemini LLM as context. The model uses only that context to generate an explanation, and the app separately builds clickable GitHub source links from the chunk metadata. The LLM never invents sources.

## Current Architecture

```text
GitHub Repository                 Next.js frontend
        │                                │
        ▼                                ▼
 GitHub API / ZIP                 Fetch / POST
        │                                │
        ▼                                ▼
 File Filtering                    FastAPI API
        │                           (main.py)
        ▼                                │
  Code Chunking                           │
        │                                ▼
        ▼                           RAG pipeline
 Local Embeddings                   (rag.py)
 (all-MiniLM-L6-v2)                      │
        │                                │
        ▼                                ▼
     ChromaDB                    Semantic Retrieval
        │                                │
        │                                ▼
        │                        Neighbor Expansion
        │                                │
        │                                ▼
        │                         Jina Reranking
        │                                │
        └────────────────────────────────► Gemini LLM
                                              │
                                              ▼
                                      Answer + Sources
```

FastAPI provides the API layer between the Next.js application and the RAG pipeline.

## Tech Stack

### Backend
* **Python** + **FastAPI**
* **ChromaDB** — vector storage
* **Google Gemini** — answer generation (`gemini-2.5-flash`)
* **sentence-transformers** — local embeddings (`all-MiniLM-L6-v2`)
* **Jina AI Reranker** — cross-encoder relevance reranking
* **LangChain Text Splitters** — language-aware chunking
* **GitHub REST API** — metadata, commit SHA, ZIP download

### Frontend
* **Next.js 15** (App Router) + **React 19**
* **TypeScript**

## Repository Setup

### Prerequisites
* Python 3.12
* Node.js (18+)
* A [Google Gemini API key](https://aistudio.google.com/) (`GEMINI_API_KEY`)
* A [Jina AI API key](https://jina.ai/api-dashboard/) (`JINA_API_KEY`)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
cp .env.example .env   # add GEMINI_API_KEY and JINA_API_KEY
uvicorn backend.main:app --reload
```

The API runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm run dev
```

The app runs at `http://localhost:3000`.

> CORS is configured to allow requests from `localhost` / `127.0.0.1` on dynamic ports.

## API

### Index Repository

```http
POST /index
Content-Type: application/json

{ "url": "https://github.com/owner/repo" }
```

Downloads, filters, chunks, embeds, and stores a repository.

**Response:**
```json
{
  "url": "https://github.com/owner/repo",
  "status": "success",
  "message": "Repository indexed successfully",
  "file_count": 42
}
```

### Ask a Question

```http
POST /ask
Content-Type: application/json

{ "url": "https://github.com/owner/repo", "question": "How does authentication work?" }
```

Embeds the question, retrieves + expands + reranks chunks, and generates an answer.

**Response:**
```json
{
  "answer": "Authentication is handled with a React Context...",
  "sources": [
    {
      "file_path": "components/auth/AuthContext.tsx",
      "start_line": 20,
      "end_line": 65,
      "commit_sha": "4d22a752f8e30de006cca7c4751f4de7ccf6a850",
      "score": 0.458
    }
  ]
}
```

The frontend builds clickable GitHub links (commit-anchored, line-ranged) from each source.

## Current Features

* GitHub repository ingestion (metadata, default branch, commit SHA)
* File filtering — source/config/docs kept; build/vendor/IDE/lockfiles ignored
* Language-aware code chunking with line-number metadata
* Local embeddings via sentence-transformers
* ChromaDB vector storage
* Repository-scoped semantic retrieval
* Same-file neighbor expansion around retrieved chunks
* **Jina AI reranking** of all candidates, trimming to the top 8
* RAG-based code explanations from Gemini
* Source links anchored to a commit SHA with exact line ranges
* FastAPI API endpoints
* **Next.js frontend** — dashboard, repository workspace, chat, and source panel

## Project Structure

```text
RepoGuide/
│
├── backend/
│   ├── main.py             # FastAPI app + routes
│   ├── config.py           # env + constants
│   ├── schemas.py          # Pydantic request/response models
│   ├── github.py           # GitHub API / ZIP download
│   ├── file_filter.py      # keep source files, drop noise
│   ├── chunking.py         # language-aware chunking with line numbers
│   ├── embeddings.py       # local sentence-transformers embeddings
│   ├── vector_storage.py   # ChromaDB add/query/get
│   ├── reranking.py        # Jina AI reranker
│   ├── llm.py              # Gemini answer generation
│   ├── prompts.py          # system prompt + prompt builder
│   └── rag.py              # index + ask pipelines
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                  # landing
│   │   ├── dashboard/page.tsx        # repositories
│   │   └── repositories/[id]/page.tsx# repository workspace
│   ├── components/
│   │   ├── layout/DashboardLayout.tsx
│   │   ├── repository/RepositoryInput.tsx
│   │   ├── repository/RepositoryWorkspace.tsx
│   │   └── chat/ (ChatWindow, ChatInput, SourcePanel)
│   ├── lib/
│   │   ├── api/ (client, repositories, chat)
│   │   └── utils/repository.ts
│   └── types/api.ts
│
├── requirements.txt
└── README.md
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key for answer generation |
| `JINA_API_KEY` | Yes | Jina AI API key for reranking |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend | Backend URL (defaults to `http://localhost:8000`) |

## Development Status

The core repository indexing, retrieval, neighbor expansion, reranking, and answer generation pipeline works end-to-end, with a Next.js frontend for the dashboard and repository chat workspace.

### Backend changes still needed for full parity

* **File-content endpoint** — the frontend file explorer currently shows a note that browsing requires a backend file/`chunks`-by-file endpoint. No such endpoint exists yet.
* **Conversation persistence** — chat history is not persisted; the backend has no conversation/messages endpoints.
* **Authentication** — no user accounts or JWT auth on the backend yet.
* **PostgreSQL** integration for users/repositories/conversations.

### Planned improvements

* File-tree browsing backed by a real file-content API
* Persistent, per-repository conversations
* Authentication (JWT) and per-user ownership
* Better embedding models / candidate retrieval to improve harder, more abstract questions
* Production deployment
