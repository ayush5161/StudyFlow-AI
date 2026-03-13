import os
import json
import base64
from openai import OpenAI
from pypdf import PdfReader
from docx import Document
import apikey


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=apikey.key
)

TEXT_MODEL = "qwen/qwen2.5-vl-72b-instruct"
VISION_MODEL = "qwen/qwen2.5-vl-72b-instruct"


# -------------------------
# PDF TEXT EXTRACTION
# -------------------------

def read_pdf(path):

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:
        t = page.extract_text()

        if t:
            text += t + "\n"

    return text


# -------------------------
# DOCX TEXT EXTRACTION
# -------------------------

def read_docx(path):

    doc = Document(path)

    text = []

    for p in doc.paragraphs:
        text.append(p.text)

    return "\n".join(text)


# -------------------------
# IMAGE TO BASE64
# -------------------------

def image_to_base64(path):

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# -------------------------
# LLM PROCESSOR (TEXT)
# -------------------------

def process_text(text):

    text = text[:8000]  # prevent huge token usage

    response = client.chat.completions.create(

        model=TEXT_MODEL,

        temperature=0,

        max_tokens=1200,

        messages=[
            {
                "role": "system",
                "content": """
You extract structured academic information from documents.

Return JSON ONLY.

Format:

{
 "subjects":[
   {
     "subject":"subject name",
     "exam_date":"YYYY-MM-DD or null",
     "topics":[
       "topic1",
       "topic2"
     ]
   }
 ]
}

Rules:
- Combine syllabus topics under the correct subject
- Extract exam dates from datesheet documents
- If no exam date exists set null
- Remove duplicates"""
            },

            {
                "role": "user",
                "content": text
            }
        ],

        
    )

    content = response.choices[0].message.content

    start = content.find("{")
    end = content.rfind("}") + 1

    return json.loads(content[start:end])


# -------------------------
# LLM PROCESSOR (IMAGE)
# -------------------------

def process_image(path):

    img_b64 = image_to_base64(path)

    response = client.chat.completions.create(

        model=VISION_MODEL,

        temperature=0,

        max_tokens=800,

        messages=[
            {
                "role": "system",
                "content": """
Extract the exam timetable.

Return JSON only.

Format:

{
 "datesheet":{
   "01-01-2026":"maths",
   "02-01-2026":"physics"
 }
}
"""
            },

            {
                "role": "user",
                "content":[
                    {
                        "type":"text",
                        "text":"Extract exam timetable"
                    },
                    {
                        "type":"image_url",
                        "image_url":{
                            "url":f"data:image/jpeg;base64,{img_b64}"
                        }
                    }
                ]
            }
        ],

        
    )

    content = response.choices[0].message.content

    start = content.find("{")
    end = content.rfind("}") + 1

    return json.loads(content[start:end])


# -------------------------
# MAIN EXTRACT FUNCTION
# -------------------------

def extract(file_path):

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":

        text = read_pdf(file_path)

        return process_text(text)

    elif ext == ".docx":

        text = read_docx(file_path)

        return process_text(text)

    elif ext in [".jpg", ".jpeg", ".png"]:

        return process_image(file_path)

    else:

        raise ValueError("Unsupported file type")