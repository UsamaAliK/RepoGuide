import chromadb
from .config import CHROMA_PERSIST_DIR


client=chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
collection=client.get_or_create_collection(name="code_chunks")
