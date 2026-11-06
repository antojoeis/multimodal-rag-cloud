"""App settings, read from environment variables (or a .env file)."""
import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
VLM_MODEL = os.getenv("VLM_MODEL", "qwen2.5vl:3b")
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")  # "ollama" now, "bedrock" in Week 5
REQUEST_TIMEOUT_S = float(os.getenv("REQUEST_TIMEOUT_S", "120"))
MAX_IMAGE_MB = float(os.getenv("MAX_IMAGE_MB", "10"))
REQUEST_LOG_PATH = os.getenv("REQUEST_LOG_PATH", "logs/requests.jsonl")  # empty = off
MAX_IMAGE_SIDE_PX = int(os.getenv("MAX_IMAGE_SIDE_PX", "1024"))  # ~1000 image tokens
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))  # Ollama's default 4096 is too small for images

# Rules sent before every question to reduce hallucination. Set SYSTEM_PROMPT= (empty) to turn off.
DEFAULT_SYSTEM_PROMPT = (
    "You are a careful hardware test assistant looking at an image. "
    "Only state what you can actually see in the image. "
    "If the question assumes something that is not in the image (a part that is not there, "
    "a failure that did not happen, a cable that is not plugged in), say so instead of going along with it. "
    "If text is too small or blurry to read, or you cannot count something reliably, say you are not sure. "
    "Never guess brand names, model numbers or values. Keep answers short."
)
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)
