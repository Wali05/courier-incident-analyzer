from pydantic import BaseModel
from typing import Optional, Literal


class IncidentReport(BaseModel):
    root_cause: str
    affected_component: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    confidence: int           # 0 to 100
    auto_recoverable: bool
    suggested_fix: str        # concrete action or code snippet
    escalate: bool
    runbook: list[str]        # 3 to 5 steps
    clarifying_question: Optional[str] = None


class AnalyzeRequest(BaseModel):
    log_input: str
