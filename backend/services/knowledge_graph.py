import json
import uuid
from typing import List, Dict, Any
from config import config
from supabase import create_client

def get_supabase_client():
    return create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)

class EntityNormalizationAgent:
    """
    Purpose: Clean and normalize extracted entities.
    Tasks:
    - Remove duplicates
    - Standardize entity names
    - Assign ontology types (Country, Organization, Person, Event, Technology, Policy, Concept, Region)
    """
    def __init__(self):
        self.allowed_types = ["Country", "Organization", "Person", "Event", "Technology", "Policy", "Concept", "Region"]
        
    def process(self, entities: List[Dict], domain: str) -> List[Dict]:
        normalized = {}
        
        for ent in entities:
            # Handle different input formats
            if isinstance(ent, dict):
                raw_name = ent.get("name") or ent.get("label", "")
                raw_type = ent.get("type", "Concept")
            else:
                raw_name = str(ent)
                raw_type = "Concept"
                
            if not raw_name:
                continue
                
            # Naive standardization (in a more complex setup, use LLM here to merge "US" and "USA")
            label = str(raw_name).strip().title()
            
            # Basic type mapping
            mapped_type = "Concept"
            for t in self.allowed_types:
                if t.lower() in str(raw_type).lower():
                    mapped_type = t
                    break
            
            # Remove duplicates by using lowercase label as dict key
            key = label.lower()
            if key not in normalized:
                normalized[key] = {
                    "id": label.replace(" ", "_"), # Basic ID generation
                    "label": label,
                    "type": mapped_type,
                    "domain": domain
                }
                
        return list(normalized.values())


class RelationshipExtractionAgent:
    """
    Purpose: Identify meaningful relationships between entities.
    Tasks:
    - Validate AI extracted relationships
    - Assign semantic relationship labels
    """
    def __init__(self):
        self.allowed_relations = [
            "alliance", "trade", "conflict", "influence", "participates_in", 
            "researches", "contributes_to", "supports", "regulates", "develops"
        ]
        
    def _map_relation(self, raw_relation: str) -> str:
        raw = str(raw_relation).lower()
        for rel in self.allowed_relations:
            if rel in raw:
                return rel
        # Default mapping logic
        if "invest" in raw or "export" in raw or "import" in raw:
            return "trade"
        if "sanction" in raw or "war" in raw:
            return "conflict"
        if "sign" in raw or "agree" in raw:
            return "alliance"
        return "influence" # fallback
        
    def process(self, relationships: List[Dict], valid_entity_ids: set) -> List[Dict]:
        validated = []
        for rel in relationships:
            source = rel.get("source", "").strip().title().replace(" ", "_")
            target = rel.get("target", "").strip().title().replace(" ", "_")
            raw_relation = rel.get("relation", "")
            
            # Validation: relationships must have valid source and target
            if source and target and source in valid_entity_ids and target in valid_entity_ids:
                mapped_relation = self._map_relation(raw_relation)
                # Ensure confidence >= 0.6 per optimization rules
                confidence = float(rel.get("confidence", 0.85))
                if confidence < 0.6:
                    continue
                    
                validated.append({
                    "source": source,
                    "target": target,
                    "relation": mapped_relation,
                    "confidence": confidence
                })
        return validated


class OntologyMappingAgent:
    """
    Purpose: Map entities and relationships into a global ontology structure.
    Tasks: Ensure consistent schema, categorize by domain.
    """
    def process(self, entities: List[Dict], relationships: List[Dict]) -> Dict:
        # Here we could enforce strict domain mappings based on entity type.
        # For our current scope, it simply passes through structurally validated data.
        return {
            "entities": entities,
            "relationships": relationships
        }


class GraphBuilderAgent:
    """
    Purpose: Construct the final knowledge graph structure.
    Tasks: Create nodes, Create edges, Ensure no duplicates, compatible with React Flow/Vis.
    """
    def process(self, mapped_data: Dict) -> Dict:
        nodes = []
        edges = []
        
        seen_nodes = set()
        for ent in mapped_data["entities"]:
            if ent["id"] not in seen_nodes:
                nodes.append({
                    "id": ent["id"],
                    "label": ent["label"],
                    "type": ent["type"]
                })
                seen_nodes.add(ent["id"])
                
        seen_edges = set()
        for rel in mapped_data["relationships"]:
            edge_key = f"{rel['source']}_{rel['relation']}_{rel['target']}"
            if edge_key not in seen_edges:
                edges.append({
                    "source": rel["source"],
                    "target": rel["target"],
                    "label": rel["relation"],
                    "confidence": rel["confidence"]
                })
                seen_edges.add(edge_key)
                
        return {
            "nodes": nodes,
            "edges": edges
        }


class GraphStorageAgent:
    """
    Purpose: Persist graph data in Supabase.
    Tables: Entities, Relationships.
    Tasks: Insert/update nodes, maintain relationships.
    """
    def __init__(self):
        self.db = get_supabase_client()
        
    def process(self, entities: List[Dict], relationships: List[Dict]):
        # Store Entities
        for ent in entities:
            # Upsert logic - in Supabase, we can use insert with upsert=True if we have unique constraints.
            # Here we do a manual check or rely on Supabase upsert.
            try:
                # Assuming table 'Entities' exists
                existing = self.db.table("Entities").select("id").eq("id", ent["id"]).execute()
                if not existing.data:
                    self.db.table("Entities").insert(ent).execute()
                else:
                    self.db.table("Entities").update(ent).eq("id", ent["id"]).execute()
            except Exception as e:
                print(f"[GraphStorageAgent] Error storing entity {ent.get('id')}: {e}")
                
        # Store Relationships
        for rel in relationships:
            try:
                rel_id = f"{rel['source']}_{rel['relation']}_{rel['target']}"
                existing = self.db.table("Relationships").select("id").eq("source", rel["source"]).eq("target", rel["target"]).eq("relation", rel["relation"]).execute()
                
                rel_data = {
                    "id": rel_id,
                    "source": rel["source"],
                    "target": rel["target"],
                    "relation": rel["relation"],
                    "confidence": rel["confidence"]
                }
                
                if not existing.data:
                    self.db.table("Relationships").insert(rel_data).execute()
                else:
                    # Graph Update Agent would handle merge/confidence update, but we do basic update here
                    self.db.table("Relationships").update(rel_data).eq("id", existing.data[0]["id"]).execute()
            except Exception as e:
                print(f"[GraphStorageAgent] Error storing relationship: {e}")


class GraphUpdateAgent:
    """
    Purpose: Maintain a continuously evolving intelligence graph.
    Tasks: Detect new entities, update relationships, merge duplicate nodes, update confidences.
    """
    def process(self, current_graph: Dict, new_entities: List[Dict], new_relationships: List[Dict]):
        # This agent would typically run a periodic background job or be invoked 
        # to calculate moving averages of confidences and merge nodes.
        # For pipeline simplicity, we'll let GraphStorageAgent handle the upserts for now.
        pass


def build_knowledge_graph(ai_extracted_data: Dict, domain: str = "geopolitics") -> Dict:
    """
    Pipeline Workflow:
    1. Receive structured entities and relationships from AI extraction layer
    2. Normalize entities
    3. Validate relationships
    4. Map ontology
    5. Build graph nodes and edges
    6. Store graph in Supabase
    7. Provide graph output for visualization layer
    """
    # Initialize agents
    normalizer = EntityNormalizationAgent()
    extractor = RelationshipExtractionAgent()
    mapper = OntologyMappingAgent()
    builder = GraphBuilderAgent()
    storage = GraphStorageAgent()
    updater = GraphUpdateAgent()
    
    # Extract raw lists
    raw_entities = ai_extracted_data.get("entities", [])
    raw_relationships = ai_extracted_data.get("relationships", [])
    
    # 2. Normalize entities
    normalized_entities = normalizer.process(raw_entities, domain)
    valid_entity_ids = {e["id"] for e in normalized_entities}
    
    # 3. Validate relationships
    validated_relationships = extractor.process(raw_relationships, valid_entity_ids)
    
    # 4. Map ontology
    mapped_data = mapper.process(normalized_entities, validated_relationships)
    
    # 6. Store graph in Supabase
    # We call storage here to persist the data to 'Entities' and 'Relationships' tables
    storage.process(mapped_data["entities"], mapped_data["relationships"])
    
    # 5/7. Build graph nodes and edges for output
    final_graph = builder.process(mapped_data)
    
    # Print optimization rules satisfaction
    print(f"[Knowledge Graph] Built graph with {len(final_graph['nodes'])} nodes and {len(final_graph['edges'])} edges.")
    
    return final_graph
