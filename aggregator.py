from collections import Counter
from match_agent import match_jd


def analyze_job_search(jd_list, user_id):
    """
    Takes a list of JD texts, matches each against the user's resume,
    and finds the single skill gap with the highest leverage across all JDs.
    """
    results = []
    all_gaps = []

    for i, jd_text in enumerate(jd_list):
        match_result = match_jd(jd_text, user_id=user_id)
        results.append({
            "jd_index": i,
            "overall_score": match_result["overall_score"],
            "gaps": match_result["gaps"],
        })
        all_gaps.extend(match_result["gaps"])

    gap_counts = Counter(all_gaps)

    if not gap_counts:
        return {
            "per_jd_results": results,
            "top_leverage_skill": None,
            "message": "No common gaps found — you're a strong match across all these roles!",
        }

    top_skill, count = gap_counts.most_common(1)[0]

    blocked_jd_indexes = [
        r["jd_index"] for r in results if top_skill in r["gaps"]
    ]

    return {
        "per_jd_results": results,
        "top_leverage_skill": top_skill,
        "blocks_jd_count": count,
        "blocked_jd_indexes": blocked_jd_indexes,
        "message": f"Learning '{top_skill}' would improve your fit on {count} out of {len(jd_list)} roles.",
    }


if __name__ == "__main__":
    sample_jds = [
        """Senior Backend Engineer, fintech. Requires Java, Spring Boot, Kafka, Kubernetes, Terraform.""",
        """Backend Engineer, e-commerce. Requires Python, Django, PostgreSQL, Kubernetes, Docker.""",
        """Platform Engineer. Requires Go, Kubernetes, Terraform, AWS, Prometheus.""",
    ]

    result = analyze_job_search(sample_jds, user_id="test_user_1")

    print(f"\nTop leverage skill: {result['top_leverage_skill']}")
    print(f"{result['message']}\n")
    for r in result["per_jd_results"]:
        print(f"JD {r['jd_index']}: score={r['overall_score']}, gaps={r['gaps']}")