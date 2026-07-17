# Demo Script (5-7 minutes)

## 1) Setup (Presenter)

- Start app:

```powershell
uvicorn app.main:app --reload --port 8008
```

- Open browser at `http://localhost:8008`.

Narration:
"This assistant only answers from approved internal documents. It shows citations and refuses to hallucinate when evidence is missing."

## 2) Upload Documents

- Upload 1-2 markdown files and 1 PDF with known policies or product info.
- Click **Upload + Index**.

Expected:
- Status reports number of indexed chunks and filenames.

Narration:
"Each file is parsed, chunked, embedded in Azure OpenAI, and indexed in Azure AI Search."

## 3) Ask Grounded Question

Question example:
- "What is our incident escalation SLA?"

Expected:
- Answer includes citation markers like `[1]` and `[2]`.
- Citation list shows filename/chunk and excerpt.

Narration:
"The app runs hybrid retrieval, then answer generation constrained to retrieved context."

## 4) Trigger Unknown Behavior

Question example:
- "What is our Mars office parking policy?"

Expected:
- Exact response: `I don't know based on the documents.`

Narration:
"This is intentional guardrail behavior for enterprise trust and compliance."

## 5) Security Note

Narration:
"In production, this service uses managed identity from App Service to call Azure OpenAI and Azure AI Search without embedding keys in code."

## 6) Close

Narration:
"This pattern scales to policy copilots, operations assistants, and regulated knowledge workflows with auditable citations."
