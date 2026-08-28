import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EMBEDDING_MODEL = "models/gemini-embedding-001"
LLM_MODEL = "gemini-1.5-flash"

CHROMA_PERSIST_DIR = "./chroma_db"
