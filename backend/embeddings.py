import google.generativeai as genai
import os
from .config import GEMINI_API_KEY,EMBEDDING_MODEL

genai.configure(api_key=GEMINI_API_KEY)

def embed_text(text:list[str],batch_size:int=10)->list[list[float]]:
    vectors=[]
    for i in range(0,len(text),batch_size):
        batch=text[i: i+batch_size]
        result=genai.embed_content(model=EMBEDDING_MODEL,content=batch)
        vectors.extend(result["embedding"])
    return vectors
