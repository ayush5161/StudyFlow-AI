# schedule_planner.py
import json
from openai import OpenAI
import apikey

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=apikey.key)
MODEL = "qwen/qwen2.5-72b-instruct"

def generate_schedule(topic_status_json):
    """
    Accepts the payload saved from the status page:
    {
      "subjects":[ {subject, exam_date, topics:[{topic, status}, ...]} ],
      "daily_hours": { "YYYY-MM-DD": number_of_hours, ...}
    }

    Returns schedule JSON:
    {
      "schedule": {
         "YYYY-MM-DD": [
            {"topic":"Subject - Topic","duration":"2hr"}
         ],
         ...
      }
    }
    """
    # If an LLM failure occurs, fallback to naive scheduling.
    prompt = f"""
You're a schedule generator. Input is a JSON with subjects (each with topics and statuses) and available hours per day.
Task: allocate topics into days between today and exam dates, respecting daily hours, prioritizing "not started" topics earlier.
Input JSON:
{json.dumps(topic_status_json, indent=2)}

Output JSON structure:

{{
 "schedule": {{
   "YYYY-MM-DD": [
      {{"topic":"Subject - Topic", "duration":"Xhr"}}
   ]
 }}
}}

Return JSON only.
"""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=16000
        )
        out = resp.choices[0].message.content
        # try to parse
        first = out.find("{")
        if first > 0:
            out = out[first:]
        return json.loads(out)
    except Exception as e:
        print("LLM schedule error:", e)
        # fallback: simple even distribution
        return simple_schedule(topic_status_json)

def simple_schedule(topic_status_json):
    import math, datetime
    subjects = topic_status_json.get("subjects", [])
    daily = topic_status_json.get("daily_hours", {})
    # collect days sorted
    days = sorted(daily.keys())
    schedule = {}
    topics_flat = []
    for s in subjects:
        for t in s.get("topics", []):
            # if topics stored as {"topic":..., "status":...}
            if isinstance(t, dict):
                name = t.get("topic")
            else:
                name = t
            topics_flat.append(f"{s.get('subject')} - {name}")
    if not days:
        return {"schedule": {}}
    idx = 0
    for d in days:
        schedule[d] = []
        # allocate 1 topic per day (naive)
        if idx < len(topics_flat):
            schedule[d].append({"topic": topics_flat[idx], "duration": "2hr"})
            idx += 1
    return {"schedule": schedule}