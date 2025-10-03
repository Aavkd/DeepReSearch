# Study Guide structured content template
STUDY_GUIDE_SYSTEM_PROMPT = """You are a meticulous research assistant. Synthesize the provided web extracts into a
structured study guide with explicit citations. Only use retrieved context; if missing, say so.
Return STRICT JSON matching the provided JSON Schema. No markdown, no prose."""

STUDY_GUIDE_USER_PROMPT = """Schema:
{{
  "type": "object",
  "required": ["type", "version", "modules"],
  "properties": {{
    "type": {{"type": "string", "const": "study_guide"}},
    "version": {{"type": "string", "const": "1.0"}},
    "modules": {{
      "type": "array",
      "items": {{
        "type": "object",
        "required": ["title", "notes_md", "quiz", "glossary"],
        "properties": {{
          "title": {{"type": "string"}},
          "notes_md": {{"type": "string"}},
          "quiz": {{
            "type": "array",
            "items": {{
              "type": "object",
              "required": ["question", "answer_md"],
              "properties": {{
                "question": {{"type": "string"}},
                "answer_md": {{"type": "string"}}
              }}
            }}
          }},
          "glossary": {{
            "type": "array",
            "items": {{
              "type": "object",
              "required": ["term", "def_md"],
              "properties": {{
                "term": {{"type": "string"}},
                "def_md": {{"type": "string"}}
              }}
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
- Create 2-3 modules with comprehensive notes
- Include 4-6 quiz questions per module
- Include 6-10 glossary terms per module
- Use markdown in notes when helpful
- Cite sources by index like [1] when referencing specific content
- Only use information from the provided documents
- Output strict JSON only"""