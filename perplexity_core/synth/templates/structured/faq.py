# FAQ structured content template
FAQ_SYSTEM_PROMPT = """You are a meticulous research assistant. Synthesize the provided web extracts into a
structured FAQ with explicit citations. Only use retrieved context; if missing, say so.
Return STRICT JSON matching the provided JSON Schema. No markdown, no prose."""

FAQ_USER_PROMPT = """Schema:
{{
  "type": "object",
  "required": ["type", "version", "items"],
  "properties": {{
    "type": {{"type": "string", "const": "faq"}},
    "version": {{"type": "string", "const": "1.0"}},
    "items": {{
      "type": "array",
      "items": {{
        "type": "object",
        "required": ["q", "a_md"],
        "properties": {{
          "q": {{"type": "string"}},
          "a_md": {{"type": "string"}}
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
- Create 5-10 Q/A pairs
- Questions should be user-facing and relevant
- Answers should be concise but comprehensive
- Use markdown in answers when helpful
- Cite sources by index like [1] when referencing specific content
- Only use information from the provided documents
- Output strict JSON only"""