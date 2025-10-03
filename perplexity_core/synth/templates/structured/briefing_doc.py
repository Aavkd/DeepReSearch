# Briefing Document structured content template
BRIEFING_DOC_SYSTEM_PROMPT = """You are a meticulous research assistant. Synthesize the provided web extracts into a
structured briefing document with explicit citations. Only use retrieved context; if missing, say so.
Return STRICT JSON matching the provided JSON Schema. No markdown, no prose."""

BRIEFING_DOC_USER_PROMPT = """Schema:
{{
  "type": "object",
  "required": ["type", "version", "sections"],
  "properties": {{
    "type": {{"type": "string", "const": "briefing_doc"}},
    "version": {{"type": "string", "const": "1.0"}},
    "sections": {{
      "type": "array",
      "items": {{
        "type": "object",
        "required": ["heading"],
        "properties": {{
          "heading": {{"type": "string"}},
          "content_md": {{"type": "string"}},
          "items": {{
            "type": "array",
            "items": {{"type": "string"}}
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
- Include an Executive Summary section (≤ 150 words)
- Include Key Developments section with bullet items
- Include Risks & Open Questions section with bullet items
- Include Recommended Actions section with concrete actions
- Use markdown in content when helpful
- Cite sources by index like [1] when referencing specific content
- Only use information from the provided documents
- Output strict JSON only"""