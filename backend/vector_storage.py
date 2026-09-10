from sqlalchemy import Column, Integer, String, Text, text, bindparam
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import DeclarativeBase
from .database import engine
from .config import settings


class Base(DeclarativeBase):
    pass


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True)
    owner = Column(String(100), nullable=False)
    repo = Column(String(100), nullable=False)
    commit_sha = Column(String(40), nullable=False)
    file_path = Column(String(500), nullable=False)
    language = Column(String(50))
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=False)


embedding_param = bindparam("embedding", type_=Vector(settings.EMBEDDING_DIMENSIONS))


async def add_chunks(chunks, embeddings):
    """Store chunks + embeddings. Only re-indexes if commit_sha changed."""
    if not chunks:
        return
    if len(chunks) != len(embeddings):
        raise ValueError(f"chunks embeddings mismatch: {len(chunks)} vs {len(embeddings)}")

    owner = chunks[0]["metadata"]["owner"]
    repo = chunks[0]["metadata"]["repo"]
    commit_sha = chunks[0]["metadata"]["commit_sha"]

    async with engine.begin() as conn:
        existing = await conn.execute(
            text("SELECT commit_sha FROM chunks WHERE owner = :owner AND repo = :repo LIMIT 1"),
            {"owner": owner, "repo": repo}
        )
        row = existing.fetchone()
        if row and row[0] == commit_sha:
            return

        await conn.execute(
            text("DELETE FROM chunks WHERE owner = :owner AND repo = :repo"),
            {"owner": owner, "repo": repo}
        )

        for chunk, embedding in zip(chunks, embeddings):
            meta = chunk["metadata"]
            await conn.execute(
                text("""
                    INSERT INTO chunks (owner, repo, commit_sha, file_path, language, start_line, end_line, content, embedding)
                    VALUES (:owner, :repo, :commit_sha, :file_path, :language, :start_line, :end_line, :content, :embedding)
                """).bindparams(embedding_param),
                {
                    "owner": meta["owner"],
                    "repo": meta["repo"],
                    "commit_sha": meta["commit_sha"],
                    "file_path": meta["file_path"],
                    "language": meta.get("language"),
                    "start_line": meta["start_line"],
                    "end_line": meta["end_line"],
                    "content": chunk["text"],
                    "embedding": embedding,
                }
            )

async def query_chunks(owner, repo, embedding, k=5):
    """Semantic search: return top-k chunks for a repo by embedding similarity."""
    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT content, owner, repo, commit_sha, file_path, start_line, end_line, language,
                       embedding <=> :embedding AS distance
                FROM chunks
                WHERE owner = :owner AND repo = :repo
                ORDER BY embedding <=> :embedding
                LIMIT :k
            """).bindparams(embedding_param),
            {"owner": owner, "repo": repo, "embedding": embedding, "k": k}
        )
        rows = result.fetchall()

    documents = [row[0] for row in rows]
    metadatas = [
        {
            "owner": row[1], "repo": row[2], "commit_sha": row[3],
            "file_path": row[4], "start_line": row[5], "end_line": row[6],
            "language": row[7],
        }
        for row in rows
    ]
    distances = [row[8] for row in rows]
    return documents, metadatas, distances


async def get_file_chunks(owner, repo, file_path):
    """Return all chunks stored for a single file (used by neighbor expansion)."""
    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT content, owner, repo, commit_sha, file_path, start_line, end_line, language
                FROM chunks
                WHERE owner = :owner AND repo = :repo AND file_path = :file_path
            """),
            {"owner": owner, "repo": repo, "file_path": file_path}
        )
        rows = result.fetchall()

    documents = [row[0] for row in rows]
    metadatas = [
        {
            "owner": row[1], "repo": row[2], "commit_sha": row[3],
            "file_path": row[4], "start_line": row[5], "end_line": row[6],
            "language": row[7],
        }
        for row in rows
    ]
    return documents, metadatas