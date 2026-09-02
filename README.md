# RepoGuide

> Understand any codebase like someone who built it explained it to you.

## What is RepoGuide?

RepoGuide is an AI-powered GitHub repository tutor that helps developers understand unfamiliar codebases.

Give it a GitHub repository and ask questions about how the code works, how different files interact, or why certain implementation patterns are used.

### Perfect for

* 📚 **Learning frameworks** — Explore real-world projects using FastAPI, LangChain, CrewAI, and more
* 🧠 **Understanding architecture** — Learn how different parts of a codebase fit together
* 🎓 **Educational exploration** — Learn programming patterns from real projects
* 🚀 **Onboarding** — Understand an unfamiliar codebase faster
* 💡 **Reverse engineering** — Trace how functionality works across a repository

## How It Works

RepoGuide uses Retrieval-Augmented Generation (RAG) designed for codebase understanding.

### 1. Index

The user provides a GitHub repository URL.

RepoGuide retrieves the repository and extracts its source files.

### 2. Chunk & Embed

Source files are split into code-aware chunks.

Each chunk is stored with metadata such as:

* File path
* Start and end line
* Repository
* Commit SHA

The chunks are converted into embeddings and stored in a vector database.

### 3. Ask

The user asks a question about the repository.

### 4. Retrieve

The question is converted into an embedding and relevant code chunks are retrieved using semantic similarity search.

### 5. Generate

The retrieved code is provided to the Gemini LLM as context.

The model uses the retrieved repository code to generate an explanation while avoiding unsupported assumptions.

## Current Architecture

```text
GitHub Repository
        │
        ▼
 GitHub API / ZIP
        │
        ▼
 File Filtering
        │
        ▼
  Code Chunking
        │
        ▼
 Gemini Embeddings
        │
        ▼
    ChromaDB
        │
        ▼
 Semantic Retrieval
        │
        ▼
   Gemini LLM
        │
        ▼
     Answer
```

FastAPI provides the API layer between the application and the RAG pipeline.

## Current Features

* GitHub repository ingestion
* Repository metadata and commit SHA tracking
* File filtering
* Language-aware code chunking
* Gemini embeddings
* ChromaDB vector storage
* Repository-scoped semantic retrieval
* RAG-based code explanations
* FastAPI API endpoints
* Chunk metadata containing file and line information
* Prompting designed to reduce unsupported assumptions

## API

### Index Repository

```http
POST /index
```

Indexes a GitHub repository and stores its embedded code chunks.

### Ask a Question

```http
POST /ask
```

Retrieves relevant code from the indexed repository and generates an answer using Gemini.

## Tech Stack

* **Python**
* **FastAPI**
* **ChromaDB**
* **Google Gemini**
* **LangChain Text Splitters**
* **GitHub REST API**

## Project Structure

```text
RepoGuide/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── github.py
│   ├── file_filter.py
│   ├── embeddings.py
│   ├── chunking.py
│   ├── vector_storage.py
│   ├── llm.py
│   ├── prompts.py
│   └── rag.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Roadmap

The current version focuses on building a reliable baseline RAG pipeline.

Planned improvements include:

* 🔗 **Relationship-aware retrieval** — Follow relationships between retrieved code chunks to retrieve additional relevant context
* 🔍 **Reranking** — Improve relevance of retrieved chunks before sending them to the LLM
* 🧩 **Multi-hop retrieval** — Retrieve related code when a question requires understanding multiple parts of the repository
* 💬 **Conversation history** — Persistent conversations for each repository
* 🔐 **Authentication** — User accounts and JWT-based authentication
* 🗄️ **PostgreSQL integration** — Persistent users, repositories, and conversations
* 🌐 **Production deployment**
* 🎨 **Improved frontend experience**

## Status

🚧 **Active Development**

The core repository indexing and RAG pipeline is working.

The project is currently being improved with more advanced retrieval techniques to better handle questions that require understanding relationships between different parts of a codebase.
