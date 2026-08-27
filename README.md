# RepoGuide

> Understand any codebase like someone who built it explained it to you.

## What is RepoGuide?

RepoGuide is your personal guide for learning codebases. Ask questions about how the code works, understand the architecture, learn best practices — get answers with source code examples.

**Perfect for:**
- 📚 **Learning frameworks** — Deep dive into Crew AI, FastAPI, LangChain
- 🧠 **Understanding architecture** — "Why are files organized this way?"
- 🎓 **Educational exploration** — Learn patterns and best practices from real code
- 🚀 **Onboarding** — New to a codebase? Learn faster with guided Q&A
- 💡 **Reverse engineering** — Understand *how* and *why* things work

## How it works

RepoGuide uses a hybrid retrieval-augmented generation (RAG) approach optimized for code understanding.

1. **Index** — User provides a GitHub repository URL. The repo is fetched as a ZIP and extracted.
2. **Chunk + Embed** — Source files are split into semantic chunks with precise metadata (file paths, line numbers, commit SHA), converted to embeddings, and stored in a vector database. Raw source code is not stored — GitHub remains the single source of truth.
3. **Ask** — User asks a question about the codebase.
4. **Retrieve** — Relevant code chunks are retrieved from the vector database via semantic search.
5. **Answer** — Chunks are passed to the Gemini LLM for context-aware answers with clickable links back to the exact lines on GitHub.

### Architecture

```
NEXT.JS
   │
   │  HTTP / JWT
   ▼
FASTAPI
   │
   ├────────────┬────────────┐
   ▼            ▼            ▼
PostgreSQL   Vector DB    GitHub
```

## Database Schema

### PostgreSQL — Users, Repositories, Conversations

**users**
```
├── id
├── email
├── password_hash
└── created_at
```

**repositories**
```
├── id
├── user_id
├── owner
├── repo
├── default_branch
├── commit_sha
└── created_at
```

**conversations**
```
├── id
├── user_id
├── repository_id
├── current_topic
└── created_at
```

**messages**
```
├── id
├── conversation_id
├── role
├── content
└── created_at
```

### pgvector — Code Chunks

**chunks**
```
├── id
├── embedding
├── content
├── repository_id
├── file_path
├── start_line
├── end_line
├── commit_sha
├── owner
└── repo
```

### Relationships

```
users         1 ──── * repositories
users         1 ──── * conversations
repositories  1 ──── * conversations
conversations 1 ──── * messages
repositories  1 ──── * chunks (vector DB)
```

Auto-generated JWT tokens authenticate users; both the SQL backend and vector search work together per indexed repository.

---

## File Structure

```
RepoGuide/
├── backend/
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # Configuration & environment variables
│   ├── database.py      # Database setup & connection
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── github.py        # GitHub API integration
│   ├── embeddings.py    # Vector embeddings
│   ├── chunking.py      # Code chunking logic
│   ├── llm.py           # LLM integration
│   └── prompts.py       # Prompt templates
├── frontend/
│   ├── index.html       # Main HTML page
│   ├── script.js        # Frontend logic
│   └── style.css        # Styling
├── .env                 # Environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Status

🚧 Work in Progress - Building core functionality

More details coming soon.
