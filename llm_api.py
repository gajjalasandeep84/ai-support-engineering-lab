import logging
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NYSOH AI API", version="1.0.0")

# LLM client — configured once, reused across requests
llm_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
MODEL = "llama3.2:3b"

# ── Models ─────────────────────────────────────────────
class SummarizeRequest(BaseModel):
    text:          str  = Field(..., min_length=20,
                                description="Document text to summarize")
    max_words:     int  = Field(150, ge=50, le=500)
    focus:         Optional[str] = Field(None,
                                description="What to focus on e.g. 'root cause'")

class SummarizeResponse(BaseModel):
    summary:       str
    key_points:    list[str]
    tokens_used:   int

# ── LLM helper ─────────────────────────────────────────
def call_llm(messages: list[dict],
             temperature: float = 0.3,
             max_tokens: int = 500) -> tuple[str, int]:
    """
    Call LLM and return (content, tokens_used).
    Raises HTTPException on failure.
    """
    try:
        response = llm_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        content     = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        logger.info(f"LLM response: {len(content)} chars, {tokens_used} tokens")
        return content, tokens_used

    except Exception as e:
        logger.error(f"LLM call failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service unavailable"
        )

# ── Endpoints ──────────────────────────────────────────
@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    logger.info(f"Summarizing {len(request.text)} chars")

    focus_instruction = ""
    if request.focus:
        focus_instruction = f"Focus especially on: {request.focus}"

    messages = [
        {
            "role": "system",
            "content": f"""You are a technical document analyst.
Summarize the provided text in under {request.max_words} words.
Return your response in this exact format:

SUMMARY:
[your summary here]

KEY_POINTS:
- [point 1]
- [point 2]
- [point 3]

{focus_instruction}"""
        },
        {
            "role": "user",
            "content": f"Summarize this document:\n\n{request.text}"
        }
    ]

    content, tokens = call_llm(messages)

    # Parse the structured response
    summary    = ""
    key_points = []

    if "SUMMARY:" in content and "KEY_POINTS:" in content:
        parts      = content.split("KEY_POINTS:")
        summary    = parts[0].replace("SUMMARY:", "").strip()
        key_points = [
            line.strip().lstrip("- ")
            for line in parts[1].strip().split("\n")
            if line.strip().startswith("-")
        ]
    else:
        summary    = content
        key_points = []

    return SummarizeResponse(
        summary=summary,
        key_points=key_points,
        tokens_used=tokens
    )

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}

#ticket description as request
class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=20,
                             description="Ticket description to analyze")



class AnalyzeResponse(BaseModel):
    severity_assessment: str
    likely_cause: str
    recommended_action: str
    tokens_used: int

#A second endpoint POST /analyze-ticket that takes a ticket description and returns:
#severity_assessment — High/Medium/Low
#likely_cause — one sentence
#recommended_action — one sentence
#tokens_used — int
@app.post("/analyze-ticket")
@app.post("/analyze-ticket", response_model=AnalyzeResponse)
def analyze_ticket(request: AnalyzeRequest):
    logger.info(f"Analyzing: {request.description[:50]}...")

    messages = [
        {
            "role": "system",
            "content": """You are a senior Java enterprise support analyst.
Analyze the ticket and return ONLY this exact format — no extra text:

SEVERITY: High/Medium/Low
LIKELY_CAUSE: one sentence describing the root cause
RECOMMENDED_ACTION: one sentence describing the immediate fix"""
        },
        {
            "role": "user",
            "content": f"Analyze this ticket:\n\n{request.description}"
        }
    ]

    content, tokens = call_llm(messages)

    # Parse line by line
    severity_assessment = "Unknown"
    likely_cause        = "Unknown"
    recommended_action  = "Unknown"

    for line in content.strip().split("\n"):
        line = line.strip()
        if line.startswith("SEVERITY:"):
            severity_assessment = line.replace("SEVERITY:", "").strip()
        elif line.startswith("LIKELY_CAUSE:"):
            likely_cause = line.replace("LIKELY_CAUSE:", "").strip()
        elif line.startswith("RECOMMENDED_ACTION:"):
            recommended_action = line.replace("RECOMMENDED_ACTION:", "").strip()

    logger.info(f"Analysis complete — severity: {severity_assessment}")

    return AnalyzeResponse(
        severity_assessment=severity_assessment,
        likely_cause=likely_cause,
        recommended_action=recommended_action,
        tokens_used=tokens
    )