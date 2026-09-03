import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.rag import ask

URL = "https://github.com/alimasoodofficial/rec-lms-app"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rag_qa_test")
os.makedirs(OUT, exist_ok=True)

# (question, difficulty, use_llm)
QUESTIONS = [
    # --- 3 EASY ---
    ("List the three demo accounts and their passwords used for login.", "easy", True),
    ("Which role (admin, instructor, or student) does the app default to when a login doesn't match a demo account?", "easy", False),
    ("What localStorage keys does the app use for saving the session and a newly registered user?", "easy", False),
    # --- 4 MEDIUM ---
    ("How does the AuthContext restore a user session when the app first loads?", "medium", True),
    ("How are course details displayed on the course detail page, and where does the course data come from?", "medium", False),
    ("What does the logout function do step by step?", "medium", False),
    ("What actions are available in the admin users page and what data does each user record contain?", "medium", False),
    # --- 3 HARD ---
    ("Trace the complete login flow: from form submission in the login page, through the demo-account and localStorage checks, to how the session is set and the user is redirected.", "hard", True),
    ("Explain the difference between the 'rec_user' and 'rec_registered_user' localStorage keys and how they interact during registration followed by login.", "hard", False),
    ("Why does the app use localStorage and mock data instead of a real backend? Quote the code that reveals this design decision and explain the tradeoffs visible in the code.", "hard", False),
]


async def get_sources(question: str, top_k: int = 15):
    """Retrieve chunks + neighbors + rerank, and return only the sources (no LLM)."""
    from backend.embeddings import embed_batch
    from backend.vector_storage import query_chunks
    from backend.rag import find_neighbors, parse_github_url
    from backend.reranking import rerank

    info = parse_github_url(URL)
    owner, repo = info["owner"], info["repo"]
    qvec = await asyncio.to_thread(lambda: embed_batch([question])[0])

    docs, metas, distances = await asyncio.to_thread(query_chunks, owner, repo, qvec, top_k)
    if not docs:
        return []

    n_docs, n_metas = await asyncio.to_thread(find_neighbors, metas, owner, repo)
    all_docs = docs + n_docs
    all_metas = metas + n_metas
    all_dist = list(distances) + [0] * len(n_docs)

    # dedupe by location
    seen = set()
    dd, dm, ddist = [], [], []
    for d, m, dist in zip(all_docs, all_metas, all_dist):
        key = (m["file_path"], m["start_line"], m["end_line"])
        if key in seen:
            continue
        seen.add(key)
        dd.append(d); dm.append(m); ddist.append(dist)

    reranked = await rerank(question, dd, len(dd))
    final = [(dd[i], dm[i], score) for i, score in reranked[:8]]

    return [
        {
            "file_path": m["file_path"],
            "start_line": m["start_line"],
            "end_line": m["end_line"],
            "commit_sha": m["commit_sha"],
            "score": round(s, 5),
        }
        for _, m, s in final
    ]


async def main():
    llm_entries = []
    sources_entries = []

    for question, difficulty, use_llm in QUESTIONS:
        print(f"\n{'='*60}\n[{difficulty.upper()}] {'(LLM)' if use_llm else '(SOURCES-ONLY)'}: {question}\n{'='*60}")

        if use_llm:
            # full pipeline including LLM answer
            result = await ask(question, URL, 15)
            entry = {
                "question": question,
                "difficulty": difficulty,
                "answer": result["answer"],
                "sources": result["sources"],
            }
            llm_entries.append(entry)
            print("ANSWER (truncated):")
            print(result["answer"][:400])
            print("\nSOURCES:")
            for s in result["sources"]:
                print(f"  {s['file_path']}#L{s['start_line']}-L{s['end_line']}  score={s['score']}")
        else:
            # sources only — no LLM call
            sources = await get_sources(question)
            entry = {
                "question": question,
                "difficulty": difficulty,
                "sources": sources,
            }
            sources_entries.append(entry)
            print("SOURCES:")
            for s in sources:
                print(f"  {s['file_path']}#L{s['start_line']}-L{s['end_line']}  score={s['score']}")

    # save to separate files
    llm_path = os.path.join(OUT, "llm_answers.json")
    sources_path = os.path.join(OUT, "sources_only.json")
    with open(llm_path, "w") as f:
        json.dump({"repo": URL, "results": llm_entries}, f, indent=2)
    with open(sources_path, "w") as f:
        json.dump({"repo": URL, "results": sources_entries}, f, indent=2)

    print(f"\n\nSaved:\n  LLM answers + sources -> {llm_path}\n  Sources only         -> {sources_path}")
    print(f"\nStats: LLM-answered={len(llm_entries)}, Sources-only={len(sources_entries)}")


if __name__ == "__main__":
    asyncio.run(main())
