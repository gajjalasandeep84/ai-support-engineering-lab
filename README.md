# AI Support Engineering Lab

Python experiments for local LLM-powered support engineering workflows, including ticket analysis, document summarization, FastAPI endpoints, and Ollama-based chat tooling.

## Overview

This repository is a hands-on AI engineering lab focused on practical support and production-investigation use cases. The examples use Python, FastAPI, Ollama, and local LLM calls to explore how AI can help with:

- Enterprise ticket intake and validation
- Incident and document summarization
- Root-cause and severity analysis
- Streaming LLM responses for live investigation workflows
- Local chatbot workflows for Java/Spring Boot support
- API calling, retries, logging, and async HTTP patterns

The project is intentionally small and readable so each script can be studied independently.

## Project Structure

| Path | Purpose |
| --- | --- |
| `main.py` | Minimal FastAPI health-check service |
| `ticket_api.py` | Ticket API with validation, severity enum, request logging, and in-memory storage |
| `llm_api.py` | FastAPI service for document summarization and ticket analysis using an Ollama-hosted model |
| `stream_api.py` | FastAPI service for plain-text and Server-Sent Events streaming LLM responses |
| `chatbot.py` | CLI chatbot that keeps conversation history and calls Ollama |
| `summarize.py` | Local document analyzer that summarizes `sample_doc.txt` into structured JSON |
| `api_caller.py` | REST API retry/logging exercise |
| `async_fetcher.py` | Async HTTP example using `httpx.AsyncClient` |
| `firstExercise.py` | Basic ticket-list analysis exercise |
| `sample_doc.txt` | Sample incident report used by the summarizer |
| `docs/SETUP.md` | Local environment and setup instructions |
| `docs/API.md` | API run commands and sample requests |

## Requirements

- Python 3.10 or newer
- Ollama installed locally
- `llama3.2:3b` pulled in Ollama, or another model configured in the scripts

See [docs/SETUP.md](docs/SETUP.md) for full setup instructions.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull llama3.2:3b
```

Run the basic API:

```powershell
uvicorn main:app --reload
```

Run the AI API:

```powershell
uvicorn llm_api:app --reload --port 8001
```

Run the ticket API:

```powershell
uvicorn ticket_api:app --reload --port 8002
```

Run the streaming AI API:

```powershell
uvicorn stream_api:app --reload --port 8003
```

Run the CLI chatbot:

```powershell
python chatbot.py
```

Run the document summarizer:

```powershell
python summarize.py
```

## Notes

This is a learning and experimentation repo, not a production service. The APIs use in-memory storage, local model calls, and simple response parsing to keep the examples approachable.

## License

This project is available for learning and portfolio use. Add a formal license file before using it in a shared or commercial environment.
