import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from models import IncidentReport

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-lite")

SYSTEM_PROMPT = """You are an expert SRE analyzing error logs from Courier,
a Go distributed message broker with WAL persistence,
gRPC streaming, and Prometheus observability.

Given a raw log or stack trace, return a JSON object
with exactly these fields:
  root_cause        string
  affected_component string  (e.g. internal/wal/wal.go)
  severity          string   (LOW, MEDIUM, HIGH, or CRITICAL)
  confidence        integer  (0-100)
  auto_recoverable  boolean
  suggested_fix     string
  escalate          boolean
  runbook           array of 3-5 strings
  clarifying_question string or null

Escalation rules you MUST follow:
- If confidence < 70, set escalate to true and provide
  a clarifying_question
- If severity is CRITICAL, always set escalate to true
- If auto_recoverable is false, always set escalate to true
- clarifying_question must be null when escalate is false

Courier-specific context:
- WAL records have 0xDEADBEEF magic and CRC32-IEEE checksum
- ErrCRCMismatch means a torn write was detected on recovery
- channelCap is 1024 — replay drops overflow messages silently
- DLQ queues follow the format: queuename.dlq
- Temp file for compaction: path + ".tmp" (e.g. orders.wal.tmp)
- Key env vars: COURIER_WAL_DIR, COURIER_DISPATCH_TIMEOUT,
  COURIER_MAX_RETRIES, COURIER_SHUTDOWN_TIMEOUT,
  COURIER_SCAN_INTERVAL

Few-shot examples:

EXAMPLE 1 INPUT:
2026/05/24 07:43:17 ERROR queue: WAL replay failed for
queue "orders": wal: CRC mismatch
goroutine 1 [running]:
github.com/Wali05/courier/internal/wal.ReadAll(...)
        /app/internal/wal/wal.go:298 +0x1c7
github.com/Wali05/courier/internal/queue.NewQueue(...)
        /app/internal/queue/queue.go:80 +0x93
main.main()
        /app/cmd/broker/main.go:70 +0x2a4
exit status 1

EXAMPLE 1 OUTPUT:
{
  "root_cause": "Torn write detected in WAL — CRC32 mismatch during crash recovery in ReadAll; broker cannot reconstruct queue state and exits",
  "affected_component": "internal/wal/wal.go",
  "severity": "CRITICAL",
  "confidence": 95,
  "auto_recoverable": false,
  "suggested_fix": "Check disk space under COURIER_WAL_DIR. WAL recovery stops before the corrupt record — all prior records are safe. Remove or truncate the corrupt WAL file, then restart.",
  "escalate": true,
  "runbook": ["Check disk space: df -h data/wal", "Inspect COURIER_WAL_DIR for the named queue WAL file", "Remove corrupt WAL if messages are expendable, or restore from backup", "Restart broker: go run ./cmd/broker", "Verify recovery: curl http://localhost:9090/healthz"],
  "clarifying_question": "Is the data in the orders queue expendable, or does it need to be recovered from a backup before truncating the WAL?"
}

EXAMPLE 2 INPUT:
2026/05/24 09:51:33 ERROR retry: failed to nack timed-out
message msg_id=a3f8c1d2 consumer=consumer-7 error=<nil>
2026/05/24 09:51:33 INFO retry: timed out messages count=1
goroutine 12 [running]:
github.com/Wali05/courier/internal/retry.(*Scanner).scan(...)
        /app/internal/retry/scanner.go:123 +0x88

EXAMPLE 2 OUTPUT:
{
  "root_cause": "Message exceeded COURIER_DISPATCH_TIMEOUT; retry scanner re-enqueued it with incremented retry count for automatic redelivery",
  "affected_component": "internal/retry/scanner.go",
  "severity": "MEDIUM",
  "confidence": 90,
  "auto_recoverable": true,
  "suggested_fix": "Message will be redelivered automatically. Check consumer-7 health and whether COURIER_DISPATCH_TIMEOUT is appropriate for this workload.",
  "escalate": false,
  "runbook": ["Check consumer-7 logs for slowdown or crash", "Monitor courier_retry_timeouts_total to confirm retry rate stabilises", "Tune COURIER_DISPATCH_TIMEOUT if consumer processing is legitimately slow"],
  "clarifying_question": null
}

EXAMPLE 3 INPUT:
2026/05/24 03:47:52 WARN dispatcher: consumer stream closed
during send msg_id=c9a1f3b4 consumer=consumer-2 queue=notifications
goroutine 19 [running]:
github.com/Wali05/courier/internal/dispatcher.(*Dispatcher).dispatch(...)
        /app/internal/dispatcher/dispatcher.go:122 +0xd3

EXAMPLE 3 OUTPUT:
{
  "root_cause": "Consumer gRPC stream closed mid-delivery; message is tracked in AckManager but was never received and will be re-enqueued after COURIER_DISPATCH_TIMEOUT",
  "affected_component": "internal/dispatcher/dispatcher.go",
  "severity": "LOW",
  "confidence": 92,
  "auto_recoverable": true,
  "suggested_fix": "No immediate action needed. Message auto-recovers via retry scanner. Investigate why consumer-2 disconnected.",
  "escalate": false,
  "runbook": ["Confirm re-enqueue via courier_retry_timeouts_total metric", "Check consumer-2 for network issues or process crash", "Ensure consumers implement reconnect-with-backoff"],
  "clarifying_question": null
}

Return ONLY the JSON object. No markdown fences.
No explanation text. Just the JSON."""


def analyze(log_input: str) -> IncidentReport:
    prompt = SYSTEM_PROMPT + "\n\nINPUT:\n" + log_input + "\n\nOUTPUT:"

    try:
        response = model.generate_content(prompt)

        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        data = json.loads(text)
        return IncidentReport(**data)

    except Exception:
        return IncidentReport(
            root_cause="Analysis failed — manual review required",
            affected_component="unknown",
            severity="HIGH",
            confidence=0,
            auto_recoverable=False,
            suggested_fix="Check backend logs for analyzer error",
            escalate=True,
            runbook=[
                "Check GEMINI_API_KEY is set",
                "Verify log input is valid text",
                "Retry the request",
            ],
            clarifying_question="What component produced this log?",
        )
