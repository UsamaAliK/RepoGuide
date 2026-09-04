from google import genai
from google.genai import types
from .prompts import SYSTEM_PROMPT,build_answer_prompt
from .config import settings

# --- Gemini LLM client ---

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_answer(question:str,context:str)->str:
    """Send question + repo context to Gemini, return answer text."""
    response = client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=build_answer_prompt(question,context),
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
    )
    return response.text


