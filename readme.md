# Minimal Agent System

**A vertical-slice demo of an Agentic RAG system built with LangGraph, FastAPI, and VectorDB.**


## Features

This project is a minimal demo with modern LLM engineering features: Multi-Agent, VectorDB, FastAPI, Async Pipeline, Local Model Hosting, Tool Call etc. Given a query, the system decide if the RAG documents contains sufficient information using pre-computed high-level summary, or requires external search for question answering.
```
[SETUP]
PDF → Chunks → { Chunk Summaries → Document Summary , VectorDB }

[SERVE]
QUERY → ROUTER → SUMMARY CONTAINS INFO?
              ↳ YES → RAG SIMILARITY SEARCH → ANSWER + SOURCE PAGE ID
              ↳ NO  → WEB SEARCH → ANSWER + SOURCE URL
```
Please note that this system is intended for demonstration purposes only and has not been fully refined (no prompt tuning, code linting, or thorough bug testing).

## Quick Start

### 1. Prerequisites
*   Python 3.12
*   Docker (for Qdrant)
*   requirements.txt

### 2. Environment Setup
Create a `.env` file in the root directory:

```bash
# API Keys
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Model Configuration
OPENAI_MODEL_NAME=gpt-4.1-mini

# Data Source Configuration
DOC_URL=https://requests.readthedocs.io/_/downloads/en/v2.0.0/pdf/
DOC_PAGE_START=11
DOC_PAGE_END=19

# Local Infrastructure
EMBEDDING_MODEL=jinaai/jina-code-embeddings-1.5b
EMBEDDING_URL=http://localhost:8000/v1

SLM_MODEL=Qwen/Qwen3-0.6B
SLM_URL=http://localhost:8001/v1

DB_COLLECTION_NAME=minimal_example
DB_URL=http://localhost:6333
```

### 3. Launch Services
We provide a helper script to spin up the Local Embedding Server, SLM Server, and Qdrant instance.

```bash
# Starts local model servers and vector DB
./bin/serve_all.sh
```

### 4. Start the Application
Start the FastAPI server. This will automatically trigger the **ingestion pipeline** (download -> chunk -> summarize -> index) on startup.

```bash
uvicorn backend:app --reload --port 8002
```

---

## Usage

The system exposes a REST API: `http://localhost:8002/docs`

### Scenario A: RAG (Internal Knowledge)
*The router detects this is a technical question about the ingested library.*

```bash
curl -X 'POST' \
  'http://localhost:8002/chat' \
  -H 'Content-Type: application/json' \
  -d '{ "question": "How to install Request?" }'
```
**Response:**
```json
{
  "answer": "To install the Requests library, you can use pip... $ pip install requests... (sources: Page 11)"
}
```

### Scenario B: Web Search (Real-time Info)
*The router detects this requires external knowledge not in the PDF.*

```bash
curl -X 'POST' \
  'http://localhost:8002/chat' \
  -H 'Content-Type: application/json' \
  -d '{ "question": "Who won the world series this year?" }'
```
**Response:**
```json
{
  "answer": "The Los Angeles Dodgers won the World Series this year (2025)... (sources: https://en.wikipedia.org/...)"
}
```

---

## Shutdown

To stop the local model servers and database:

```bash
./bin/shutdown.sh
```