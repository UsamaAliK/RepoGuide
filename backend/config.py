import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS=768
EMBEDDING_BATCH_SIZE=50
EMBEDDING_MAX_CONCURRENCY=8
LLM_MODEL = "gemini-2.5-flash"

CHROMA_PERSIST_DIR = "./chroma_db"
