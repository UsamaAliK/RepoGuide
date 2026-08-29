import google.generativeai as genai
import os
from .config import GEMINI_API_KEY,EMBEDDING_MODEL,EMBEDDING_DIMENSIONS

genai.configure(api_key=GEMINI_API_KEY)

def embed_text(text:list[str],batch_size:int=10,task_type="RETRIEVAL_DOCUMENT")->list[list[float]]:
    vectors=[]
    for i in range(0,len(text),batch_size):
        batch=text[i: i+batch_size]
        result=genai.embed_content( model=EMBEDDING_MODEL,
                content=batch,
                output_dimensionality=EMBEDDING_DIMENSIONS,
                task_type=task_type
                )
        vectors.extend(result["embedding"])
    return vectors

