# Courier Incident Analyzer

AI-powered incident analyzer for Go distributed systems — 
paste an error log, get root cause, suggested fix, and 
escalation decision.

## Motivation

Built from real failure modes in Courier 
(github.com/Wali05/courier) — a Go message broker with 
WAL-based durability, gRPC streaming, and 
Prometheus/Grafana observability. When you've built the 
system that fails at 3am, you know which information 
actually matters for diagnosis.

Same reliability methodology as the bookkeeping eval:
github.com/Wali05/bookkeeping-ai-eval

## Evaluation Results

Ran the analyzer against 10 ground-truth failure cases 
derived directly from Courier's source code — real 
failure modes, not synthetic examples.

| Confidence Bucket | Accuracy | Count |
|-------------------|----------|-------|
| High (90–100)     | 50%      | 6     |
| Medium (70–89)    | 33%      | 3     |
| Low (<70)         | 100%     | 1     |

**Key finding:** The model was most accurate when it 
was least confident. At high confidence (90-100%), it 
was wrong half the time — confidently misdiagnosing 
real production failure modes. This mirrors the same 
overconfidence pattern found in the bookkeeping eval: 
models assign high confidence to plausible-sounding 
answers without sufficient grounding in system-specific 
context.

This is the core reliability problem in AI-powered 
observability tools — not that models get things wrong, 
but that they don't know when they're wrong.

## What it covers

- WAL CRC32 mismatch on crash recovery
- WAL directory missing at startup
- Dispatch timeout with automatic retry
- Max retries exhausted — DLQ routing
- Consumer gRPC stream closed mid-delivery
- WAL compaction atomic rename failure
- Partial write on last WAL record
- Graceful shutdown drain timeout
- WAL replay channel overflow (silent data loss)
- Duplicate ACK on unknown message ID

## Stack

Backend: FastAPI + Gemini Flash + Pydantic v2
Frontend: Next.js 14 + TypeScript + Tailwind CSS

## Setup

### Backend
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY
uvicorn main:app --reload --port 8000

### Frontend
cd frontend && npm install && npm run dev

### Evaluate
cd backend && python evaluate.py

## Related

Built on the same confidence calibration methodology 
as github.com/Wali05/bookkeeping-ai-eval — applied to 
distributed systems observability instead of LLM 
financial accuracy.
