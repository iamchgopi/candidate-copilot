import ollama
import json

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
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}],
    )
    raw_output = response["message"]["content"]

    # Try to isolate JSON in case the model adds extra text
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