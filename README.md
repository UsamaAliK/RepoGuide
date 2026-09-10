# RepoGuide

> Understand any codebase like someone who built it explained it to you.

## What is RepoGuide?

RepoGuide is an AI-powered GitHub repository tutor that helps developers understand unfamiliar codebases.

Give it a GitHub repository and ask questions about how the code works, how different files interact, or why certain implementation patterns are used. Answers are generated only from code actually retrieved from the repository — RepoGuide doesn't invent files, functions, or behavior, and every answer comes with clickable source links pointing at the exact file and line range it referenced.

### Perfect for

* **Learning frameworks** — Explore real-world projects using FastAPI, LangChain, Next.js, and more
* **Understanding architecture** — Learn how different parts of a codebase fit together
* **Onboarding** — Understand an unfamiliar codebase faster
* **Reverse engineering** — Trace how functionality works across a repository

## How It Works

RepoGuide uses Retrieval-Augmented Generation (RAG) designed for codebase understanding.

### 1. Index

The user provides a GitHub repository URL.

RepoGuide downloads the repository archive to a temporary directory, filters it to source/config/docs files (skipping build output, vendor directories, and lockfiles), chunks the code, embeds it into a vector store, and **deletes the temporary files** — nothing is kept on disk after indexing.

### 2. Chunk & Embed

Source files are split into code-aware chunks (language-aware splitting where supported).

Each chunk is stored with metadata:

* File path
* Start and end line
* Repository (owner + repo)
* Commit SHA (so source links stay valid as branches move)

The chunks are embedded with a local model (`all-MiniLM-L6-v2`, 384-dim) and stored in PostgreSQL (pgvector), keyed by owner/repo.

### 3. Ask

The user asks a question about the repository. Consecutive questions form a **conversation** — history is summarized on the fly and used to resolve follow-ups like "what about the function it calls?"

### 4. Retrieve & Expand

The (possibly rewritten) question runs through **hybrid retrieval** — three independent searches whose results are fused by **reciprocal rank fusion (RRF)**:

* **Semantic (vector)** — embedded and matched against pgvector (top-10)
* **Keyword (full-text)** — Postgres FTS over chunk content (`tsvector` + `ts_rank_cd`, top-10)
* **Filename** — deterministic `file_path` matching when the question names a file (so "how does `render.yaml` work" always finds the file)

Each candidate chunk is then expanded with its **before and after neighbors** in the same file (by line number) so the model has surrounding context, deduplicated, and capped at 20 candidates.

### 5. Rerank

The ~20 candidates are rescored against the question by the [Jina AI reranker](https://jina.ai/reranker/). Chunks scoring far below the best hit are dropped (**relative** threshold — Jina scores vary by repo), trimming the context to the smallest useful set (max 8).

### 6. Generate

The retained code is provided to the Gemini LLM as context, together with conversation history. The model uses only that context to generate an explanation; the app separately builds clickable GitHub source links from the chunk metadata. **The LLM never invents sources or URLs.**

## Authentication

RepoGuide uses JWT access tokens (15-minute expiry) with **rotating refresh tokens** (30 days) stored as hashes in PostgreSQL:

* `POST /api/register` and `POST /api/login` return both tokens
* `POST /api/refresh` exchanges a valid refresh token for a new token pair (old one is revoked)
* `POST /api/logout` revokes the refresh token server-side
* On a `401`, the frontend transparently refreshes the token and retries the request — no forced re-login until the refresh token itself expires
* Every resource request verifies ownership: a user can only read repositories, conversations, and messages they own

## Current Architecture

```text
Indexing:                       Answering:
                                
GitHub Repo                      Next.js frontend ──► FastAPI (main.py) ──► RAG (rag.py)
  │  │                             │  JWT auth + ownership (auth.py)
  ▼  │                             ▼
download ZIP ──► file filter   ask(): 3 searches in parallel
  ▼                                │  • vector search (pgvector)
chunk (line numbers)               │  • keyword search (tsvector FTS)
  ▼                                │  • filename match
embed (all-MiniLM-L6-v2)           ▼
  ▼                             RRF fusion ──► neighbor expansion ──► Jina rerank (max 20)
PostgreSQL + pgvector               ▼
  (chunks + vectors)            Gemini LLM ──► answer + app-built GitHub source links
                                   ▼
                              PostgreSQL (conversations, messages, sources,
                              users, repos, refresh tokens)
```

FastAPI provides the API layer between the Next.js application and the RAG pipeline. PostgreSQL stores code chunks and vectors (pgvector) plus all application state.

## Tech Stack

### Backend
* **Python** + **FastAPI**
* **PostgreSQL** (SQLAlchemy async + Alembic) — users, repositories, conversations, messages, refresh tokens
* **pgvector** — vector storage for code chunks (HNSW index)
* **PostgreSQL full-text search** — weighted `tsvector` (file path + content) for keyword search
* **Hybrid retrieval** — vector + full-text + filename, fused by reciprocal rank fusion (RRF)
* **Google Gemini** — answer generation (`gemini-2.5-flash`)
* **sentence-transformers** — local embeddings (`all-MiniLM-L6-v2`)
* **Jina AI Reranker** — cross-encoder relevance reranking
* **JWT** (PyJWT + bcrypt) — access + rotating refresh tokens
* **LangChain Text Splitters** — language-aware chunking
* **GitHub REST API** — metadata, commit SHA, ZIP download

### Frontend
* **Next.js 15** (App Router) + **React 19**
* **TypeScript**
* JWT auth context, protected routes, conversation sidebar, GPT-style chat UI

## Repository Setup

### Prerequisites
* Python 3.12
* Node.js (18+)
* PostgreSQL (local dev) or a hosted instance (Supabase/Render)
* A [Google Gemini API key](https://aistudio.google.com/) (`GEMINI_API_KEY`)
* A [Jina AI API key](https://jina.ai/api-dashboard/) (`JINA_API_KEY`)

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env   # set secrets (see Environment Variables below)
alembic -c backend/alembic.ini upgrade head
uvicorn backend.main:app --reload
```

Run from the repo root (the backend is a package). The API runs at `http://localhost:8000`.

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

All routes except `/`, `/api/register`, `/api/login`, `/api/refresh` require `Authorization: Bearer <access_token>`.

### Authentication

```http
POST /api/register
{ "username": "you", "password": "secret" }

POST /api/login
{ "username": "you", "password": "secret" }

POST /api/refresh
{ "refresh_token": "..." }

POST /api/logout
{ "refresh_token": "..." }
```

Register and login respond with `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }`.

### Index Repository

```http
POST /index
Content-Type: application/json

{ "url": "https://github.com/owner/repo" }
```

Downloads, filters, chunks, embeds, and stores a repository. If the repo was already indexed by anyone and its commit SHA is unchanged, the existing index is reused and just linked to the current user.

**Response:**
```json
{
  "url": "https://github.com/owner/repo",
  "status": "success",
  "message": "Repository indexed successfully",
  "file_count": 42
}
```

### Chat

```http
POST /api/chat
Content-Type: application/json

{ "url": "https://github.com/owner/repo", "question": "How does authentication work?", "conversation_id": 0 }
```

`conversation_id: 0` creates a new conversation; pass an existing id to continue it. Embeds the (possibly rewritten) question, runs hybrid retrieval (vector + full-text + filename, RRF-fused), expands and reranks chunks, generates an answer, and persists the messages.

**Response:**
```json
{
  "answer": "Authentication is handled with a React Context...",
  "conversation_id": 3,
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

### Data Access

```http
GET /api/repositories                 # repos linked to the current user
GET /api/repositories/{repo_id}       # single repo (ownership-checked)
GET /api/conversations                # all conversations for the current user
GET /api/conversations/{repo_id}      # conversations for a repo
GET /api/messages/{conversation_id}   # messages + sources (ownership-checked)
```

## Current Features

* Account registration, login, and logout (JWT access + rotating refresh tokens)
* GitHub repository ingestion (metadata, default branch, commit SHA)
* File filtering — source/config/docs kept; build/vendor/IDE/lockfiles ignored
* Language-aware code chunking with line-number metadata
* Local embeddings via sentence-transformers
* pgvector vector storage (HNSW index)
* Repository-scoped **hybrid retrieval** — semantic (pgvector) + full-text (tsvector) + filename match, RRF-fused, so both "how does auth work" and "show me render.yaml" succeed
* Same-file neighbor expansion around retrieved chunks
* **Jina AI reranking** (pool capped at 20) with a **relative** relevance threshold (top 8 context)
* Conversation-aware retrieval — history summaries + follow-up resolution
* RAG-based code explanations from Gemini
* Source links anchored to a commit SHA with exact line ranges (LLM never invents them)
* **PostgreSQL persistence** — users, repositories, conversations, messages, sources, refresh tokens
* **Next.js frontend** — login, register, dashboard, repository workspace, GPT-style chat UI, collapsible sources, conversation sidebar

## Project Structure

```text
RepoGuide/
│
├── backend/
│   ├── main.py             # FastAPI app + routes
│   ├── config.py           # env + constants
│   ├── schemas.py          # Pydantic request/response models
│   ├── auth.py             # JWT + bcrypt + rotating refresh tokens
│   ├── database.py         # async SQLAlchemy engine/session
│   ├── models.py           # ORM models (User, Repository, Conversation, ...)
│   ├── github.py           # GitHub API / ZIP download
│   ├── file_filter.py      # keep source files, drop noise
│   ├── chunking.py         # language-aware chunking with line numbers
│   ├── embeddings.py       # local sentence-transformers embeddings
│   ├── vector_storage.py   # pgvector add/query + FTS keyword + filename match
│   ├── reranking.py        # Jina AI reranker
│   ├── llm.py              # Gemini answer generation + conversation summary
│   ├── prompts.py          # system prompt + prompt builder
│   ├── rag.py              # index + ask pipelines
│   ├── requirements.txt
│   └── alembic/            # database migrations
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                  # landing
│   │   ├── login/page.tsx            # login
│   │   ├── register/page.tsx         # register
│   │   ├── dashboard/page.tsx        # repositories
│   │   └── repositories/[id]/page.tsx# repository workspace
│   ├── components/
│   │   ├── auth/ (AuthGuard, LoginForm, RegisterForm)
│   │   ├── chat/ (ChatWindow, ChatInput, SourcePanel, MessageContent, ConversationSidebar)
│   │   ├── layout/ (AppShell, LandingHeader, Logo)
│   │   └── repository/ (RepositoryInput, RepositoryWorkspace)
│   ├── lib/
│   │   ├── api/ (client, auth, chat, repositories, conversations)
│   │   ├── auth/ (AuthContext, token)
│   │   └── utils/repository.ts
│   └── types/api.ts
│
└── README.md
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key for answer generation |
| `JINA_API_KEY` | Yes | Jina AI API key for reranking |
| `DATABASE_URL` | Yes | Async PostgreSQL URL (e.g. `postgresql+asyncpg://...`) |
| `JWT_SECRET` | Yes | Secret for signing JWT access tokens |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend | Backend URL (defaults to `http://localhost:8000`) |

## Development Status

Pipeline is complete end-to-end: index → store → hybrid retrieve (vector + FTS + filename) → expand → rerank → generate → sources, with JWT auth, PostgreSQL persistence, conversations, and a full Next.js frontend.

### Know limitations

* **Embedding speed** — embeddings run locally on CPU; large repos index slowly
* **Single embedding stack** — query and index embeddings must use the same model

### Planned improvements

* Deploy production backend and frontend (Render / Vercel)
* Hosted embedding API for faster, quota-managed indexing
* Fine-tuned retrieval for harder, more abstract questions