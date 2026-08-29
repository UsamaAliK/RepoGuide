import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS=768
LLM_MODEL = "gemini-2.5-flash"

CHROMA_PERSIST_DIR = "./chroma_db"
