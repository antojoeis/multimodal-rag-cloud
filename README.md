# Multimodal RAG on Cloud

![CI](https://github.com/antojoeis/multimodal-rag-cloud/actions/workflows/ci.yml/badge.svg)

Ask questions about images of hardware (boards, connectors, test screens, logs) and get answers from a vision-language model (VLM). The goal is a multimodal RAG system deployed on AWS, with a measured comparison of a **self-hosted** model (Ollama on a GPU) against a **managed** one (Amazon Bedrock).

> **Why this project:** I've built on-premise LLM pipelines in production (Ollama + GPU edge servers). This repo shows the same skills on the cloud, with numbers for cost, latency and quality.

## Tech stack

**Now:** Python, FastAPI, Pydantic, Ollama, Qwen2.5-VL 3B, Pillow, httpx, pytest, Docker, GitHub Actions
**Planned:** pgvector, CLIP / sentence-transformers, Amazon Bedrock, S3, Terraform, ECS Fargate

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
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml     # API + Ollama (GPU)
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

With Docker instead (API + Ollama; GPU needs the NVIDIA Container Toolkit):

```bash
docker compose up --build -d
docker compose exec ollama ollama pull qwen2.5vl:3b
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
- [ ] **Week 4:** Docker Compose for the full stack (API + Ollama done; Postgres next)
- [ ] **Week 5:** Bedrock backend behind the same interface; S3 storage
- [ ] **Week 6:** Terraform: VPC, ECS Fargate, RDS Postgres, IAM
- [ ] **Week 7:** GitHub Actions: test, build, push to ECR, deploy
- [ ] **Week 8:** Benchmark Ollama vs. Bedrock (latency, cost, accuracy) and write up

## License

MIT
