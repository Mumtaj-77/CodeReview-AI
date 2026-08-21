from fastapi import FastAPI

app = FastAPI(
    title="CodeReview AI",
    description="Multi-agent code review system with intelligent LLM routing",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "project": "CodeReview AI",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}