from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import AnalyzeRequest, IncidentReport
from analyzer import analyze

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=IncidentReport)
def analyze_endpoint(request: AnalyzeRequest):
    try:
        return analyze(request.log_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
