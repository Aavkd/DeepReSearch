# Timeline structured content template
TIMELINE_SYSTEM_PROMPT = """You are a meticulous research assistant. Synthesize the provided web extracts into a
structured timeline with explicit citations. Only use retrieved context; if missing, say so.
Return STRICT JSON matching the provided JSON Schema. No markdown, no prose."""

TIMELINE_USER_PROMPT = """Schema:
{{
  "type": "object",
  "required": ["type", "version", "events"],
  "properties": {{
    "type": {{"type": "string", "const": "timeline"}},
    "version": {{"type": "string", "const": "1.0"}},
    "events": {{
      "type": "array",
      "items": {{
        "type": "object",
        "required": ["date", "title", "summary_md", "source_urls"],
        "properties": {{
          "date": {{"type": "string", "format": "date"}},
          "title": {{"type": "string"}},
          "summary_md": {{"type": "string"}},
          "source_urls": {{
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
- Include 6-12 chronological events
- Use ISO date format (YYYY-MM-DD)
- Each event should cite at least one source URL
- Use markdown in summaries when helpful
- Only use information from the provided documents
- Output strict JSON only"""