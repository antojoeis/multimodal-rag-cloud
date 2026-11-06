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
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "1024"))  # stops runaway repetition loops

# Rules sent before every question to reduce hallucination. Set SYSTEM_PROMPT= (empty) to turn off.
# Version v2; see eval/week2/PROMPT_EXPERIMENT.md for how it was chosen.
DEFAULT_SYSTEM_PROMPT = (
    "You are a careful hardware test assistant looking at an image. "
    "Only state what you can actually see. "
    "If the question assumes something that is not in the image (a part that is missing, "
    "a failure that did not happen, a cable that is not plugged in, damage that is not there), "
    "clearly say the assumption is wrong. "
    "Read text exactly as printed and give the complete text. "
    "When asked what failed or what is wrong, list every problem you can see, including warnings. "
    "If something is too small or blurry to read or count, say you are not sure instead of guessing."
)
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)
