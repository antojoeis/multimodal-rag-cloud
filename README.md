# Multimodal RAG on Cloud

Ask questions about images and documents together. Upload a PDF, a screenshot, or a photo of a device, and get grounded answers from a vision-language model, deployed on AWS with full infrastructure-as-code and CI/CD.

The same app runs in two modes, so you can compare them:

| Mode | Model | Where it runs |
|---|---|---|
| Self-hosted | Qwen2.5-VL via Ollama | Local GPU / EC2 GPU instance |
| Managed | Amazon Bedrock (multimodal model) | Fully managed |

> **Why this project:** I've built on-premise LLM pipelines in production (Ollama + GPU edge servers). This repo shows the same skills on the cloud, plus a measured comparison of cost, latency and quality between self-hosted and managed inference.

---

## Architecture

```
            ┌──────────────┐
 User ───►  │  Web UI      │
            └──────┬───────┘
                   │ REST
            ┌──────▼───────┐        ┌──────────────────┐
            │  API (FastAPI)│──────►│  S3 (raw files)   │
            └──┬────────┬──┘        └──────────────────┘
     ingest    │        │  query
   ┌───────────▼──┐  ┌──▼─────────────────────┐
   │ Embeddings   │  │ Retriever (top-k text   │
   │ text + CLIP  │  │ + image chunks)         │
   └──────┬───────┘  └──┬─────────────────────┘
          │             │
   ┌──────▼─────────────▼──┐     ┌─────────────────────────┐
   │ PostgreSQL + pgvector  │     │ VLM: Ollama  OR Bedrock │
   └────────────────────────┘     └─────────────────────────┘
```

**Flow:**
1. **Ingest:** files go to S3; PDFs are split into text chunks and page images; images get CLIP embeddings, text gets text embeddings; all are stored in pgvector.
2. **Query:** the question is embedded, the top-k text and image chunks are retrieved, then sent to the VLM with the question.
3. **Answer:** the response comes back with citations to the source page or image.

---

## Tech stack

- **API:** Python, FastAPI, Pydantic
- **Models:** Qwen2.5-VL (Ollama), Amazon Bedrock, CLIP / sentence-transformers, Whisper (optional voice input)
- **Data:** PostgreSQL + pgvector, Amazon S3
- **Infra:** Docker, Terraform, Amazon ECS (Fargate) → EKS (stretch goal)
- **CI/CD:** GitHub Actions (lint, test, build, push to ECR, deploy)
- **Security:** Syft SBOM + vulnerability scan in CI, IAM least privilege, Secrets Manager

---

## Repo structure

```
multimodal-rag-cloud/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── ingest.py            # file upload, chunking, embedding
│   ├── retrieve.py          # vector search (text + image)
│   ├── llm/
│   │   ├── base.py          # common interface
│   │   ├── ollama_vlm.py    # self-hosted backend
│   │   └── bedrock_vlm.py   # managed backend
│   └── db.py                # pgvector access
├── ui/                      # simple web front end
├── infra/
│   ├── terraform/
│   │   ├── main.tf          # VPC, ECS, RDS, S3, IAM
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── k8s/                 # EKS manifests (stretch goal)
├── tests/
├── benchmarks/
│   └── compare.py           # latency / cost / quality: Ollama vs Bedrock
├── .github/workflows/
│   └── ci.yml
├── docker-compose.yml       # run everything locally
├── Dockerfile
└── README.md
```

---

## Quick start (local)

```bash
git clone https://github.com/<your-username>/multimodal-rag-cloud.git
cd multimodal-rag-cloud
ollama pull qwen2.5vl
docker compose up --build
# open http://localhost:8000/docs
```

## Deploy to AWS

```bash
cd infra/terraform
terraform init
terraform apply -var="llm_backend=bedrock"
```

> Set an AWS billing alarm before deploying. Run `terraform destroy` when you're done testing.

---

## Results

| Metric | Ollama (self-hosted) | Bedrock (managed) |
|---|---|---|
| Median latency (s) | TODO | TODO |
| Cost per 1,000 queries (USD) | TODO | TODO |
| Answer accuracy on test set | TODO | TODO |

**Takeaways:** TODO (when to self-host vs. use a managed service)

---

## Roadmap

- [ ] **Week 1–2:** Local MVP: FastAPI + Ollama VLM, upload an image and ask a question
- [ ] **Week 3:** Multimodal RAG: pgvector, CLIP image embeddings, PDF ingestion, citations
- [ ] **Week 4:** Docker Compose for the full stack; unit tests
- [ ] **Week 5:** AWS basics: S3 storage, Bedrock backend behind the same interface
- [ ] **Week 6:** Terraform: VPC, ECS Fargate, RDS Postgres, IAM, Secrets Manager
- [ ] **Week 7:** GitHub Actions: test → build → push to ECR → deploy; Syft SBOM scan
- [ ] **Week 8:** Benchmarks and write-up; fill in the Results table
- [ ] **Stretch:** EKS deployment, Whisper voice input, GPU instance for self-hosted mode

---

## License

MIT
