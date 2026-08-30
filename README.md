<div align="center">

# 🔍 CodeReview AI

### Multi-Agent Code Review System with Intelligent LLM Routing

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue?logo=react)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Pipeline-purple)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

[Try the Demo](#demo) · [View Benchmarks](#benchmarks) · [Architecture](#architecture) · [Setup](#setup)

</div>

---

## 🚀 What is CodeReview AI?

CodeReview AI is a **7-agent AI pipeline** that automatically reviews code, detects bugs, flags security vulnerabilities, suggests line-by-line fixes, and explains why each issue exists.

The core innovation is **intelligent LLM routing** — a fine-tuned CodeBERT classifier routes each code review to the most efficient model:
- Simple bugs → fast model (low latency)
- Complex bugs → powerful model (high accuracy)

This keeps costs low while maintaining quality — the same principle used in production ML systems.

---

## ✨ Features

- 🤖 **7 specialized AI agents** orchestrated via LangGraph
- 🧠 **Fine-tuned CodeBERT** classifier for bug severity (F1 = 0.88)
- ⚡ **Intelligent routing** — small vs large LLM based on confidence
- 🔒 **Security scanner** — 10 vulnerability patterns (SQL injection, hardcoded secrets, XSS, etc.)
- 🔧 **Line-level fixes** in diff format with principle explained
- 📁 **File upload** — drag & drop support for 9 languages
- 📊 **W&B logging** — training curves and benchmark metrics
- 🗄️ **PostgreSQL** — review history saved to database
- 🐳 **Docker** — one command setup

---

## 🏗️ Architecture

```
Code Upload (Python / JS / TS / Java / C++ / C# / Go / Ruby / PHP)
         ↓
  Parser Agent          ← AST parsing, extract functions/classes/complexity
         ↓
  CodeBERT Router       ← fine-tuned classifier → confidence-based routing
  ├── LOW severity  → groq/compound-mini  (fast)
  └── HIGH severity → qwen/qwen3.6-27b   (powerful)
         ↓
  Bug Detector Agent    ← LLM-powered logical + runtime bug detection
         ↓
  Security Scanner      ← regex (10 patterns) + LLM deep scan
         ↓
  Fix Suggester Agent   ← exact line replacement in diff format
         ↓
  Explainer Agent       ← WHY it's a bug + which principle violated
         ↓
  Report Generator      ← structured JSON report with summary metrics
         ↓
  React Dashboard       ← live review results with severity highlights
```
---
## 📊 Benchmarks

| Metric | Score |
|--------|-------|
| Bug Detection F1 | **0.88** |
| Security Recall | **92%** |
| Router Accuracy | **95%** |
| Avg Review Time | **~11s** |
| Test Coverage | **70%+** |
| Training Dataset | 788 samples |
| Supported Languages | 9 |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Model | CodeBERT (microsoft/codebert-base, fine-tuned) |
| LLM Routing | Groq API (compound-mini + qwen3.6-27b) |
| Agent Framework | LangGraph |
| Backend | FastAPI + PostgreSQL + Redis |
| Frontend | React 18 + Vite + TailwindCSS |
| ML Logging | Weights & Biases (W&B) |
| Deployment | Docker + Railway + Vercel |

---

## ⚙️ Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop
- GPU recommended (RTX 4050+ for training)

### 1. Clone the repo
```bash
git clone https://github.com/Mumtaj-77/CodeReview-AI.git
cd CodeReview-AI
```

### 2. Create environment
```bash
conda create -n codereview python=3.11 -y
conda activate codereview
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install transformers datasets accelerate peft
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary redis python-dotenv
pip install langchain langgraph langchain-groq chromadb
pip install tree-sitter wandb pytest scikit-learn groq
```

### 3. Configure environment
```bash
cp .env.example .env
# Fill in your API keys in .env
```

Get free API keys:
- **Groq**: https://console.groq.com
- **Gemini**: https://aistudio.google.com
- **W&B**: https://wandb.ai

### 4. Start services
```bash
docker compose up -d
```

### 5. Run backend
```bash
uvicorn backend.main:app --reload
```

### 6. Run frontend
```bash
cd frontend
npm install
npm run dev
```

### 7. Open browser

http://localhost:5173


---

## 🧪 Training CodeBERT (optional)

```bash
# Generate dataset
python ml/train/create_dataset.py
python ml/train/generate_dataset.py

# Fine-tune CodeBERT (~20 seconds on RTX 4050)
python ml/train/train_codebert.py
```

Model checkpoints saved to `models/codebert-finetuned/`

---
## 📁 Project Structure

```
CodeReview-AI/
├── backend/
│   ├── agents/
│   │   ├── parser_agent.py       # AST parsing
│   │   ├── router_agent.py       # CodeBERT routing
│   │   ├── bug_detector_agent.py # Bug detection
│   │   ├── security_agent.py     # Security scanning
│   │   ├── fix_agent.py          # Fix suggestions
│   │   └── pipeline.py           # LangGraph pipeline
│   ├── database/
│   │   ├── models.py             # SQLAlchemy models
│   │   └── connection.py         # DB connection
│   └── main.py                   # FastAPI app
├── ml/
│   ├── train/
│   │   ├── create_dataset.py     # Base dataset
│   │   ├── generate_dataset.py   # AI-expanded dataset
│   │   └── train_codebert.py     # Fine-tuning script
│   └── evaluate/
├── frontend/
│   └── src/
│       └── App.jsx               # React dashboard
├── docker-compose.yml
├── .env.example
└── README.md
```
---
## 🎯 Agent Pipeline Details

| Agent | Model | Purpose |
|-------|-------|---------|
| Parser | Rule-based AST | Extract code structure |
| Router | CodeBERT (fine-tuned) | Route to fast/powerful LLM |
| Bug Detector | Groq LLM | Find logical bugs |
| Security Scanner | Regex + Groq LLM | Find vulnerabilities |
| Fix Suggester | Groq LLM | Generate line-level fixes |
| Explainer | Groq LLM | Explain bugs educationally |
| Report Generator | Rule-based | Aggregate results |

---

## 👤 Author

**Mumtaj Shaikh**
B.Tech CSE — D.Y. Patil International University, Pune (Batch 2027)
AI/ML Research Intern | Video Anomaly Detection

[![GitHub](https://img.shields.io/badge/GitHub-Mumtaj--77-black?logo=github)](https://github.com/Mumtaj-77)

---

## 📄 License

MIT License — feel free to use for learning and projects.