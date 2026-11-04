"""Week 1 MVP: upload an image, ask a question, get an answer from a VLM.

Run:  uvicorn app.main:app --reload
Docs: http://localhost:8000/docs
"""
import httpx
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app import config
from app.llm.base import VLMBackend
from app.llm.ollama_vlm import OllamaVLM
from app.request_log import log_request

app = FastAPI(title="Multimodal RAG on Cloud", version="0.1.0")

ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp"}


def get_backend() -> VLMBackend:
    if config.LLM_BACKEND == "ollama":
        return OllamaVLM()
    raise RuntimeError(f"Unknown LLM_BACKEND: {config.LLM_BACKEND}")


class AskResponse(BaseModel):
    answer: str
    model: str
    latency_s: float


@app.get("/health")
async def health(backend: VLMBackend = Depends(get_backend)):
    ok = await backend.health()
    return {"status": "ok" if ok else "degraded", "llm_backend": config.LLM_BACKEND, "llm_reachable": ok}


@app.post("/ask", response_model=AskResponse)
async def ask(
    question: str = Form(..., min_length=1, max_length=2000),
    image: UploadFile | None = File(None),
    backend: VLMBackend = Depends(get_backend),
):
    images: list[bytes] = []
    image_name = image_kb = None
    if image is not None and image.filename:
        if image.content_type not in ALLOWED_TYPES:
            raise HTTPException(415, f"Unsupported image type: {image.content_type}")
        data = await image.read()
        if len(data) > config.MAX_IMAGE_MB * 1024 * 1024:
            raise HTTPException(413, f"Image larger than {config.MAX_IMAGE_MB} MB")
        images.append(data)
        image_name, image_kb = image.filename, round(len(data) / 1024, 1)

    try:
        result = await backend.ask(question, images)
    except httpx.HTTPError as exc:
        log_request(question, None, config.VLM_MODEL, None, image_name, image_kb, error=str(exc))
        raise HTTPException(502, f"LLM backend error: {exc}") from exc

    log_request(question, result.text, result.model, result.latency_s, image_name, image_kb)
    return AskResponse(answer=result.text, model=result.model, latency_s=result.latency_s)
