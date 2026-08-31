import chromadb
from .config import CHROMA_PERSIST_DIR


client=chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
collection=client.get_or_create_collection(name="code_chunks")

def query_chunks(owner:str,repo:str,embedding:list[float],k:int=5):
    result=collection.query(query_embeddings=[embedding],
                            n_results=k,
                            where={"$and":[{"owner":owner},{"repo":repo}]},
                            include=["documents","metadatas","distances"])
    return result["documents"][0],result["metadatas"][0],result["distances"][0]

def add_chunks(chunks:list[dict],embeddings:list[list[float]]):
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
