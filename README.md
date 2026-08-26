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

1. User provides GitHub repository URL
2. Repository files are indexed with embeddings
3. User asks questions about the codebase
4. AI finds relevant code and explains it
5. Answers include links to source files




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
