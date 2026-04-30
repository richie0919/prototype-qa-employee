import os
import requests
from dotenv import load_dotenv

load_dotenv()

LLM_HOST = os.getenv("LLM_HOST")
LLM_MODEL = os.getenv("LLM_MODEL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

def ask_llm(messages):
    url = f"{LLM_HOST}/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "hyfindr-ai-agent"
    }

    data = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0
    }

    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    if "choices" not in response_json:
        raise Exception(f"LLM Error: {response_json}")


    return response_json["choices"][0]["message"]["content"]