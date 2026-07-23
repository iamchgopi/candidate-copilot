import ollama
import json
import chromadb
from sentence_transformers import SentenceTransformer
from jd_parser import parse_jd

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="resume")


def retrieve_evidence(query, n_results=3):
    """Search your resume for the most relevant bullets to a given skill/requirement."""
    query_embedding = embed_model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
    return results["documents"][0]


def match_jd(jd_text):
    parsed_jd = parse_jd(jd_text)

  # Retrieve evidence separately for EACH must-have skill, so none get crowded out
    all_evidence = set()
    for skill in parsed_jd["must_have_skills"] + [parsed_jd["domain"]]:
        for e in retrieve_evidence(skill, n_results=4):
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
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    raw = response["message"]["content"]
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
    result = match_jd(sample_jd)
    print(json.dumps(result, indent=2))