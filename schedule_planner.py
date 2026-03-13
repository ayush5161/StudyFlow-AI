import json
from openai import OpenAI
import apikey


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=apikey.key
)

MODEL = "qwen/qwen3-vl-235b-a22b-thinking"


def generate_schedule(extracted_data, study_hours):

    prompt = f"""You are an AI study planner.

Input contains:
- subjects
- exam dates
- topics
- user preparation status
- hours available per day

Rules:

1. Prioritize subjects with the nearest exam date
2. Topics marked "not started" should receive more time
3. Topics marked "partially completed" receive medium time
4. Topics marked "completed" should be skipped unless revision is possible
5. Do not exceed the available hours per day

Return JSON:

{
 "schedule":{
   "YYYY-MM-DD":[
      {"duration":"2h","topic":"Subject - Topic"}
   ]
 }
}"""

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