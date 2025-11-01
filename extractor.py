import re
import json
import os

OPENAI_ENABLED = False
try:
    from openai import OpenAI
    OPENAI_ENABLED = bool(os.getenv("OPENAI_API_KEY"))
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception:
    OPENAI_ENABLED = False

PROMPT_TEMPLATE = """
You are a JSON extractor. Extract these fields from the text: accountNumber, period, avgBalance, status.
Return a JSON object only. If value not found, return null for that field.
Text:
\"\"\"{text}\"\"\"
"""

def llm_extract(text: str):
    
    if not OPENAI_ENABLED:
        return None
    messages = [
        {"role": "system", "content": "You extract structured fields from document text."},
        {"role": "user", "content": PROMPT_TEMPLATE.format(text=text)}
    ]
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages, max_tokens=300)
        content = resp.choices[0].message["content"]
        return json.loads(content)
    except Exception:
        return None

def regex_extract(text: str):
    out = {"accountNumber": None, "period": None, "avgBalance": None, "status": None}

    m = re.search(r"(?:Account(?: No(?:\.|)| Number|#)[:\s]*)([0-9\-\s]{6,20})", text, re.IGNORECASE)
    if not m:
        m = re.search(r"\b([0-9]{6,20})\b", text)
    if m:
        out["accountNumber"] = re.sub(r"[\s\-]", "", m.group(1))

   
    m = re.search(r"([A-Za-z]{3,9}\s*(?:–|-|to)\s*[A-Za-z]{3,9}\s*\d{4})", text)
    if not m:
        m = re.search(r"(\d{1,2}/\d{4}\s*(?:-|to|–)\s*\d{1,2}/\d{4})", text)
    if m:
        out["period"] = m.group(1)

    m = re.search(r"(?:avg(?:\.|) ?balance|average balance|avg balance)[:\s]*\$?([\d,]+\.\d{2})", text, re.IGNORECASE)
    if not m:
        m = re.search(r"Average\s+Balance[:\s]*\$?([\d,\,]+(?:\.\d{2})?)", text, re.IGNORECASE)
    if m:
        try:
            out["avgBalance"] = float(m.group(1).replace(",", ""))
        except Exception:
            out["avgBalance"] = None

   
    m = re.search(r"\b(status|verification)[:\s]*(verified|unverified|pending|closed|active|inactive)\b", text, re.IGNORECASE)
    if m:
        out["status"] = m.group(2).lower()
    else:
        if re.search(r"\bverified\b", text, re.IGNORECASE):
            out["status"] = "verified"

    return out

def extract_fields(text: str):
    llm_result = None
    if OPENAI_ENABLED:
        llm_result = llm_extract(text)
    if llm_result:
        meta = {"source": "llm", "confidence": None}
        return llm_result, meta

    res = regex_extract(text)
   
    non_null = sum(1 for v in res.values() if v is not None)
    confidence = round(non_null / len(res), 2)
    meta = {"source": "regex", "confidence": confidence}
    return res, meta