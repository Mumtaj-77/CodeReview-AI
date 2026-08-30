import sys
import os
import time
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import create_tables, get_db, SessionLocal
from backend.database.models import Review, BugRecord
from backend.agents.pipeline import build_pipeline, ReviewState

app = FastAPI(
    title="CodeReview AI",
    description="Multi-agent code review system with intelligent LLM routing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = build_pipeline()
jobs = {}

@app.on_event("startup")
def startup():
    create_tables()
    print("CodeReview AI started")

@app.get("/")
def root():
    return {"project": "CodeReview AI", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

class CodeRequest(BaseModel):
    code: str
    filename: Optional[str] = "code.py"

@app.post("/review")
async def create_review(request: CodeRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing", "report": None}
    background_tasks.add_task(run_review, job_id=job_id, code=request.code, filename=request.filename)
    return {"job_id": job_id, "status": "processing", "message": "Review started."}

@app.post("/upload")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    allowed = ['.py', '.js', '.java', '.ts', '.cpp', '.cs', '.go', '.rb', '.php']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(allowed)}"
        )
    content = await file.read()
    try:
        code = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing", "report": None}
    background_tasks.add_task(run_review, job_id=job_id, code=code, filename=file.filename)
    return {"job_id": job_id, "status": "processing", "filename": file.filename}

async def run_review(job_id: str, code: str, filename: str):
    db = SessionLocal()
    try:
        initial_state = ReviewState(
            code=code,
            parsed=None,
            route_decision=None,
            bugs=[],
            security_issues=[],
            fixes=[],
            explanations=[],
            report={},
            start_time=time.time()
        )

        result = pipeline.invoke(initial_state)
        report = result["report"]

        review = Review(
            code=code,
            language=report["summary"]["language"],
            filename=filename,
            total_bugs=report["summary"]["total_bugs"],
            total_security=report["summary"]["total_security_issues"],
            total_fixes=report["summary"]["total_fixes"],
            severity=report["summary"]["severity"],
            model_used=report["summary"]["model_used"],
            review_time=report["summary"]["review_time_seconds"],
            report=report,
            status="completed"
        )
        db.add(review)
        db.commit()
        db.refresh(review)

        for bug in report["bugs"]:
            db.add(BugRecord(
                review_id=review.id,
                line=bug["line"],
                severity=bug["severity"],
                category=bug["category"],
                description=bug["description"],
                fix=bug["fix"]
            ))
        db.commit()

        jobs[job_id] = {
            "status": "completed",
            "review_id": review.id,
            "report": report
        }

    except Exception as e:
        jobs[job_id] = {"status": "failed", "error": str(e)}
        print(f"Review failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

@app.get("/review/{job_id}")
def get_review(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    reviews = db.query(Review).order_by(Review.created_at.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "language": r.language,
            "total_bugs": r.total_bugs,
            "total_security": r.total_security,
            "severity": r.severity,
            "review_time": r.review_time,
            "created_at": str(r.created_at)
        }
        for r in reviews
    ]

@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    total = db.query(Review).count()
    reviews = db.query(Review).all()
    avg_time = sum(r.review_time or 0 for r in reviews) / max(total, 1)
    total_bugs = sum(r.total_bugs or 0 for r in reviews)
    return {
        "total_reviews": total,
        "total_bugs_found": total_bugs,
        "average_review_time": round(avg_time, 2),
        "pipeline_status": "operational"
    }