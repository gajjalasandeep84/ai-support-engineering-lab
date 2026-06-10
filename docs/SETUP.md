# Setup Guide

This guide sets up the project locally on Windows PowerShell.

## 1. Clone the Repository

```powershell
git clone https://github.com/gajjalasandeep84/ai-support-engineering-lab.git
cd ai-support-engineering-lab
```

## 2. Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If script execution is blocked, run PowerShell as your user and allow local scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 3. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

## 4. Install and Start Ollama

Install Ollama from:

```text
https://ollama.com/download
```

Pull the model used by the project:

```powershell
ollama pull llama3.2:3b
```

Verify Ollama is running:

```powershell
ollama list
```

The scripts expect Ollama at:

```text
http://localhost:11434
```

## 5. Run the Services

Basic health API:

```powershell
uvicorn main:app --reload
```

AI summarization and ticket-analysis API:

```powershell
uvicorn llm_api:app --reload --port 8001
```

Ticket API:

```powershell
uvicorn ticket_api:app --reload --port 8002
```

## 6. Run the Scripts

CLI chatbot:

```powershell
python chatbot.py
```

Document summarizer:

```powershell
python summarize.py
```

Async HTTP example:

```powershell
python async_fetcher.py
```

API retry/logging example:

```powershell
python api_caller.py
```

## Troubleshooting

### Ollama Connection Fails

Make sure Ollama is running and the model is available:

```powershell
ollama list
ollama pull llama3.2:3b
```

### FastAPI Command Not Found

Make sure the virtual environment is active and dependencies are installed:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Port Already in Use

Run the API on another port:

```powershell
uvicorn llm_api:app --reload --port 8010
```
