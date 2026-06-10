import requests
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict

# ── Logging ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("summarizer.log")
    ]
)
logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL      = "llama3.2:3b"
MAX_CHARS  = 3000   # max document size before chunking

# ── Data model for structured output ───────────────────
@dataclass
class DocumentSummary:
    title:       str
    severity:    str
    key_points:  list
    root_cause:  str
    action_items: list
    confidence:  str

# ── Read document ──────────────────────────────────────
def read_document(filepath: str) -> str:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {filepath}")

    logger.info(f"Reading document: {filepath}")
    content = path.read_text(encoding="utf-8")
    logger.info(f"Document loaded — {len(content)} characters")
    return content

# ── Chunk if too large ─────────────────────────────────
def chunk_document(content: str, max_chars: int) -> list[str]:
    if len(content) <= max_chars:
        return [content]

    chunks = []
    words  = content.split()
    current_chunk = []
    current_len   = 0

    for word in words:
        current_len += len(word) + 1
        if current_len > max_chars:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_len   = len(word)
        else:
            current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    logger.info(f"Document split into {len(chunks)} chunks")
    return chunks

# ── Parse LLM JSON response ────────────────────────────
def parse_llm_response(response_text: str) -> dict:
    """Strip markdown fences and parse JSON — Day 9 pattern"""
    clean = response_text.strip()
    if clean.startswith("```json"):
        clean = clean[7:]
    if clean.startswith("```"):
        clean = clean[3:]
    if clean.endswith("```"):
        clean = clean[:-3]
    try:
        return json.loads(clean.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response: {e}", exc_info=True)
        return {}

# ── Call LLM ───────────────────────────────────────────
def summarize_chunk(chunk: str, chunk_num: int) -> dict:
    system_prompt = """You are an expert technical analyst.
Analyze the provided document and return ONLY a JSON object.
No markdown, no explanation — pure JSON only.

Return this exact structure:
{
  "title": "document title or topic",
  "severity": "High/Medium/Low/Unknown",
  "key_points": ["point 1", "point 2", "point 3"],
  "root_cause": "identified root cause or Unknown",
  "action_items": ["action 1", "action 2"],
  "confidence": "High/Medium/Low"
}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",
         "content": f"Analyze this document:\n\n{chunk}"}
    ]

    payload = {
        "model":    MODEL,
        "messages": messages,
        "stream":   False
    }

    try:
        logger.info(f"Summarizing chunk {chunk_num}")
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        raw = response.json()["message"]["content"]
        logger.info(f"Chunk {chunk_num} summarized")
        return parse_llm_response(raw)

    except requests.Timeout:
        logger.error(f"Timeout on chunk {chunk_num}", exc_info=True)
        return {}
    except Exception as e:
        logger.error(f"Error on chunk {chunk_num}: {e}", exc_info=True)
        return {}

# ── Save summary ───────────────────────────────────────
def save_summary(summary: dict, output_path: str):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Summary saved to {output_path}")

# ── Main ───────────────────────────────────────────────
def main():
    input_file  = "C:\\Development\\python\\ai-engineering\\sample_doc.txt"
    output_file = "C:\\Development\\python\\ai-engineering\\summaries\\summary.json"

    try:
        # Read document
        content = read_document(input_file)

        # Chunk if needed
        chunks = chunk_document(content, MAX_CHARS)

        # Summarize — first chunk for now
        # (multi-chunk merging comes in Phase 4 RAG)
        summary = summarize_chunk(chunks[0], chunk_num=1)

        if not summary:
            logger.error("No summary generated")
            return

        # Print results
        print("\n=== Document Summary ===")
        print(json.dumps(summary, indent=2))

        # Save to file
        save_summary(summary, output_file)
        print(f"\nSaved to {output_file}")

    except FileNotFoundError as e:
        logger.error(f"File error: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)

if __name__ == "__main__":
    main()