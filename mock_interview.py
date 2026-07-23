import ollama
from jd_parser import parse_jd

def generate_question(parsed_jd, asked_so_far):
    prompt = f"""You are a hiring manager interviewing a candidate for this role:
Title: {parsed_jd['title']}
Must-have skills: {', '.join(parsed_jd['must_have_skills'])}
Domain: {parsed_jd['domain']}

Questions already asked: {asked_so_far if asked_so_far else 'None yet'}

Ask ONE new, specific interview question testing one of the must-have skills above.
Do not repeat a topic already asked. Return ONLY the question text, nothing else.
"""
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()


def judge_answer(question, answer):
    prompt = f"""You are a hiring manager judging a candidate's interview answer.

Question: {question}
Candidate's answer: {answer}

Give brief, direct feedback: what was strong, what was missing, and one suggestion
to make the answer sharper. Keep it to 3-4 sentences total.
"""
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()


def run_interview(jd_text, num_questions=3):
    parsed_jd = parse_jd(jd_text)
    print(f"\n--- Mock Interview for: {parsed_jd['title']} ---\n")

    asked_so_far = []
    for i in range(num_questions):
        question = generate_question(parsed_jd, asked_so_far)
        asked_so_far.append(question)

        print(f"Q{i+1}: {question}\n")
        answer = input("Your answer: ")

        feedback = judge_answer(question, answer)
        print(f"\nFeedback: {feedback}\n")
        print("-" * 60)


if __name__ == "__main__":
    sample_jd = """
    We are hiring a Senior Backend Engineer to join our fintech payments team.
    Requirements: 4+ years experience with Java, Spring Boot, and distributed systems.
    Must have hands-on experience with Kafka and SQL databases.
    Experience with AWS (Lambda, ECS) is required.
    Nice to have: exposure to Kubernetes, Docker, and observability tools like Grafana.
    This is a remote-friendly role.
    """
    run_interview(sample_jd, num_questions=3)