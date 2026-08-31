import google.generativeai as genai
from google.generativeai import GenerativeModel,generative_models
from .prompts import SYSTEM_PROMPT,build_answer_prompt
from .config import GEMINI_API_KEY,LLM_MODEL



genai.configure(api_key=GEMINI_API_KEY)

def generate_answer(question:str,context:str)->str:
    model=GenerativeModel(LLM_MODEL,system_instruction=SYSTEM_PROMPT)
    response=model.generate_content(build_answer_prompt(question,context))
    return response.text


