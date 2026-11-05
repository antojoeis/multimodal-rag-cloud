# Multimodal RAG on Cloud

Ask questions about images of hardware (boards, connectors, test screens, logs) and get answers from a vision-language model (VLM). The goal is a multimodal RAG system deployed on AWS, with a measured comparison of a **self-hosted** model (Ollama on a GPU) against a **managed** one (Amazon Bedrock).

> **Why this project:** I've built on-premise LLM pipelines in production (Ollama + GPU edge servers). This repo shows the same skills on the cloud, with numbers for cost, latency and quality.

## Current status

| Part | Status |
|---|---|
| FastAPI service: upload an image and ask a question | ✅ Done |
| Self-hosted VLM: `qwen2.5vl:3b` on Ollama, GTX 1660 6 GB | ✅ Done |
| Image resizing (≤1024 px) and an 8K context window to prevent truncated, garbage answers | ✅ Done |
| Request logging (JSONL) and a latency report | ✅ Done |
| Evaluation: 11 public images, 28 questions with an answer key | ✅ Done |
| Unit tests (pytest, 15 tests, no GPU needed) | ✅ Done |
| RAG: embeddings, vector DB, citations | ⏳ Week 3 |
| AWS: Bedrock, S3, Terraform, CI/CD | ⏳ Weeks 4–7 |

## First results (Week 2 baseline, `qwen2.5vl:3b`)

| Question type | Correct |
|---|---|
| Count | 3 / 5 |
| Describe | 2 / 5 |
| Read text (OCR) | 4 / 10 |
| Find a problem | 2 / 4 |
| Trick (hallucination test) | 1 / 4 |
| **Total** | **12 / 28 (43%)**: 7 partial, 6 wrong, 3 hallucinations |

Latency: about 12 s for a new image and about 0.5 s (median) for a follow-up question on the same image.
Details: [eval/week2/](eval/week2/) · test plan: [eval/WEEK2_TEST_PLAN.md](eval/WEEK2_TEST_PLAN.md)

## Tech stack

**Now:** Python, FastAPI, Pydantic, Ollama, Qwen2.5-VL 3B, Pillow, httpx, pytest
**Planned:** pgvector, CLIP / sentence-transformers, Amazon Bedrock, S3, Docker, Terraform, ECS Fargate, GitHub Actions

## Repo structure

```
multimodal-rag-cloud/
├── app/
│   ├── main.py            # API: POST /ask, GET /health
│   ├── config.py          # settings from env / .env
│   ├── image_utils.py     # validate, fix rotation, resize
│   ├── request_log.py     # JSONL request log
│   └── llm/
│       ├── base.py        # common VLM interface
│       └── ollama_vlm.py  # self-hosted backend
├── tests/                 # pytest, uses a fake model
├── scripts/
│   ├── run_eval.py        # run the question set against the API
│   └── log_report.py      # latency summary + accuracy from graded CSV
├── eval/                  # test plan, images, questions, results
├── DEVICE_SETUP.md        # GPU device: SSH, NVIDIA driver, Ollama
└── GIT_MANUAL.md
```

## Quick start

Needs Python 3.11+ and [Ollama](https://ollama.com). An NVIDIA GPU with 6 GB or more is recommended.

```bash
git clone https://github.com/antojoeis/multimodal-rag-cloud.git
cd multimodal-rag-cloud
ollama pull qwen2.5vl:3b

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

uvicorn app.main:app --host 0.0.0.0 --port 8000
# open http://localhost:8000/docs
```

Run tests: `pytest`
Run the evaluation: `python scripts/run_eval.py --api http://localhost:8000`

## Target architecture

```
 User ──► Web UI ──► API (FastAPI) ──► S3 (raw files)
                       │       │
                ingest │       │ query
                       ▼       ▼
          Embeddings (text + CLIP) ──► PostgreSQL + pgvector
                                              │ top-k chunks
                                              ▼
                              VLM: Ollama (self-hosted) OR Bedrock (managed)
```

## Roadmap

- [x] **Week 1:** FastAPI + Ollama VLM MVP; GPU test device setup
- [x] **Week 2:** Evaluation set, request logging, baseline results
- [ ] **Week 3:** Multimodal RAG: pgvector, CLIP image embeddings, PDF ingestion, citations
- [ ] **Week 4:** Docker Compose for the full stack
- [ ] **Week 5:** Bedrock backend behind the same interface; S3 storage
- [ ] **Week 6:** Terraform: VPC, ECS Fargate, RDS Postgres, IAM
- [ ] **Week 7:** GitHub Actions: test, build, push to ECR, deploy
- [ ] **Week 8:** Benchmark Ollama vs. Bedrock (latency, cost, accuracy) and write up

## License

MIT
