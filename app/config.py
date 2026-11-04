"""App settings, read from environment variables (or a .env file)."""
import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
VLM_MODEL = os.getenv("VLM_MODEL", "qwen2.5vl:7b")
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")  # "ollama" now, "bedrock" in Week 5
REQUEST_TIMEOUT_S = float(os.getenv("REQUEST_TIMEOUT_S", "120"))
MAX_IMAGE_MB = float(os.getenv("MAX_IMAGE_MB", "10"))
REQUEST_LOG_PATH = os.getenv("REQUEST_LOG_PATH", "logs/requests.jsonl")  # empty = off
MAX_IMAGE_SIDE_PX = int(os.getenv("MAX_IMAGE_SIDE_PX", "1024"))  # ~1000 image tokens
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))  # Ollama's default 4096 is too small for images
