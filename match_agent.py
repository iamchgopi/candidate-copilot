import json
import chromadb
from sentence_transformers import SentenceTransformer
from jd_parser import parse_jd, call_gemini_with_retry

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
db_client = chromadb.PersistentClient(path="./chroma_db")


def get_user_collection(user_id):
    return db_client.get_or_create_collection(name=f"resume_{user_id}")


def retrieve_evidence(collection, query, n_results=3):
    """Search a specific user's resume for the most relevant bullets to a given skill/requirement."""
    query_embedding = embed_model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
    return results["documents"][0]


def match_jd(jd_text, user_id):
    parsed_jd = parse_jd(jd_text)
    collection = get_user_collection(user_id)

    all_evidence = set()
    for skill in parsed_jd["must_have_skills"] + [parsed_jd["domain"]]:
        for e in retrieve_evidence(collection, skill, n_results=4):
            all_evidence.add(e)
    evidence_text = "\n".join(f"- {e}" for e in all_evidence)

    prompt = f"""You are scoring how well a candidate's resume matches a job description.

JOB REQUIREMENTS:
Title: {parsed_jd['title']}
Must-have skills: {', '.join(parsed_jd['must_have_skills'])}
Nice-to-have skills: {', '.join(parsed_jd['nice_to_have_skills'])}
Domain: {parsed_jd['domain']}
Min years experience: {parsed_jd['min_years_experience']}

CANDIDATE'S RELEVANT RESUME EVIDENCE (retrieved by relevance search):
{evidence_text}

Score the candidate on each dimension from 0-100, and give a ONE-LINE justification for each score
that references the specific evidence above. Also list any must-have skills NOT found in the evidence
as honest gaps.

Return ONLY valid JSON in exactly this format:
{{
  "skill_score": 0,
  "skill_justification": "...",
  "domain_score": 0,
  "domain_justification": "...",
  "experience_score": 0,
  "experience_justification": "...",
  "overall_score": 0,
  "gaps": ["...", "..."]
}}
"""
    response = call_gemini_with_retry(model="gemini-3.5-flash-lite", contents=prompt)
    raw = response.text
    start = raw.find("{")
    end = raw.rfind("}") + 1
    return json.loads(raw[start:end])


if __name__ == "__main__":
    sample_jd = """
    We are hiring a Senior Backend Engineer to join our fintech payments team.
    Requirements: 4+ years experience with Java, Spring Boot, and distributed systems.
    Must have hands-on experience with Kafka and SQL databases.
    Experience with AWS (Lambda, ECS) is required.
    Nice to have: exposure to Kubernetes, Docker, and observability tools like Grafana.
    This is a remote-friendly role.
    """
    result = match_jd(sample_jd, user_id="test_user_1")
    print(json.dumps(result, indent=2))