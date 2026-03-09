import json
import requests
import time
import re
from config import config
from supabase import create_client

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Ordered list of models to try — if the first fails, fall back to the next
MODELS = [
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "openrouter/free",
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "mistralai/mistral-nemo:free",
    "qwen/qwen3-next-80b-a3b-instruct:free"
]

EXTRACTION_PROMPT = """You are an elite intelligence extraction engine.

Analyze the provided article and extract structured geopolitical or strategic intelligence.

CRITICAL INSTRUCTION: You MUST output ONLY valid JSON. 
DO NOT output any reasoning, thinking, explanations, warnings, or conversational text. 
Start your response with '{' and end with '}'.

Return ONLY valid JSON with EXACTLY this structure:

{
  "domain": "one of the allowed domains",
  "event_title": "Clear, concise title of the event",
  "summary": "Brief 1-2 sentence summary of what happened.",
  "impact": "Brief description of the geopolitical/economic impact.",
  "timestamp": "Date or time of the event if mentioned, else empty string",
  "entities": [
    {"name": "Entity Name", "type": "one of the allowed entity types"}
  ],
  "relationships": [
    {"source": "Entity 1", "relation": "one of the allowed relationship types", "target": "Entity 2"}
  ]
}

Allowed domains: geopolitics, economics, defense, technology, climate, society
Allowed entity types: country, organization, person, technology, resource, location
Allowed relationship types: imports, exports, alliance, sanctions, develops, invests, conflict

Only return JSON. No extra text, no markdown code blocks. NO EXCEPTIONS."""


def _clean_json_content(raw):
    """
    Clean raw AI response text to extract valid JSON.
    Handles markdown fences, extra text before/after JSON, etc.
    """
    if not raw:
        return None

    content = raw.strip()

    # Start by trying natural parse
    try:
        json.loads(content)
        return content
    except ValueError:
        pass

    # Look for markdown code blocks
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
    if match:
        candidate = match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except ValueError:
            pass

    # Try grabbing everything from the first { to the last }
    first_brace = content.find('{')
    last_brace = content.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = content[first_brace:last_brace+1]
        try:
            json.loads(candidate)
            return candidate
        except ValueError:
            pass

    return content



def _call_openrouter(headers, payload, model_name):
    """
    Make an API call to OpenRouter with retry logic.
    Returns the parsed JSON response or raises an exception.
    """
    max_retries = 3
    retry_delay = 3

    for attempt in range(max_retries):
        try:
            response = requests.post(
                OPENROUTER_API_URL, headers=headers, json=payload, timeout=120
            )

            if response.status_code == 200:
                return response.json()

            # Rate limited — wait and retry
            if response.status_code == 429:
                wait = retry_delay * (attempt + 1)
                print(f"[Intelligence] Rate limited on {model_name}, waiting {wait}s...")
                time.sleep(wait)
                continue

            # Other HTTP error
            print(f"[Intelligence] {model_name} returned HTTP {response.status_code}: {response.text[:200]}")
            return None

        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                print(f"[Intelligence] Connection error, retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"[Intelligence] Connection failed after {max_retries} attempts: {e}")
                return None
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"[Intelligence] Timeout, retrying... (Attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"[Intelligence] Timeout after {max_retries} attempts")
                return None
        except Exception as e:
            print(f"[Intelligence] Unexpected error calling {model_name}: {e}")
            return None

    return None


def extract_intelligence(text, source_url):
    """
    Send cleaned article text to OpenRouter and extract structured intelligence.
    Tries multiple models in order until one succeeds.
    Returns a dict with domain, event_title, summary, impact, timestamp, entities, relationships.
    """
    if not config.OPENROUTER_API_KEY:
        return {
            "error": "OpenRouter API key not configured",
            "domain": "unknown",
            "event_title": "Configuration Error",
            "summary": "Please add your OPENROUTER_API_KEY to the .env file.",
            "impact": "None",
            "timestamp": "",
            "entities": [],
            "relationships": [],
        }

    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Global Ontology Engine",
    }

    # Truncate text to 4000 chars to stay within limits and improve quality
    article_text = text[:4000] if text else ""

    for model in MODELS:
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": EXTRACTION_PROMPT},
                    {
                        "role": "user",
                        "content": f"Analyze the following article from {source_url}:\n\n{article_text}",
                    },
                ],
                "temperature": 0.1,
                "max_tokens": 8192,
            }

            print(f"[Intelligence] Trying model: {model}")
            result = _call_openrouter(headers, payload, model)

            if not result:
                print(f"[Intelligence] No response from {model}, trying next...")
                continue

            # Extract content from the response
            choices = result.get("choices", [])
            if not choices:
                print(f"[Intelligence] No choices from {model}: {json.dumps(result)[:200]}")
                continue

            message = choices[0].get("message", {})
            content = message.get("content")

            # Some models (like Nemotron) put output in "reasoning" instead of "content"
            if not content:
                reasoning = message.get("reasoning", "")
                if reasoning:
                    print(f"[Intelligence] {model} returned output in 'reasoning' field. Using it.")
                    content = reasoning
                else:
                    print(f"[Intelligence] {model} returned empty content, trying next model...")
                    continue

            # Clean and parse the JSON
            print(f"[Intelligence] Raw content length: {len(content)}")
            with open("last_ai_response.txt", "w", encoding="utf-8") as f:
                f.write(content)
            
            cleaned = _clean_json_content(content)
            if not cleaned:
                print(f"[Intelligence] Could not extract JSON from {model} response. First 500 chars: {content[:500]}")
                continue

            parsed = json.loads(cleaned)

            # Validate and set defaults
            ALLOWED_DOMAINS = [
                "geopolitics", "economics", "defense",
                "technology", "climate", "society",
            ]
            if parsed.get("domain", "").lower() not in ALLOWED_DOMAINS:
                parsed["domain"] = "geopolitics"
            else:
                parsed["domain"] = parsed["domain"].lower()

            parsed.setdefault("event_title", "Untitled Event")
            parsed.setdefault("summary", "")
            parsed.setdefault("impact", "")
            parsed.setdefault("timestamp", "")
            parsed.setdefault("entities", [])
            parsed.setdefault("relationships", [])

            print(
                f"[Intelligence] Extracted: '{parsed['event_title']}' "
                f"({len(parsed['entities'])} entities, {len(parsed['relationships'])} relationships) "
                f"using {model}"
            )
            return parsed

        except json.JSONDecodeError as e:
            cleaned_text = repr(cleaned[:100]) if 'cleaned' in locals() and cleaned else 'None'
            print(f"[Intelligence] JSON parse error with {model}: {e}. Cleaned (first 100 chars): {cleaned_text}")
            continue
        except Exception as e:
            print(f"[Intelligence] Error with {model}: {e}")
            continue

    # All models failed
    print("[Intelligence] All models failed to extract intelligence")
    return {
        "error": "All AI models failed to extract intelligence",
        "domain": "unknown",
        "event_title": "Extraction Error",
        "summary": "The AI service could not process this article. Please try again later.",
        "impact": "",
        "timestamp": "",
        "entities": [],
        "relationships": [],
    }


def store_intelligence(data, source_url):
    """
    Store extracted intelligence data into Supabase tables:
    - extracted_events
    - entities
    - relationships
    Returns the event record with its ID.
    """
    try:
        if data.get("domain") == "unknown" and data.get("event_title") == "Extraction Error":
            print("[Intelligence] Error detected, skipping database insertion to keep feed clean.")
            return data

        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)

        # 1. Insert into extracted_events
        event_record = {
            "source_url": source_url,
            "domain": data.get("domain", "geopolitics"),
            "event_title": data.get("event_title", "Untitled"),
            "summary": data.get("summary", ""),
            "impact": data.get("impact", ""),
            "timestamp": data.get("timestamp", "") or None,
        }

        event_result = db.table("extracted_events").insert(event_record).execute()

        if not event_result.data:
            print("[Intelligence] Failed to insert event")
            return None

        event_id = event_result.data[0]["id"]
        print(f"[Intelligence] Stored event: {event_id}")

        # 2. Insert entities
        entities = data.get("entities", [])
        if entities:
            entity_records = []
            for entity in entities:
                if isinstance(entity, dict):
                    entity_records.append({
                        "event_id": event_id,
                        "entity_name": entity.get("name", ""),
                        "entity_type": entity.get("type", "organization"),
                    })
                elif isinstance(entity, str):
                    entity_records.append({
                        "event_id": event_id,
                        "entity_name": entity,
                        "entity_type": "organization",
                    })

            if entity_records:
                db.table("entities").insert(entity_records).execute()
                print(f"[Intelligence] Stored {len(entity_records)} entities")

        # 3. Insert relationships
        relationships = data.get("relationships", [])
        if relationships:
            rel_records = []
            for rel in relationships:
                if isinstance(rel, dict):
                    rel_records.append({
                        "event_id": event_id,
                        "source_entity": rel.get("source", ""),
                        "relation": rel.get("relation", ""),
                        "target_entity": rel.get("target", ""),
                    })

            if rel_records:
                db.table("relationships").insert(rel_records).execute()
                print(f"[Intelligence] Stored {len(rel_records)} relationships")

        # Run the modular Knowledge Graph Creation pipeline
        try:
            from services.knowledge_graph import build_knowledge_graph
            kg_result = build_knowledge_graph(data, data.get("domain", "geopolitics"))
            print(f"[Intelligence] Knowledge Graph synced: {len(kg_result['nodes'])} nodes, {len(kg_result['edges'])} edges")
        except Exception as kg_e:
            print(f"[Intelligence] Failed to build knowledge graph: {kg_e}")

        # Return full event data
        return {
            **event_result.data[0],
            "entities": entities,
            "relationships": relationships,
            "knowledge_graph": kg_result if 'kg_result' in locals() else None,
        }

    except Exception as e:
        print(f"[Intelligence] Storage error: {e}")
        return None
