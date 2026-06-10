# API Guide

This project contains three FastAPI entry points.

## Basic API

Start:

```powershell
uvicorn main:app --reload
```

Health check:

```powershell
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## AI API

Start:

```powershell
uvicorn llm_api:app --reload --port 8001
```

Health check:

```powershell
curl http://127.0.0.1:8001/health
```

### Summarize Text

Endpoint:

```text
POST /summarize
```

Example:

```powershell
curl -X POST http://127.0.0.1:8001/summarize `
  -H "Content-Type: application/json" `
  -d "{\"text\":\"Users are seeing payment failures after deployment CR-4821. Error logs show NullPointerException in PaymentService.java during authorization. Debit card transactions still work, but credit card transactions are failing.\",\"max_words\":100,\"focus\":\"root cause and action items\"}"
```

### Analyze Ticket

Endpoint:

```text
POST /analyze-ticket
```

Example:

```powershell
curl -X POST http://127.0.0.1:8001/analyze-ticket `
  -H "Content-Type: application/json" `
  -d "{\"description\":\"RTC-8821: Payment authorization fails for credit card transactions after CR-4821 deployment. Logs show NullPointerException in PaymentService.processTransaction.\"}"
```

## Ticket API

Start:

```powershell
uvicorn ticket_api:app --reload --port 8002
```

### Create Ticket

Endpoint:

```text
POST /tickets
```

Example:

```powershell
curl -X POST http://127.0.0.1:8002/tickets `
  -H "Content-Type: application/json" `
  -d "{\"id\":\"RTC-8821\",\"severity\":\"High\",\"module\":\"PaymentService\",\"description\":\"Payment processing fails for credit card authorization.\",\"assignee\":\"support-engineer\"}"
```

### Get Ticket

```powershell
curl http://127.0.0.1:8002/tickets/RTC-8821
```

### List Tickets

```powershell
curl http://127.0.0.1:8002/tickets
```

Filter by severity:

```powershell
curl "http://127.0.0.1:8002/tickets?severity=High"
```

## Interactive Docs

FastAPI also provides browser-based API docs:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8001/docs
http://127.0.0.1:8002/docs
```
