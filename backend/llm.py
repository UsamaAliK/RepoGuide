from google import genai
from google.genai import types
from .prompts import SYSTEM_PROMPT,build_answer_prompt
from .config import settings

# --- Gemini LLM client ---

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_answer(question:str,context:str,history:list[dict]|None=None)->str:
    """Send question + repo context to Gemini, return answer text."""
    response = client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=build_answer_prompt(question,context,history),
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
    )
    return response.text

def summarize_conversation(old_summary:str,conversation:list[dict])->str:
    """Merge old summary + newer messages into one compact rolling summary."""
    turns="\n\n".join(
        f"{'User' if msg['role']=='user' else 'Assistant'}: {msg['content']}"
        for msg in conversation
    )
    prompt=(
        "You are summarizing a repository-coding tutoring conversation.\n"
        "Merge the existing summary with the new messages into ONE compact summary.\n"
        "Rules:\n"
        "- Keep it under ~200 words.\n"
        "- Preserve key facts, questions asked, decisions, and planned next steps.\n"
        "- This is a code-learning conversation: preserve references to functions, "
        "files, line ranges, and repository topics so later answers stay coherent.\n"
        "- Do not invent new information. Only condense what actually happened.\n\n"
        f"Existing summary:\n{old_summary or '(none yet)'}\n\n"
        f"New messages:\n{turns}"
    )
    response = client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=prompt,
    )
    return response.text