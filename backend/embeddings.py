import google.generativeai as genai
import asyncio
from .config import GEMINI_API_KEY,EMBEDDING_MODEL,EMBEDDING_DIMENSIONS,EMBEDDING_BATCH_SIZE,EMBEDDING_MAX_CONCURRENCY

genai.configure(api_key=GEMINI_API_KEY)

def embed_batch(text:list[str],task_type="RETRIEVAL_DOCUMENT")->list[list[float]]:
    
    
        result=genai.embed_content( model=EMBEDDING_MODEL,
                content=text,
                output_dimensionality=EMBEDDING_DIMENSIONS,
                task_type=task_type
                )
        return result["embedding"]

async def embed_text(texts: list[str], task_type="RETRIEVAL_DOCUMENT",
                     batch_size=EMBEDDING_BATCH_SIZE,
                     max_concurrency=EMBEDDING_MAX_CONCURRENCY) -> list[list[float]]:
        if not texts:
            return []
        batch=[texts[i:i+batch_size]for i in range(0,len(texts),batch_size)]    
        semaphore=asyncio.Semaphore(max_concurrency)
        async def run(batch:list[str])->list[list]:
               async with semaphore:
                      return await asyncio.to_thread(embed_batch,batch,task_type)
        results=await asyncio.gather(*(run(b)for b in batch))
        return [v for result in results for v in result]

async def embed_query(text:str,task_type="RETRIEVAL_QUERY")->list[float]:
       return (await embed_text([text],task_type=task_type))[0]

               




