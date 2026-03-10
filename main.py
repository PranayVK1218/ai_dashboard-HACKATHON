"""
InsightAI Backend — main.py
FastAPI server for the India Life Insurance Claims Dashboard.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn
from gemini_query import GeminiQueryEngine
from database import DatabaseEngine

app = FastAPI(
    title="InsightAI API",
    description="Conversational AI for India Life Insurance Business Intelligence",
    version="1.0.0"
)

# CORS — allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Initialize engines
db = DatabaseEngine(csv_path="../data/sales_data.csv")
ai = GeminiQueryEngine()


class QueryRequest(BaseModel):
    question: str
    year: Optional[str] = None
    insurer: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sql: Optional[str] = None
    data: Optional[list] = None
    chart_type: Optional[str] = None


@app.get("/")
def root():
    return {"message": "InsightAI is running. Visit /docs for API reference."}


@app.get("/api/data")
def get_data(year: Optional[str] = None, insurer: Optional[str] = None):
    """Return filtered claims data."""
    return db.query(year=year, insurer=insurer)


@app.get("/api/kpis")
def get_kpis(year: Optional[str] = None):
    """Return KPI summary for the given year."""
    return db.get_kpis(year=year)


@app.get("/api/trend")
def get_trend():
    """Return year-over-year trend data."""
    return db.get_trend()


@app.get("/api/insurers")
def get_insurers():
    """Return list of all unique insurers."""
    return db.get_insurers()


@app.post("/api/ask", response_model=QueryResponse)
async def ask_question(req: QueryRequest):
    """
    Process a natural language question via the Gemini AI engine.
    Returns an answer, the generated SQL, and data for chart rendering.
    """
    try:
        context = db.get_context_summary(year=req.year, insurer=req.insurer)
        result = await ai.answer(req.question, context)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health():
    return {"status": "ok", "records": db.count()}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)