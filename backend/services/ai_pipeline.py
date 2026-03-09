import json
import requests
import re
from config import config

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Using NVIDIA free model via OpenRouter
MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2:free"


def analyze_content(text, domain="general"):
    """
    Send extracted text content to OpenRouter (NVIDIA model) for structured analysis.
    Returns structured intelligence data: summary, entities, events, relationships.
    """
    try:
        if not config.OPENROUTER_API_KEY:
            return {
                "summary": "OpenRouter API key not configured. Please add your key to the .env file.",
                "entities": [],
                "events": [],
                "relationships": [],
            }

        system_prompt = f"""You are an intelligence analyst working on a Global Ontology Engine.
Your task is to analyze the provided content and extract structured intelligence data.

IMPORTANT INSTRUCTION: DO NOT output any reasoning, thinking, explanations, or conversational text. 
You must output ONLY the raw JSON object and absolutely nothing else.

Domain focus: {domain}

Respond ONLY with valid JSON in this exact format:
{{
    "summary": "A concise 2-3 sentence summary of the key intelligence from the content",
    "entities": ["list of important named entities like people, organizations, countries, technologies"],
    "events": ["list of key events or developments mentioned"],
    "relationships": ["list of notable relationships between entities, e.g. 'India signed trade deal with Japan'"]
}}

Rules:
- Focus on factual, verifiable intelligence
- Prioritize geopolitical, economic, defense, technology, climate, or social relevance
- Keep entity names short and precise
- Maximum 10 items per list
- If the content is not relevant, still provide what you can extract"""

        headers = {
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Global Ontology Engine",
        }

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text[:4000]},  # Limit content length
            ],
            "temperature": 0.1,
            "max_tokens": 1000,
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=120)

        if response.status_code != 200:
            print(f"[AI Pipeline] OpenRouter error [{response.status_code}]: {response.text[:200]}")
            return {
                "summary": f"AI processing error (status {response.status_code})",
                "entities": [],
                "events": [],
                "relationships": [],
            }

        result = response.json()
        message = result["choices"][0]["message"]
        content = message.get("content")

        if not content:
            reasoning = message.get("reasoning", "")
            if reasoning:
                content = reasoning
            else:
                return {
                    "summary": "AI returned empty content.",
                    "entities": [],
                    "events": [],
                    "relationships": [],
                }

        # Parse JSON from response (handle markdown code blocks)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Extract JSON object using regex if there's extra text
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            candidate = match.group(0)
            try:
                parsed = json.loads(candidate)
                print(f"[AI Pipeline] Analysis complete \u2014 {len(parsed.get('entities', []))} entities extracted")
                return parsed
            except ValueError:
                pass

        parsed = json.loads(content)
        print(f"[AI Pipeline] Analysis complete — {len(parsed.get('entities', []))} entities extracted")
        return parsed

    except json.JSONDecodeError:
        # If AI didn't return valid JSON, wrap the raw text response
        return {
            "summary": content if 'content' in dir() else "Failed to parse AI response",
            "entities": [],
            "events": [],
            "relationships": [],
        }
    except Exception as e:
        print(f"[AI Pipeline] Error: {e}")
        return {
            "summary": f"Error during AI analysis: {str(e)}",
            "entities": [],
            "events": [],
            "relationships": [],
        }
