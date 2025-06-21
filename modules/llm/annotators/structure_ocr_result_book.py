# -*- coding: utf-8 -*-
"""
Created on Mon May 12 17:51:57 2025

@author: m.lotfi
"""

from ollama import Client
import json
import sys
import torch

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

model = "gemma3"

prompt = f"""
You are an expert in Arabic book structure analysis and formatting.

Your task is to extract and serialize the structural components of the following Arabic book text. These components include:

1. **Header** – appears at the top of the page and typically includes the book or chapter title.
2. **Footer** – appears at the bottom of the page and may contain the page number or publication info.
3. **Sections** – major content divisions, often introduced with words like: "مقدمة", "المبحث الأول", "الخاتمة", etc.
4. **Subsections** – nested under sections, often introduced with phrases like: "الأسلوب الأول", "الخطأ الثاني", etc.
5. **Paragraphs** – meaningful blocks of continuous content.

**Instructions**:
- Serialize the sections and subsections using numeric keys (e.g., section 1, 2; subsection 1.1, 1.2, etc.).
- Use the text's natural cues (e.g., "المبحث الأول", "الأسلوب الثاني", etc.) for identifying structure.
- Preserve and return Arabic text exactly as-is.
- Include a header and footer if they are repeated or positioned consistently.

**Return the output in JSON format** as follows:

{{
  "header": "text or null",
  "footer": "text or null",
  "sections": [
    {{
      "index": 1,
      "title": "Section title in Arabic",
      "paragraphs": ["...", "..."],
      "subsections": [
        {{
          "index": "1.1",
          "title": "Subsection title in Arabic",
          "paragraphs": ["...", "..."]
        }}
      ]
    }}
  ]
}}

Here is the Arabic book text:
\"\"\"{text}\"\"\"
"""

def book_structure_ollama(model: str, prompt: str):
    payload = {
            "model"     : model,
            "prompt"    : prompt,
            "stream"    : False,    # ⚠️ Set True if you want streaming        
            "options"   : {
                "temperature": 0.2
            }
        }
        
    if "gemma" not in model:
        payload["format"] = 'json'   # ⚠️ ensure structured JSON output            
    
    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result['response']
    else:
        raise Exception(f"Ollama API error: {response.status_code}, {response.text}")

# Example usage
if __name__ == "__main__":
    model = "gemma3"
    file_path = "./txt/1ـ 211.0 (267) علوم القرآن/00031ـ كتب غريب القرآن الكريم --- حسين بن محمد نصار.PDF/الكتاب.txt"
    text = pages[1]
    prompt = f"""
    You are an expert in Arabic book structure analysis and formatting.

    Your task is to extract and serialize the structural components of the following Arabic book text. These components include:

    1. **Header** – appears at the top of the page and typically includes the book or chapter title.
    2. **Footer** – appears at the bottom of the page and may contain the page number or publication info.
    3. **Sections** – major content divisions, often introduced with words like: "مقدمة", "المبحث الأول", "الخاتمة", etc.
    4. **Subsections** – nested under sections, often introduced with phrases like: "الأسلوب الأول", "الخطأ الثاني", etc.
    5. **Paragraphs** – meaningful blocks of continuous content.

    **Instructions**:
    - Serialize the sections and subsections using numeric keys (e.g., section 1, 2; subsection 1.1, 1.2, etc.).
    - Use the text's natural cues (e.g., "المبحث الأول", "الأسلوب الثاني", etc.) for identifying structure.
    - Preserve and return Arabic text exactly as-is.
    - Include a header and footer if they are repeated or positioned consistently.

    **Return the output in JSON format** as follows:

    {{
      "header": "text or null",
      "footer": "text or null",
      "sections": [
        {{
          "index": 1,
          "title": "Section title in Arabic",
          "paragraphs": ["...", "..."],
          "subsections": [
            {{
              "index": "1.1",
              "title": "Subsection title in Arabic",
              "paragraphs": ["...", "..."]
            }}
          ]
        }}
      ]
    }}

    Here is the Arabic book text:
    \"\"\"{text}\"\"\"
    """
    prompt = "Explain quantum physics in simple terms."
    response = book_structure_ollama(model, prompt)
    print("Ollama says:", response)
