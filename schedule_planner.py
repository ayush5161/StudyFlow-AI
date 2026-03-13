import json
from openai import OpenAI
import apikey


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=apikey.key
)

MODEL = "qwen/qwen3-vl-235b-a22b-thinking"


def generate_schedule(extracted_data, study_hours):

    prompt = f"""
You are an AI study planner.

You receive:

1) Exam dates and subjects
2) Syllabus topics
3) Available study hours per day

Rules:
- Allocate topics before their exam date
- Split hours into study blocks
- Prefer 1hr or 2hr sessions
- Do not exceed the hours available that day
- Cover all topics

Return JSON only.

Exam data:
{json.dumps(extracted_data, indent=2)}

Study hours per day:
{json.dumps(study_hours, indent=2)}

Return JSON like:

{{
 "01-01-2026": {{
   "2hr":"Topic A",
   "2hr_2":"Topic B"
 }},
 "02-01-2026": {{
   "1hr":"Topic C"
 }}
}}
"""

    response = client.chat.completions.create(

        model=MODEL,

        temperature=0.3,

        max_tokens=2000,

        messages=[
            {
                "role":"system",
                "content":"You generate optimized study schedules."
            },
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    content = response.choices[0].message.content

    start = content.find("{")
    end = content.rfind("}") + 1

    return json.loads(content[start:end])