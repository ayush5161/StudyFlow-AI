import json
from openai import OpenAI
import apikey


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=apikey.key
)

MODEL = "qwen/qwen3-vl-235b-a22b-thinking"


def generate_schedule(extracted_data, study_hours):

    prompt = f"""You are an intelligent exam preparation planner.

Input contains:
1. Subjects
2. Exam dates
3. Topics with preparation status
4. Hours available per day

Your task is to generate a realistic day-by-day study schedule.

Rules:

1. Prioritize subjects with the nearest exam date.
2. Topics marked "not started" should receive the most study time.
3. Topics marked "partially completed" should receive moderate time.
4. Topics marked "completed" should only receive revision if extra time exists.
5. Never schedule a topic after its exam date.
6. Do not exceed the available hours for that day.
7. Prefer study blocks of 1 or 2 hours.
8. Spread topics across multiple days if needed.

Return JSON only in this format:

{
 "schedule":{
   "YYYY-MM-DD":[
      {"duration":"2h","topic":"Subject - Topic"},
      {"duration":"1h","topic":"Subject - Topic"}
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