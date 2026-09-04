import chromadb
from .config import settings

# --- chroma setup (single collection for all repos) ---

client=chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
collection=client.get_or_create_collection(name="code_chunks")

# --- queries ---

def query_chunks(owner:str,repo:str,embedding:list[float],k:int=5):
    """Semantic search: return top-k chunks for a repo by embedding similarity."""
    result=collection.query(query_embeddings=[embedding],
                            n_results=k,
                            where={"$and":[{"owner":owner},{"repo":repo}]},
                            include=["documents","metadatas","distances"])
    return result["documents"][0],result["metadatas"][0],result["distances"][0]

def get_file_chunks(owner:str,repo:str,file_path:str):
    """Return all chunks stored for a single file (used by neighbor expansion)."""
    result=collection.get(
        where={"$and":[{"owner":owner},{"repo":repo},{"file_path":file_path}]},
        include=["documents","metadatas"],
    )
    return result["documents"],result["metadatas"]

# --- writes ---

def add_chunks(chunks:list[dict],embeddings:list[list[float]]):
    """Store chunks + embeddings. Deletes existing repo chunks first (re-index safe)."""
    if not chunks:
        return
    if len(chunks)!=len(embeddings):
        raise ValueError(f"chunks embeddings mismatch . {len(chunks)} vs {len(embeddings)}")
    owner=chunks[0]["metadata"]["owner"]
    repo=chunks[0]["metadata"]["repo"]
    collection.delete(where={"$and":[{"owner":owner},{"repo":repo}]})
    ids=[
        f"{owner}/{repo}:{c['metadata']['file_path']}:{c['metadata']['start_line']}-{c['metadata']['end_line']}:{i}"
        for i, c in enumerate(chunks)
    ]
    collection.add(
        ids=ids,
        documents=[c["text"]for c in chunks],
        metadatas=[c["metadata"]for c in chunks],
        embeddings=embeddings
    )
