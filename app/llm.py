from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
import os
from fastapi.concurrency import run_in_threadpool

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def summarize_chat(messages: list[str]) -> str:
    prompt = "Summarize the following conversation:\n" + "\n".join(messages)
    model = genai.GenerativeModel("gemini-1.5-flash-8b")
    def sync_call():
        return model.generate_content(prompt).text
    return await run_in_threadpool(sync_call)

async def chat_insights(messages: list[str], insight_type: str) -> str:
    base = "\n".join(messages)
    if insight_type == "sentiment":
        prompt = f"Analyze the overall sentiment (positive, negative, neutral) of the following conversation:\n{base}"
    elif insight_type == "keywords":
        prompt = f"Extract the main topics or keywords from the following conversation:\n{base}"
    elif insight_type == "actions":
        prompt = f"List all action items or tasks mentioned in the following conversation:\n{base}"
    elif insight_type == "highlights":
        prompt = f"Extract the most important highlights from the following conversation:\n{base}"
    else:
        prompt = f"Provide insights for the following conversation:\n{base}"
    model = genai.GenerativeModel("gemini-1.5-flash-8b")
    def sync_call():
        return model.generate_content(prompt).text
    return await run_in_threadpool(sync_call) 