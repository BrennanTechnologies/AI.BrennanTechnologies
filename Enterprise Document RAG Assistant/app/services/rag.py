# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from __future__ import annotations

from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType, VectorizedQuery
from openai import AzureOpenAI

from app.config import Settings
from app.models import AskResponse, SourceCitation

UNKNOWN_RESPONSE = "I don't know based on the documents."


def _build_prompt(question: str, citations: list[SourceCitation]) -> str:
    context_lines: list[str] = []
    for idx, item in enumerate(citations, start=1):
        context_lines.append(f"[{idx}] {item.filename} ({item.chunk_id}): {item.excerpt}")
    context = "\n".join(context_lines)

    return (
        "You are an enterprise assistant that can only answer from the provided context.\n"
        f"If the answer is not present, reply exactly: {UNKNOWN_RESPONSE}\n"
        "Always include citation markers like [1], [2] in the answer when you make claims.\n\n"
        f"Question: {question}\n\n"
        f"Context:\n{context}"
    )


def ask_question(
    question: str,
    search_client: SearchClient,
    openai_client: AzureOpenAI,
    settings: Settings,
) -> AskResponse:
    embedding = openai_client.embeddings.create(
        model=settings.azure_openai_embedding_deployment,
        input=[question],
    ).data[0].embedding

    vector_query = VectorizedQuery(
        vector=embedding,
        fields="content_vector",
        k_nearest_neighbors=settings.top_k,
    )

    results = search_client.search(
        search_text=question,
        vector_queries=[vector_query],
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name="default-semantic",
        top=settings.top_k,
        select=["id", "filename", "chunk_id", "content"],
    )

    citations: list[SourceCitation] = []
    for result in results:
        score = float(result.get("@search.score", 0.0))
        citations.append(
            SourceCitation(
                source_id=result["id"],
                filename=result.get("filename", "unknown"),
                chunk_id=result.get("chunk_id", "unknown"),
                score=score,
                excerpt=result.get("content", "")[:420],
            )
        )

    strong_results = [c for c in citations if c.score >= settings.similarity_threshold]
    if not strong_results:
        return AskResponse(answer=UNKNOWN_RESPONSE, citations=[])

    prompt = _build_prompt(question, strong_results)
    completion = openai_client.chat.completions.create(
        model=settings.azure_openai_chat_deployment,
        messages=[
            {
                "role": "system",
                "content": "Answer using only supplied context. If not found, use fallback sentence exactly.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )

    answer = completion.choices[0].message.content or UNKNOWN_RESPONSE
    if UNKNOWN_RESPONSE.lower() in answer.lower():
        answer = UNKNOWN_RESPONSE
    return AskResponse(answer=answer, citations=strong_results)
