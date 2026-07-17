# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.models import AskRequest, AskResponse, UploadResponse
from app.services.indexer import index_file
from app.services.openai_client import create_openai_client
from app.services.rag import ask_question
from app.services.search_client import ensure_index, get_search_client

settings = get_settings()
app = FastAPI(title="Enterprise Document RAG Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


@app.on_event("startup")
def startup() -> None:
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    ensure_index(settings)


@app.get("/")
def root() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents/upload", response_model=UploadResponse)
async def upload_documents(files: list[UploadFile] = File(...)) -> UploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    openai_client = create_openai_client(settings)
    search_client = get_search_client(settings)

    saved_files: list[str] = []
    total_chunks = 0

    for file in files:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".pdf", ".md"}:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

        file_path = Path(settings.upload_dir) / Path(file.filename or "upload.bin").name
        content = await file.read()
        file_path.write_bytes(content)

        chunks = index_file(file_path, search_client, openai_client, settings)
        total_chunks += chunks
        saved_files.append(file_path.name)

    return UploadResponse(filenames=saved_files, indexed_chunks=total_chunks)


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    openai_client = create_openai_client(settings)
    search_client = get_search_client(settings)
    return ask_question(question, search_client, openai_client, settings)
