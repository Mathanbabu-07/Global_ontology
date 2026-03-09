import sys
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

prompt = """You are an intelligence extraction engine.

Analyze the provided article and extract structured geopolitical or strategic intelligence.

Return ONLY valid JSON with the following structure:
{
  "domain": "geopolitics",
  "event_title": "Test",
  "summary": "This is a test",
  "impact": "None",
  "timestamp": "",
  "entities": [],
  "relationships": []
}

Allowed domains: geopolitics, economics, defense, technology, climate, society
Only return JSON. No extra text, no markdown code blocks.

Article: The US and UK signed a new trade deal today regarding artificial intelligence research.
"""

payload = {
    "model": "nvidia/nemotron-3-nano-30b-a3b:free",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.1,
    "max_tokens": 1000
}

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    json=payload
)

print(f"Status: {response.status_code}")
res = response.json()
msg = res.get("choices", [{}])[0].get("message", {})
print("--- CONTENT ---")
print(repr(msg.get("content")))
print("--- REASONING ---")
print(repr(msg.get("reasoning")))
