import os
from dotenv import load_dotenv

load_dotenv()

# --- env + constants ---
class Settings():

  GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
  DATABASE_URL = os.getenv("DATABASE_URL")
  JWT_SECRET = os.getenv("JWT_SECRET")
  JWT_ALGORITHM = "HS256"
  JWT_EXPIRES_MINUTES=15
  REFRESH_TOKEN_EXPIRE_DAYS=30
  EMBEDDING_MODEL = "all-MiniLM-L6-v2"
  EMBEDDING_DIMENSIONS=384
  EMBEDDING_BATCH_SIZE=50
  EMBEDDING_MAX_CONCURRENCY=1
  LLM_MODEL = "gemini-2.5-flash"

settings = Settings()