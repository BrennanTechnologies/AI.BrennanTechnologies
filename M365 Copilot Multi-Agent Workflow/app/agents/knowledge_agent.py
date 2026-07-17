# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from pathlib import Path


def answer_from_knowledge(knowledge_dir: str, user_input: str) -> dict:
    base = Path(knowledge_dir)
    if not base.exists():
        return {
            "answer": "I don't know based on the workflow knowledge.",
            "citations": [],
        }

    query_tokens = set(user_input.lower().split())
    best_file = None
    best_score = -1

    for file in sorted(base.glob("*.md")):
        content = file.read_text(encoding="utf-8", errors="ignore")
        score = len(query_tokens.intersection(set(content.lower().split())))
        if score > best_score:
            best_score = score
            best_file = (file.name, content)

    if not best_file or best_score <= 0:
        return {
            "answer": "I don't know based on the workflow knowledge.",
            "citations": [],
        }

    file_name, content = best_file
    excerpt = content[:240]
    return {
        "answer": "Based on M365 governance workflow guidance, follow approved process and least-privilege roles.",
        "citations": [{"source": file_name, "excerpt": excerpt, "score": best_score}],
    }
