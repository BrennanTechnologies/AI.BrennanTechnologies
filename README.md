
# AI.BrennanTechnologies

AI Solutions and Agents by Brennan Technologies, LLC.

This monorepo contains two independent projects for building and observing AI systems.


Author:  Chris Brennan

Company: Brennan Technologies, LLC

Email:   chris@brennantechnologies.com

Web:     https://www.brennantechnologies.com
---

## Projects

### [AI-Agents-BrennanTechnologies](./AI-Agents-BrennanTechnologies/)

A modular Python framework for building agentic AI systems.

**Key capabilities:**
- Specialized agents: Base, Research, Code Review, Tool-Calling, and Multi-Agent Orchestrator
- Retrieval-Augmented Generation (RAG) pipeline with document processing and vector search
- Provider-agnostic LLM integration (OpenAI, Anthropic, local/offline)
- Tooling layer: web search, code execution, key-value memory, vector memory
- LangGraph-style workflow orchestration with runnable examples

**Stack:** Python · LangGraph-style workflows · DuckDuckGo search · OpenAI / Anthropic / local LLM

**Quick start:**
```powershell
cd AI-Agents-BrennanTechnologies
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python examples/run_base_agent.py
```

#### High-Level Architecture

```mermaid
flowchart LR
	U[User / Application] --> O[Multi-Agent Orchestrator]
	O --> A1[Base Agent]
	O --> A2[Research Agent]
	O --> A3[Code Review Agent]
	O --> A4[Tool-Calling Agent]

	A2 --> T1[Web Search Tool]
	A4 --> T2[Code Executor Tool]
	A4 --> T3[Memory Store]
	A4 --> T4[Vector Memory]

	O --> W[Workflow Graph]
	W --> R[RAG Pipeline]
	R --> DP[Document Processor]
	R --> VS[Vector Store]
	R --> RT[Retriever]

	A1 --> LLMF[LLM Factory]
	A2 --> LLMF
	A3 --> LLMF
	A4 --> LLMF
	R --> LLMF

	LLMF --> P1[OpenAI Wrapper]
	LLMF --> P2[Anthropic Wrapper]
	LLMF --> P3[Local Wrapper]
```

#### Agent Flow

```mermaid
flowchart TD
	S[Incoming Task] --> D{Task Classifier}
	D -->|General task| B[Base Agent]
	D -->|Research/latest| R[Research Agent]
	D -->|Code review| C[Code Review Agent]
	D -->|Tool action| T[Tool-Calling Agent]
	B --> OUT[Response]
	R --> OUT
	C --> OUT
	T --> OUT
```

#### RAG Pipeline

```mermaid
flowchart LR
	D[Raw Documents] --> P[Document Processor]
	P --> C[Chunked Text]
	C --> V[Vector Store]
	Q[User Query] --> R[Retriever]
	V --> R
	R --> K[Top-k Context]
	K --> G[LLM Generation]
	Q --> G
	G --> A[Grounded Answer]
```

#### Multi-Agent Collaboration

```mermaid
sequenceDiagram
	participant User
	participant Orch as Orchestrator
	participant Res as Research Agent
	participant Tool as Tool-Calling Agent
	participant RAG as RAG Pipeline
	participant LLM as LLM Layer

	User->>Orch: "Research modern RAG patterns"
	Orch->>Res: route(task)
	Res->>Tool: web_search(query)
	Tool-->>Res: search results
	Res->>LLM: summarize findings
	LLM-->>Res: research draft
	Orch->>RAG: enrich with indexed knowledge
	RAG->>LLM: grounded prompt + context
	LLM-->>RAG: grounded answer
	RAG-->>Orch: enriched output
	Orch-->>User: final combined response
```

---

### [LLM-Observability-Dashboard](./LLM-Observability-Dashboard/)

A full-stack observability dashboard for tracking LLM request health, latency, token usage, cost, and error rates.

**Key capabilities:**
- Ingest LLM events via REST API
- KPI cards: total requests, p95 latency, error rate, token usage, estimated cost
- Trace table with model/status filtering
- Latency and error-rate time-series charts
- Seed data for instant local demo

**Stack:** FastAPI · SQLAlchemy · SQLite · React · TypeScript · Vite · Recharts · Docker Compose

**Quick start (Docker):**
```bash
cd LLM-Observability-Dashboard
docker compose up --build
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

**Quick start (local):**
```bash
cd LLM-Observability-Dashboard/backend
python -m venv .venv && source .venv/Scripts/activate
pip install -e .
uvicorn app.main:app --reload --port 8000

# In another terminal:
cd LLM-Observability-Dashboard/frontend
npm install && npm run dev

# Seed sample data:
curl -X POST http://localhost:8000/api/seed
```

#### System Architecture

```mermaid
flowchart LR
	Client[Browser / React + Vite] -->|REST| API[FastAPI Backend]
	API -->|SQLAlchemy ORM| DB[(SQLite)]
	API -->|POST /api/events| Ingest[Event Ingestion]
	API -->|GET /api/traces| Traces[Trace Query]
	API -->|GET /api/metrics/summary| Summary[KPI Summary]
	API -->|GET /api/metrics/timeseries| TS[Time Series]
	API -->|POST /api/seed| Seed[Seed Data]
```

#### Request Lifecycle

```mermaid
sequenceDiagram
	participant App as LLM Application
	participant API as FastAPI Backend
	participant DB as SQLite
	participant UI as React Dashboard

	App->>API: POST /api/events (LLM event payload)
	API->>DB: INSERT event record
	DB-->>API: OK
	API-->>App: 201 Created

	UI->>API: GET /api/metrics/summary
	API->>DB: aggregate query
	DB-->>API: KPI data
	API-->>UI: JSON summary

	UI->>API: GET /api/traces
	API->>DB: filtered trace query
	DB-->>API: trace rows
	API-->>UI: JSON trace list
```

---

## Repository Structure

```text
AI.BrennanTechnologies/
├── AI-Agents-BrennanTechnologies/   # Modular multi-agent & RAG framework (Python)
├── LLM-Observability-Dashboard/    # Full-stack LLM observability dashboard
│   ├── backend/                    # FastAPI + SQLAlchemy
│   └── frontend/                   # React + TypeScript + Vite
└── README.md
```
