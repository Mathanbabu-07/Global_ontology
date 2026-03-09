import sys
import json
import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

prompt = """You are an intelligence extraction engine.

Analyze the provided article and extract structured geopolitical or strategic intelligence.

IMPORTANT INSTRUCTION: DO NOT output any reasoning, thinking, explanations, or conversational text. 
You must output ONLY the raw JSON object and absolutely nothing else.

Return ONLY valid JSON with the following structure:

{
  "domain": "",
  "event_title": "",
  "summary": "",
  "impact": "",
  "timestamp": "",
  "entities": [
    {"name": "", "type": ""}
  ],
  "relationships": [
    {"source": "", "relation": "", "target": ""}
  ]
}

Allowed domains: geopolitics, economics, defense, technology, climate, society
Only return JSON. No extra text, no markdown code blocks.

Article: The US and UK signed a new trade deal today regarding artificial intelligence research.
"""

payload = {
    "model": "nvidia/nemotron-3-nano-30b-a3b:free",
    "messages": [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Analyze the following article from https://reuters.com/\n\nArticle: The US and UK signed a new trade deal today regarding artificial intelligence research."}
    ],
    "temperature": 0.1,
    "max_tokens": 2000
}

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    json=payload,
    timeout=120
)

print(f"Status: {response.status_code}")
res = response.json()
msg = res.get("choices", [{}])[0].get("message", {})

content = msg.get("content")
reasoning = msg.get("reasoning")
print(f"Has Content: {bool(content)}")
print(f"Has Reasoning: {bool(reasoning)}")

if not content and reasoning:
    print("Using reasoning as content fallback")
    content = reasoning
elif not content and not reasoning:
    print("Both empty!")
    sys.exit(1)

# Clean
# If content starts with '{' and ends with '}', try parsing directly
content = content.strip()
print("--- RAW STRIPPED ---")
print(repr(content))

if content.startswith("{") and content.endswith("}"):
    try:
        json.loads(content)
        print("Parsed via start/end match!")
        sys.exit(0)
    except ValueError:
        pass

# Try to find JSON object using a greedy regex from the first { to the last }
match = re.search(r'\{.*\}', content, re.DOTALL)
if match:
    candidate = match.group(0)
    try:
        json.loads(candidate)
        print("Parsed via regex match!")
        print(repr(candidate))
        sys.exit(0)
    except ValueError as e:
        print(f"Regex matched but JSON invalid: {e}")

print("FAILED TO PARSE")
