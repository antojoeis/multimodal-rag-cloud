"""App settings, read from environment variables (or a .env file)."""
import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
VLM_MODEL = os.getenv("VLM_MODEL", "qwen2.5vl:7b")
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")  # "ollama" now, "bedrock" in Week 5
REQUEST_TIMEOUT_S = float(os.getenv("REQUEST_TIMEOUT_S", "120"))
MAX_IMAGE_MB = float(os.getenv("MAX_IMAGE_MB", "10"))
