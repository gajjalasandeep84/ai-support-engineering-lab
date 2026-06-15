import logging
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NYSOH Stream API")

llm_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
MODEL = "llama3.2:3b"

# ── Models ─────────────────────────────────────────────
class StreamRequest(BaseModel):
    prompt: str             = Field(..., min_length=5)
    system: Optional[str]  = Field("You are a helpful Java expert.")

class InvestigateRequest(BaseModel):
    description: str = Field(..., min_length=20,
                             description="Ticket description to investigate")

# ── Generators ─────────────────────────────────────────
def generate_stream(messages: list[dict], label: str = ""):
    logger.info(f"Stream started: {label}")
    try:
        response = llm_client.chat.completions.create(
            model=MODEL, messages=messages, stream=True
        )
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
    except Exception as e:
        logger.error(f"Stream failed: {e}", exc_info=True)
        yield "\n[Error: LLM unavailable]"
    finally:
        logger.info(f"Stream ended: {label}")

def generate_sse(messages: list[dict]):
    logger.info("SSE stream started")
    try:
        response = llm_client.chat.completions.create(
            model=MODEL, messages=messages, stream=True
        )
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                data = json.dumps({"token": delta.content})
                yield f"data: {data}\n\n"
    except Exception as e:
        logger.error(f"SSE failed: {e}", exc_info=True)
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
    finally:
        yield "data: [DONE]\n\n"
        logger.info("SSE stream ended")

# ── Endpoints ──────────────────────────────────────────
@app.post("/stream")
def stream_response(request: StreamRequest):
    messages = [
        {"role": "system", "content": request.system},
        {"role": "user",   "content": request.prompt}
    ]
    return StreamingResponse(
        generate_stream(messages, label="stream"),
        media_type="text/plain"
    )

@app.post("/stream/sse")
def stream_sse(request: StreamRequest):
    messages = [
        {"role": "system", "content": request.system},
        {"role": "user",   "content": request.prompt}
    ]
    return StreamingResponse(
        generate_sse(messages),
        media_type="text/event-stream"
    )

@app.post("/stream/plain")
def stream_plain(request: StreamRequest):
    messages = [
        {"role": "system", "content": request.system},
        {"role": "user",   "content": request.prompt}
    ]
    return StreamingResponse(
        generate_stream(messages, label="plain"),
        media_type="text/plain"
    )

@app.post("/stream/investigate")
def stream_investigate(request: InvestigateRequest):
    system_prompt = """You are a senior Java enterprise investigator.
Think out loud as you investigate. Structure your response as steps:

Step 1: Read the ticket description carefully
Step 2: Identify the error type and module affected
Step 3: Check what likely changed recently
Step 4: Identify the root cause
Step 5: Recommend the fix

Be conversational — as if narrating your investigation in real time."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",
         "content": f"Investigate this ticket:\n\n{request.description}"}
    ]
    return StreamingResponse(
        generate_stream(messages, label="investigate"),
        media_type="text/plain"
    )

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}