import logging
import time
import uuid
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum  # add this import

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#Add a Severity enum — reject anything that isn't High/Medium/Low
# Change 1 — fix Severity:
class Severity(str, Enum):
    HIGH   = "High"
    MEDIUM = "Medium"
    LOW    = "Low"

app = FastAPI(
    title="NYSOH Ticket API",
    description="AI-powered ticket investigation system",
    version="1.0.0"
)

    

# Models
# Change 2 — use Severity type in model:
class TicketRequest(BaseModel):
    id:          str      = Field(..., min_length=3, max_length=20,
                                  description="RTC ticket ID e.g. RTC-8821")
    severity:    Severity          # ← was str, now Severity enum
    module:      str
    description: str      = Field(..., min_length=10)
    assignee:    Optional[str] = None

    @validator("id")
    def id_must_start_with_rtc(cls, v):
        if not v.upper().startswith("RTC-"):
            raise ValueError("Ticket ID must start with RTC-")
        return v.upper()


class TicketResponse(BaseModel):
    id:       str
    severity: str
    module:   str
    status:   str

# In-memory store (DB comes in Phase 4)
tickets: dict = {}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    cid   = str(uuid.uuid4())[:8]
    start = time.time()
    logger.info(f"[{cid}] {request.method} {request.url.path}")
    response = await call_next(request)
    elapsed  = (time.time() - start) * 1000
    logger.info(f"[{cid}] {response.status_code} in {elapsed:.0f}ms")
    response.headers["X-Correlation-ID"] = cid
    return response


@app.get("/")
def root():
    return {"service": "NYSOH Ticket API", "version": "1.0.0"}

@app.post("/tickets", response_model=TicketResponse,
          status_code=status.HTTP_201_CREATED)
def create_ticket(request: TicketRequest):
    logger.info(f"Creating ticket {request.id}")
    if request.id in tickets:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ticket {request.id} already exists"
        )
    tickets[request.id] = request.dict()
    logger.info(f"Ticket {request.id} created")
    return TicketResponse(
        id=request.id,
        severity=request.severity,
        module=request.module,
        status="Open"
    )

@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str):
    logger.info(f"Fetching ticket {ticket_id}")
    if ticket_id not in tickets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found"
        )
    t = tickets[ticket_id]
    return TicketResponse(
        id=t["id"],
        severity=t["severity"],
        module=t["module"],
        status="Open"
    )

@app.get("/tickets")
def list_tickets(severity: Optional[str] = None):
    result = list(tickets.values())
    if severity:
        result = [t for t in result if t["severity"] == severity]
    return {"count": len(result), "tickets": result}