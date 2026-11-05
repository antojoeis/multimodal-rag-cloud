# Multimodal RAG on Cloud

![CI](https://github.com/antojoeis/multimodal-rag-cloud/actions/workflows/ci.yml/badge.svg)

Ask questions about images and documents together. Upload a PDF, a screenshot,
or a photo of a device, and get grounded answers from a vision-language model.
It runs locally on a GPU with Ollama today; the cloud version (AWS, Terraform,
CI/CD) is being built week by week.

**Why this project:** I've built on-premise LLM pipelines in production (Ollama +
GPU edge servers for hardware-test automation). This repo applies the same
skills to vision-language models, evaluates them honestly on real hardware
images, and then moves them to the cloud with a measured comparison of cost,
latency and quality between self-hosted and managed inference.

## Status

| Part | State |
|---|---|
| FastAPI service: upload an image, ask a question, get an answer (`/ask`, `/health`) | Done |
| Self-hosted VLM backend (Qwen2.5-VL via Ollama), image resizing, request logging | Done |
| Evaluation: 28-question test set on 12 hardware images, automated runner, graded results | Done ([results](eval/WEEK2_RESULTS.md)) |
| Unit tests, Dockerfile, Docker Compose, GitHub Actions CI | Done |
| Multimodal RAG: pgvector, CLIP image embeddings, PDF ingestion, citations | Next (Week 3) |
| Managed backend (Amazon Bedrock), S3, Terraform, deploy pipeline | Planned (Weeks 5–7) |
| Self-hosted vs. managed benchmark | Planned (Week 8) |

## First results (Week 2)

`qwen2.5vl:3b` on a GTX 1660 (6 GB), 28 questions about PCB photos, connectors,
oscilloscope screens and test reports:

| Metric | Result |
|---|---|
| Correct | 12 / 28 (43%) |
| Correct or partly correct | 19 / 28 (68%) |
| Hallucinations on false-premise ("trick") questions | 2 of 4, plus 1 wrong |
| Median latency | 0.9 s (first request after model load: 14 s) |

Main findings: printed screenshots and test reports are read well; small or
embossed text, dense counting and false-premise questions are weak spots. The
full write-up with failure patterns is in [eval/WEEK2_RESULTS.md](eval/WEEK2_RESULTS.md).

## Architecture (target)

```
                 ┌──────────────┐
      User ───►  │    Web UI    │
                 └──────┬───────┘
                        │ REST
                 ┌──────▼───────┐       ┌──────────────────┐
                 │ API (FastAPI)│──────►│  S3 (raw files)  │
                 └──┬────────┬──┘       └──────────────────┘
             ingest │        │ query
        ┌───────────▼──┐  ┌──▼─────────────────────┐
        │ Embeddings   │  │ Retriever (top-k text   │
        │ text + CLIP  │  │ + image chunks)         │
        └──────┬───────┘  └──┬─────────────────────┘
               │             │
        ┌──────▼─────────────▼──┐   ┌─────────────────────────┐
        │ PostgreSQL + pgvector  │   │ VLM: Ollama OR Bedrock  │
        └────────────────────────┘   └─────────────────────────┘
```

Today the API sends the question and image straight to the VLM. Retrieval,
storage and the Bedrock backend are added in the coming weeks behind the same
`VLMBackend` interface (`app/llm/base.py`).

## Tech stack

- **Now:** Python, FastAPI, Pydantic, httpx, Pillow, Ollama (Qwen2.5-VL), pytest, Docker, GitHub Actions
- **Planned:** PostgreSQL + pgvector, CLIP / sentence-transformers, Amazon Bedrock, S3, Terraform, ECS Fargate, Syft SBOM scan in CI

## Repo structure

```
multimodal-rag-cloud/
├── app/
│   ├── main.py          # FastAPI: /ask and /health
│   ├── config.py        # settings from environment / .env
│   ├── image_utils.py   # validate and resize images before the VLM
│   ├── request_log.py   # JSONL log of every request
│   └── llm/
│       ├── base.py      # common backend interface
│       └── ollama_vlm.py
├── eval/
│   ├── WEEK2_TEST_PLAN.md
│   ├── WEEK2_RESULTS.md
│   └── week2/           # public test images, questions with answer key, results CSV
├── scripts/
│   ├── run_eval.py      # run the question set against the API
│   └── log_report.py    # latency / error summary from the request log
├── tests/
├── DEVICE_SETUP.md      # Ubuntu + NVIDIA GPU test machine setup
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Quick start

With Docker (API + Ollama):

```bash
git clone https://github.com/antojoeis/multimodal-rag-cloud.git
cd multimodal-rag-cloud
docker compose up --build -d
docker compose exec ollama ollama pull qwen2.5vl:3b
# open http://localhost:8000/docs
```

Without Docker (Ollama already installed):

```bash
ollama pull qwen2.5vl:3b
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # set VLM_MODEL=qwen2.5vl:3b for a 6 GB GPU
uvicorn app.main:app --reload
```

Run the tests: `python -m pytest -q`

Re-run the evaluation: `python scripts/run_eval.py --api http://localhost:8000 --out eval/week2/results_3b.csv`

## Roadmap

- [x] Week 1: FastAPI + Ollama VLM MVP
- [x] Week 2: evaluation set, automated runner and first results for the 3B model
- [ ] Week 3: multimodal RAG: pgvector, CLIP image embeddings, PDF ingestion, citations
- [ ] Week 4: full stack in Docker Compose (Postgres added)
- [ ] Week 5: AWS basics: S3 storage, Bedrock backend behind the same interface
- [ ] Week 6: Terraform: VPC, ECS Fargate, RDS Postgres, IAM, Secrets Manager
- [ ] Week 7: CI/CD: build → push to ECR → deploy; Syft SBOM scan
- [ ] Week 8: self-hosted vs. managed benchmark (latency, cost, accuracy) and write-up
- Stretch: EKS, Whisper voice input, GPU instance for self-hosted mode

## License

MIT
