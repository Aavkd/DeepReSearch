# Mind Map structured content template
MIND_MAP_SYSTEM_PROMPT = """You are a meticulous research assistant. Synthesize the provided web extracts into a
structured mind map with explicit citations. Only use retrieved context; if missing, say so.
Return STRICT JSON matching the provided JSON Schema. No markdown, no prose."""

MIND_MAP_USER_PROMPT = """Schema:
{{
  "type": "object",
  "required": ["type", "version", "nodes"],
  "properties": {{
    "type": {{"type": "string", "const": "mind_map"}},
    "version": {{"type": "string", "const": "1.0"}},
    "nodes": {{
      "type": "array",
      "items": {{
        "type": "object",
        "required": ["id", "label", "children"],
        "properties": {{
          "id": {{"type": "string"}},
          "label": {{"type": "string"}},
          "children": {{
            "type": "array",
            "items": {{
              "$ref": "#"
            }}
          }}
        }}
      }}
    }}
  }}
}}

User query:
"{query}"

Documents (each has url, title, excerpt):
{docs_json}

Instructions:
- Create a hierarchical mind map structure with ≤ 30 nodes
- Prioritize breadth over depth
- Children arrays may be empty for leaf nodes
- Only use information from the provided documents
- Output strict JSON only"""