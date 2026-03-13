import os
import base64
import json
from pypdf import PdfReader
from docx import Document
from openai import OpenAI
import apikey

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=apikey.key
)

MODEL = "qwen/qwen2.5-72b-instruct"


# -----------------------
# TEXT EXTRACTION
# -----------------------

def extract_pdf(path):

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text


def extract_docx(path):

    doc = Document(path)

    text = ""

    for p in doc.paragraphs:
        text += p.text + "\n"

    return text


def extract_image(path):

    with open(path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role":"user",
                "content":[
                    {
                        "type":"text",
                        "text":"Extract all readable text from this document."
                    },
                    {
                        "type":"image_url",
                        "image_url":{
                            "url":f"data:image/png;base64,{img}"
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content


# -----------------------
# ORGANIZE WITH LLM
# -----------------------

def organize_with_llm(all_text):

    combined = "\n\n".join(all_text)

    prompt = f"""
You are organizing exam data for a study planner.

You will receive:
• syllabus text
• exam datesheet text

Your job:

1. Detect subjects.
2. Extract syllabus topics.
3. Match exam dates to subjects.
4. Ignore exams whose syllabus was not uploaded.

Topics must be grouped (4-8 topics per subject).

Return JSON only:

{{
 "subjects":[
   {{
     "subject":"subject name",
     "exam_date":"YYYY-MM-DD",
     "topics":[
       "topic1",
       "topic2",
       "topic3"
     ]
   }}
 ]
}}

TEXT:

{combined}
"""

    response = client.chat.completions.create(

        model=MODEL,

        temperature=0,

        messages=[
            {"role":"user","content":prompt}
        ]

    )

    result = response.choices[0].message.content

    try:
        return json.loads(result)
    except:
        print("LLM OUTPUT:")
        print(result)
        raise Exception("LLM JSON parsing failed")


# -----------------------
# MAIN EXTRACT FUNCTION
# -----------------------

def extract(path):

    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return extract_pdf(path)

    elif ext == ".docx":
        return extract_docx(path)

    elif ext in [".png",".jpg",".jpeg"]:
        return extract_image(path)

    else:
        raise Exception("Unsupported file type")