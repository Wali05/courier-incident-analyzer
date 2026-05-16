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

const SEVERITY_STYLES: Record<
  IncidentData["severity"],
  { bg: string; color: string; fill: string }
> = {
  LOW: { bg: "#22c55e", color: "#052e16", fill: "#22c55e" },
  MEDIUM: { bg: "#eab308", color: "#1c1917", fill: "#eab308" },
  HIGH: { bg: "#f97316", color: "#ffffff", fill: "#f97316" },
  CRITICAL: { bg: "#ef4444", color: "#ffffff", fill: "#ef4444" },
};

const LABEL_STYLE: React.CSSProperties = {
  color: "#94a3b8",
  fontSize: "11px",
  fontWeight: 600,
  textTransform: "uppercase",
  letterSpacing: "0.1em",
  marginBottom: "6px",
  display: "block",
};

const SECTION_STYLE: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "4px",
};

export default function IncidentReport({ data }: { data: IncidentData }) {
  const sev = SEVERITY_STYLES[data.severity];

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "20px",
        width: "100%",
      }}
    >
      {/* 1. TOP ROW â€” Severity badge + Confidence bar */}
      <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
        {/* Severity badge */}
        <div>
          <span
            style={{
              backgroundColor: sev.bg,
              color: sev.color,
              fontWeight: 700,
              fontSize: "12px",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              borderRadius: "6px",
              padding: "4px 12px",
              display: "inline-block",
            }}
          >
            {data.severity}
          </span>
        </div>

        {/* Confidence bar */}
        <div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "6px",
            }}
          >
            <span style={{ color: "#94a3b8", fontSize: "12px" }}>
              Confidence
            </span>
            <span style={{ color: "#e2e8f0", fontSize: "12px", fontWeight: 600 }}>
              {data.confidence}%
            </span>
          </div>
          <div
            style={{
              backgroundColor: "#374151",
              borderRadius: "9999px",
              height: "8px",
              width: "100%",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                className={`w-[${data.confidence}%] bg-[${sev.fill}] h-full transition-all`},
              }}
            />
          </div>
        </div>
      </div>

      {/* 2. ROOT CAUSE */}
      <div style={SECTION_STYLE}>
        <span style={LABEL_STYLE}>Root Cause</span>
        <p
          style={{
            color: "#f1f5f9",
            fontSize: "16px",
            fontWeight: 400,
            margin: 0,
            lineHeight: "1.6",
          }}
        >
          {data.root_cause}
        </p>
      </div>

      {/* 3. AFFECTED COMPONENT */}
      <div style={SECTION_STYLE}>
        <span style={LABEL_STYLE}>Affected Component</span>
        <code
          style={{
            color: "#94a3b8",
            fontSize: "14px",
            fontFamily: "monospace",
          }}
        >
          {data.affected_component}
        </code>
      </div>

      {/* 4. RECOVERY STATUS */}
      <div
        style={{
          backgroundColor: data.auto_recoverable ? "#14532d" : "#450a0a",
          borderRadius: "9999px",
          padding: "10px 16px",
          color: data.auto_recoverable ? "#4ade80" : "#f87171",
          fontSize: "13px",
          fontWeight: 600,
          textAlign: "center",
        }}
      >
        {data.auto_recoverable
          ? "âœ“ Auto-recoverable â€” retry scanner handles this"
          : "âš  Escalate to human â€” manual intervention required"}
      </div>

      {/* 5. SUGGESTED FIX â€” only when auto_recoverable */}
      {data.auto_recoverable && (
        <div style={SECTION_STYLE}>
          <span style={LABEL_STYLE}>Suggested Fix</span>
          <pre
            style={{
              backgroundColor: "#1e293b",
              color: "#94a3b8",
              fontFamily: "monospace",
              fontSize: "13px",
              padding: "12px",
              borderRadius: "8px",
              margin: 0,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {data.suggested_fix}
          </pre>
        </div>
      )}

      {/* 6. RUNBOOK */}
      <div style={SECTION_STYLE}>
        <span style={LABEL_STYLE}>Runbook</span>
        <ol
          style={{
            margin: 0,
            paddingLeft: "20px",
            display: "flex",
            flexDirection: "column",
            gap: "8px",
          }}
        >
          {data.runbook.map((step, i) => (
            <li
              key={i}
              style={{ color: "#f1f5f9", fontSize: "14px", lineHeight: "1.55" }}
            >
              {step}
            </li>
          ))}
        </ol>
      </div>

      {/* 7. CLARIFYING QUESTION â€” only when escalate=true and not null */}
      {data.escalate && data.clarifying_question && (
        <div
          style={{
            backgroundColor: "#422006",
            border: "1px solid #92400e",
            borderRadius: "8px",
            padding: "12px 14px",
            color: "#fde68a",
            fontSize: "13px",
            lineHeight: "1.55",
          }}
        >
          <strong>?</strong> {data.clarifying_question}
        </div>
      )}
    </div>
  );
}

