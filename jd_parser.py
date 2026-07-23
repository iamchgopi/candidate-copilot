import os
import json
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def call_gemini_with_retry(model, contents, max_retries=3):
    """Retries Gemini calls on temporary server overload (503 errors)."""
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(model=model, contents=contents)
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"Gemini busy, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise


def parse_jd(jd_text):
    prompt = f"""You are a job description parser. Read the job description below and extract structured information.

Return ONLY valid JSON, no other text, in exactly this format:
{{
  "title": "...",
  "seniority": "...",
  "min_years_experience": 0,
  "must_have_skills": ["...", "..."],
  "nice_to_have_skills": ["...", "..."],
  "domain": "...",
  "remote_ok": true
}}

Job Description:
{jd_text}
"""
    response = call_gemini_with_retry(model="gemini-3.5-flash-lite", contents=prompt)
    raw_output = response.text

    start = raw_output.find("{")
    end = raw_output.rfind("}") + 1
    json_str = raw_output[start:end]

    return json.loads(json_str)


if __name__ == "__main__":
    sample_jd = """
    We are hiring a Senior Backend Engineer to join our fintech payments team.
    Requirements: 4+ years experience with Java, Spring Boot, and distributed systems.
    Must have hands-on experience with Kafka and SQL databases.
    Experience with AWS (Lambda, ECS) is required.
    Nice to have: exposure to Kubernetes, Docker, and observability tools like Grafana.
    This is a remote-friendly role.
    """
    result = parse_jd(sample_jd)
    print(json.dumps(result, indent=2))