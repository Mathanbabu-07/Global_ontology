import json
import requests
import re
from supabase import create_client
from config import config

def build_ontology_from_content(content: str, url: str):
    """
    Given the scraped content, uses Gemini 2.5 Flash to extract nodes and edges.
    Stores them in Supabase.
    Return structured graph object.
    """
    print(f"[Ontology] Extracting graph for {url}")
    
    api_key = config.GEMINI_API_KEY
    if not api_key:
        return {"error": "GEMINI_API_KEY is not set in backend/.env"}

    prompt = """You are a global intelligence ontology engine.

Analyze the provided article and identify entities and relationships between them.

Return JSON in this format:

{
"entities": [
{"name":"", "type":""}
],
"relationships": [
{"source":"", "relation":"", "target":""}
]
}

Entity types allowed: country, organization, person, technology, resource, location, event.

Relationship types allowed: imports, exports, sanctions, develops, invests, alliance, conflict, controls, influences.

Only return JSON.
"""

    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt + "\n\nArticle:\n" + content[:10000]}]
        }]
    }

    try:
        response = requests.post(gemini_url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        res_data = response.json()
        
        # Parse Gemini response
        text = res_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        if not text:
            return {"error": "Empty response from Gemini"}
            
        print(f"[Ontology] Raw Gemini response ({len(text)} chars)")
        
        # Clean markdown if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].strip()
            
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            text = match.group(0)
            
        data = json.loads(text)
        
        # Use Supabase
        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
        
        nodes_added = []
        edges_added = []
        
        domain = "general" # Enhancements could have Gemini predict this
        
        # Insert nodes
        for ent in data.get("entities", []):
            name = ent.get("name")
            etype = ent.get("type", "organization")
            if not name: continue
            
            # Check if exists
            existing = db.table("graph_nodes").select("id").eq("entity_name", name).execute()
            if not existing.data:
                node_res = db.table("graph_nodes").insert({
                    "entity_name": name,
                    "entity_type": etype,
                    "domain": domain
                }).execute()
                if node_res.data:
                    nodes_added.append(name)
        
        # Insert edges
        for rel in data.get("relationships", []):
            source = rel.get("source")
            target = rel.get("target")
            relation = rel.get("relation")
            if not source or not target or not relation: continue
            
            # Note: For strict correctness we should check if source/target exist as nodes, if not create them.
            # But the AI should have outputted them in "entities".
            
            # Check if edge already exists
            existing_edge = db.table("graph_edges").select("id").eq("source_node", source).eq("target_node", target).eq("relation", relation).execute()
            if not existing_edge.data:
                edge_res = db.table("graph_edges").insert({
                    "source_node": source,
                    "relation": relation,
                    "target_node": target,
                    "event_reference": url
                }).execute()
                if edge_res.data:
                    edges_added.append({"source": source, "target": target, "relation": relation})
        
        return {
            "success": True,
            "nodes_added": len(nodes_added),
            "edges_added": len(edges_added),
            "entities": data.get("entities", []),
            "relationships": data.get("relationships", [])
        }

    except Exception as e:
        print(f"[Ontology] Error: {e}")
        return {"error": str(e)}


def generate_insights_from_events(events_data: list):
    """
    Given a list of event objects (from extracted_events), uses Gemini 2.5 Flash to 
    reason out hidden connections and generate a new structured graph payload.
    """
    print(f"[Ontology] Generating insights for {len(events_data)} events")
    
    api_key = config.GEMINI_API_KEY
    if not api_key:
        return {"error": "GEMINI_API_KEY is not set in backend/.env"}

    # Prepare context
    context_text = ""
    for idx, e in enumerate(events_data):
        context_text += f"\nEvent {idx+1}:\nTitle: {e.get('event_title')}\nSummary: {e.get('summary')}\nDomain: {e.get('domain')}\n"

    prompt = """You are an advanced intelligence ontology engine.

Your task is to analyze the following geopolitical/strategic events and discover hidden connections, deeper impacts, and strategic relationships between the entities involved.

First provide a very brief 'reasoning' paragraph (max 3 sentences) explaining the overarching theme or hidden connection tying these events together.

Then, return a structured graph representation in JSON.

The FULL response must be ONLY valid JSON matching this structure exactly:

{
  "reasoning": "Your analytical paragraph here...",
  "graph": {
    "nodes": [
      {"id": "Entity Name", "type": "country/organization/person/technology/resource", "domain": "domain"}
    ],
    "edges": [
      {"source": "Entity1", "relation": "influences/controls/requires/conflicts_with", "target": "Entity2"}
    ]
  }
}

Do NOT wrap the JSON in markdown blocks (no ```json). Output raw JSON.
"""

    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt + "\n\nEvents Context:\n" + context_text}]
        }]
    }

    try:
        response = requests.post(gemini_url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        res_data = response.json()
        
        # Parse Gemini response
        text = res_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        if not text:
            return {"error": "Empty response from Gemini"}
            
        print(f"[Ontology] Raw Gemini reasoning response ({len(text)} chars)")
        
        # Clean markdown if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].strip()
            
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            text = match.group(0)
            
        data = json.loads(text)
        
        return {
            "success": True,
            "reasoning": data.get("reasoning", "No reasoning provided."),
            "graph": data.get("graph", {"nodes": [], "edges": []})
        }

    except Exception as e:
        print(f"[Ontology] Reasoning Error: {e}")
        return {"error": str(e)}
