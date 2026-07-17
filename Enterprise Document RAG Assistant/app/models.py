# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    source_id: str = Field(description="Unique id of the retrieved chunk")
    filename: str = Field(description="Original document filename")
    chunk_id: str = Field(description="Chunk identifier within the document")
    score: float = Field(description="Retrieval relevance score")
    excerpt: str = Field(description="Short cited excerpt")


class AskRequest(BaseModel):
    question: str = Field(min_length=3)


class AskResponse(BaseModel):
    answer: str
    citations: list[SourceCitation]


class UploadResponse(BaseModel):
    filenames: list[str]
    indexed_chunks: int
