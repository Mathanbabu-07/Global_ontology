from flask import Blueprint, request, jsonify
from config import config
from supabase import create_client
from services.scraper import scrape_url
from services.ai_pipeline import analyze_content

query_bp = Blueprint("query", __name__)


@query_bp.route("/query", methods=["POST"])
def query_handler():
    """
    Accept a user prompt from the AI Query Console.
    Fetch relevant sources, scrape them, analyze content, and return a response.
    """
    try:
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)

        # Determine domain from prompt keywords
        domain = detect_domain(prompt)

        # Fetch active sources, optionally filter by domain
        query = db.table("sources").select("*").eq("active", True)
        if domain:
            query = query.eq("domain", domain)
        sources = query.limit(5).execute()

        if not sources.data:
            # No sources found — use AI directly on the prompt
            response = analyze_content(prompt, domain or "general")
            return jsonify({
                "response": response.get("summary", "No sources available. Please add sources in the Source Registry."),
                "domain": domain,
                "sources_used": 0,
            }), 200

        # Scrape and analyze each source
        results = []
        for source in sources.data:
            try:
                content = scrape_url(source["url"])
                if content:
                    analysis = analyze_content(
                        f"CRITICAL INSTRUCTION: You must strictly answer the user's query using ONLY the provided content. If the content does not contain the answer, state that you cannot answer it based on the source. Do not hallucinate external knowledge.\n\nUser query: {prompt}\n\nContent from {source['url']}:\n{content[:3000]}",
                        source.get("domain", "general"),
                    )
                    results.append(analysis)

                    # Store scraped data
                    db.table("scraped_data").insert({
                        "source_id": source["id"],
                        "source_url": source["url"],
                        "domain": source.get("domain", "general"),
                        "summary": analysis.get("summary", ""),
                        "entities": analysis.get("entities", []),
                        "events": analysis.get("events", []),
                        "relationships": analysis.get("relationships", []),
                    }).execute()
            except Exception as e:
                print(f"[Query] Error processing {source['url']}: {e}")
                continue

        # Combine results into a response
        if results:
            combined_summary = "\n\n".join(
                [f"**{r.get('source_url', 'Source')}**: {r.get('summary', 'N/A')}" for r in results]
            )
            all_entities = []
            for r in results:
                all_entities.extend(r.get("entities", []))

            response_text = f"Based on {len(results)} source(s) analyzed:\n\n{combined_summary}"
            if all_entities:
                response_text += f"\n\n**Key Entities**: {', '.join(set(all_entities[:15]))}"
        else:
            response_text = "Could not extract intelligence from the available sources. Try adding more sources or refining your query."

        return jsonify({
            "response": response_text,
            "domain": domain,
            "sources_used": len(results),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def detect_domain(prompt):
    """Simple keyword-based domain detection from user prompt."""
    prompt_lower = prompt.lower()
    domain_keywords = {
        "geopolitics": ["geopolitical", "geopolitics", "foreign policy", "diplomacy", "international relations", "border", "sanctions"],
        "economics": ["economic", "economy", "gdp", "trade", "inflation", "fiscal", "monetary", "market"],
        "defense": ["defense", "defence", "military", "army", "navy", "weapons", "missile", "security"],
        "technology": ["technology", "tech", "ai", "artificial intelligence", "cyber", "digital", "software"],
        "climate": ["climate", "environment", "carbon", "emission", "weather", "global warming", "sustainability"],
        "society": ["society", "social", "population", "health", "education", "culture", "demographic"],
    }
    for domain, keywords in domain_keywords.items():
        if any(kw in prompt_lower for kw in keywords):
            return domain
    return None
