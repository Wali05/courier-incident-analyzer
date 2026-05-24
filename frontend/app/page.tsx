"use client";

import { useState } from "react";
import IncidentReport from "./components/IncidentReport";

const DEFAULT_LOG = `2026/05/24 07:43:17 ERROR queue: WAL replay failed for queue "orders": wal: CRC mismatch
goroutine 1 [running]:
github.com/Wali05/courier/internal/wal.ReadAll(...)
        /app/internal/wal/wal.go:298 +0x1c7
github.com/Wali05/courier/internal/queue.NewQueue(...)
        /app/internal/queue/queue.go:80 +0x93
main.main()
        /app/cmd/broker/main.go:70 +0x2a4
exit status 1`;

interface IncidentData {
  root_cause: string;
  affected_component: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  confidence: number;
  auto_recoverable: boolean;
  suggested_fix: string;
  escalate: boolean;
  runbook: string[];
  clarifying_question: string | null;
}

export default function Home() {
  const [log, setLog] = useState(DEFAULT_LOG);
  const [result, setResult] = useState<IncidentData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ log_input: log }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: IncidentData = await res.json();
      setResult(data);
    } catch {
      setError("Backend error — is the FastAPI server running on port 8000?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      style={{ backgroundColor: "#0f1117", minHeight: "100vh", padding: "24px" }}
    >
      {/* Header */}
      <div style={{ marginBottom: "24px" }}>
        <h1
          style={{
            color: "#f1f5f9",
            fontSize: "22px",
            fontWeight: 700,
            letterSpacing: "0.02em",
            margin: 0,
          }}
        >
          🛰 Courier Incident Analyzer
        </h1>
        <p style={{ color: "#64748b", fontSize: "13px", marginTop: "4px" }}>
          Powered by Gemini · WAL · gRPC · Prometheus
        </p>
      </div>

      {/* Two-column layout */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
          gap: "20px",
          alignItems: "start",
        }}
      >
        {/* LEFT PANEL */}
        <div
          style={{
            backgroundColor: "#1a1d27",
            borderRadius: "12px",
            padding: "24px",
            display: "flex",
            flexDirection: "column",
            gap: "16px",
          }}
        >
          <label
            style={{
              color: "#94a3b8",
              fontSize: "11px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
            }}
          >
            Error Log / Stack Trace
          </label>

          <textarea
            value={log}
            onChange={(e) => setLog(e.target.value)}
            style={{
              backgroundColor: "#0d1117",
              color: "#e2e8f0",
              fontFamily: "monospace",
              fontSize: "13px",
              lineHeight: "1.6",
              border: "1px solid #2d3748",
              borderRadius: "8px",
              padding: "14px",
              minHeight: "320px",
              resize: "none",
              outline: "none",
              width: "100%",
              boxSizing: "border-box",
            }}
            spellCheck={false}
          />

          {error && (
            <div
              style={{
                backgroundColor: "#450a0a",
                border: "1px solid #7f1d1d",
                color: "#f87171",
                borderRadius: "8px",
                padding: "12px 14px",
                fontSize: "13px",
              }}
            >
              {error}
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading || !log.trim()}
            style={{
              backgroundColor: loading || !log.trim() ? "#1e3a5f" : "#3b82f6",
              color: "#ffffff",
              border: "none",
              borderRadius: "8px",
              padding: "12px 0",
              fontSize: "14px",
              fontWeight: 600,
              cursor: loading || !log.trim() ? "not-allowed" : "pointer",
              width: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              transition: "background-color 0.2s",
            }}
          >
            {loading && (
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{ animation: "spin 1s linear infinite" }}
              >
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
            )}
            {loading ? "Analyzing..." : "Analyze Incident"}
          </button>
        </div>

        {/* RIGHT PANEL */}
        <div
          style={{
            backgroundColor: "#1a1d27",
            borderRadius: "12px",
            padding: "24px",
            minHeight: "200px",
            display: "flex",
            alignItems: result ? "flex-start" : "center",
            justifyContent: result ? "flex-start" : "center",
          }}
        >
          {result ? (
            <IncidentReport data={result} />
          ) : (
            <p
              style={{
                color: "#475569",
                fontSize: "14px",
                textAlign: "center",
              }}
            >
              Paste a log and click Analyze
            </p>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </main>
  );
}
