# text_extractor.py
import os
import base64
import json
from pypdf import PdfReader
from docx import Document
from openai import OpenAI
import apikey  # your module containing `key = "..."`

# configure client for openrouter
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=apikey.key)

# Choose your preferred qwen model here
MODEL = "qwen/qwen2.5-72b-instruct"

def extract_pdf(path):
    text = []
    try:
        reader = PdfReader(path)
        for p in reader.pages:
            tx = p.extract_text()
            if tx:
                text.append(tx)
    except Exception as e:
        print("PDF extraction error:", e)
    return "\n".join(text)

def extract_docx(path):
    text = []
    try:
        doc = Document(path)
        for p in doc.paragraphs:
            if p.text:
                text.append(p.text)
    except Exception as e:
        print("DOCX extraction error:", e)
    return "\n".join(text)

def extract_image(path):
    # We send the image to the LLM as base64 and ask it to extract text (no OCR locally).
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    # Ask the LLM directly to extract visible text from the image
    prompt = (
        "Extract readable text from the attached image. Return plain text only."
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0.0,
            messages=[
                {"role": "user", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                    ],
                },
            ],
        )
        return resp.choices[0].message.content
    except Exception as e:
        print("Image LLM error:", e)
        return ""

def extract(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_pdf(path)
    if ext == ".docx":
        return extract_docx(path)
    if ext in [".png", ".jpg", ".jpeg"]:
        return extract_image(path)
    # fallback read as text
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def organize_with_llm(text_list, today_date=None):
    """
    Merge syllabus texts and datesheet texts into a final normalized JSON.
    Output format:
    {
      "subjects":[
         {"subject":"name","exam_date":"YYYY-MM-DD","topics":[...]}
      ],
      "study_days":[{"date":"YYYY-MM-DD","hours":null}, ...]
    }
    """
    combined = "\n\n---DOCUMENT---\n\n".join(text_list)
    today_date = today_date or "2026-01-01"  # default, can be overridden by caller
    prompt = f"""
You are given raw extracted text from syllabus files and datesheet/exam schedule files.
Task:
1) Detect subjects with an associated syllabus (group topics into 4-8 study items).
2) Detect exam dates for subjects in YYYY-MM-DD format.
3) Match dates to subjects (allow fuzzy matching of names). 
4) Ignore any exam that does not have a corresponding syllabus in the uploaded files.
5) Produce study_days: list of every date from {today_date} through the latest exam date you found (inclusive).
6) Return JSON only in this exact structure:

{{ 
 "subjects":[
   {{
     "subject":"<name>",
     "exam_date":"YYYY-MM-DD or null",
     "topics":[ "topic1", "topic2", "topic3" ]
   }}
 ],
 "study_days":[
   {{ "date":"YYYY-MM-DD", "hours": null }}
 ]
}}

Now analyze the following combined text and produce the JSON only (no explanation):

TEXT:
{combined}
"""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=16000
        )
        out = resp.choices[0].message.content
        # Sometimes model returns code block or extra text — attempt to find first '{'
        first_brace = out.find("{")
        if first_brace > 0:
            out = out[first_brace:]
        return json.loads(out)
    except Exception as e:
        print("organize_with_llm error:", e)
        # Fallback: return empty well-formed structure
        return {"subjects": [], "study_days": []}