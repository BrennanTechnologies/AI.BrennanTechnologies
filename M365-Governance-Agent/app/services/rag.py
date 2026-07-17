# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

import re
from pathlib import Path

from app.config import Settings
from app.models import AskResponse, Citation

UNKNOWN = "I don't know based on the governance documents."


class KnowledgeDoc:
    def __init__(self, source: str, content: str):
        self.source = source
        self.content = content
        self.tokens = _tokenize(content)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_\-]{3,}", text.lower()))


def _excerpt(text: str, question: str) -> str:
    words = question.split()
    pivot = words[0] if words else ""
    idx = text.lower().find(pivot.lower()) if pivot else -1
    if idx < 0:
        return text[:220]
    start = max(0, idx - 90)
    end = min(len(text), idx + 130)
    return text[start:end]


def load_knowledge(settings: Settings) -> list[KnowledgeDoc]:
    base = Path(settings.knowledge_dir)
    docs: list[KnowledgeDoc] = []

    if not base.exists():
        return docs

    for file in sorted(base.glob("*.md")):
        content = file.read_text(encoding="utf-8", errors="ignore")
        docs.append(KnowledgeDoc(source=file.name, content=content))
    return docs


def answer_question(question: str, settings: Settings) -> AskResponse:
    docs = load_knowledge(settings)
    if not docs:
        return AskResponse(answer=UNKNOWN, citations=[])

    q_tokens = _tokenize(question)
    scored: list[tuple[int, KnowledgeDoc]] = []

    for doc in docs:
        overlap = len(q_tokens.intersection(doc.tokens))
        if overlap > 0:
            scored.append((overlap, doc))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    top = scored[: settings.top_k]

    if not top or top[0][0] < settings.min_relevance_score:
        return AskResponse(answer=UNKNOWN, citations=[])

    citations: list[Citation] = []
    answer_bits: list[str] = []

    for idx, (score, doc) in enumerate(top, start=1):
        citations.append(Citation(source=doc.source, excerpt=_excerpt(doc.content, question), score=score))
        answer_bits.append(f"[{idx}] {doc.source} indicates relevant guidance.")

    answer = (
        "Based on the governance documents: "
        + " ".join(answer_bits)
        + " Verify role scope, approval requirements, and audit steps before execution."
    )

    return AskResponse(answer=answer, citations=citations)
