"""Self-hosted backend: Qwen2.5-VL (or any vision model) served by Ollama."""
import base64
import time

import httpx

from app import config
from app.llm.base import VLMAnswer, VLMBackend


class OllamaVLM(VLMBackend):
    def __init__(self, base_url: str = config.OLLAMA_URL, model: str = config.VLM_MODEL,
                 system_prompt: str = config.SYSTEM_PROMPT):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.system_prompt = system_prompt

    def build_messages(self, question: str, images: list[bytes]) -> list[dict]:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({
            "role": "user",
            "content": question,
            "images": [base64.b64encode(img).decode() for img in images],
        })
        return messages

    async def ask(self, question: str, images: list[bytes]) -> VLMAnswer:
        payload = {
            "model": self.model,
            "stream": False,
            "options": {"num_ctx": config.OLLAMA_NUM_CTX, "num_predict": config.MAX_OUTPUT_TOKENS},
            "messages": self.build_messages(question, images),
        }
        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT_S) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
        data = resp.json()
        return VLMAnswer(
            text=data["message"]["content"],
            model=self.model,
            latency_s=round(time.perf_counter() - start, 3),
        )

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False
