"""API tests with a fake backend, so they run without Ollama or a GPU."""
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app import config
from app.llm.base import VLMAnswer, VLMBackend
from app.main import app, get_backend


class FakeVLM(VLMBackend):
    def __init__(self):
        self.last_images: list[bytes] = []
        self.fail = False

    async def ask(self, question, images):
        if self.fail:
            raise httpx.ConnectError("ollama down")
        self.last_images = images
        return VLMAnswer(text=f"echo: {question}", model="fake", latency_s=0.0)

    async def health(self):
        return True


fake = FakeVLM()
app.dependency_overrides[get_backend] = lambda: fake
client = TestClient(app)

@pytest.fixture(autouse=True)
def request_log(tmp_path, monkeypatch):
    """Send the request log to a temp file so tests never touch logs/."""
    path = tmp_path / "requests.jsonl"
    monkeypatch.setattr(config, "REQUEST_LOG_PATH", str(path))
    fake.fail = False
    return path


def read_log(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082"
)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["llm_reachable"] is True


def test_ask_text_only():
    r = client.post("/ask", data={"question": "hello"})
    assert r.status_code == 200
    assert r.json()["answer"] == "echo: hello"
    assert fake.last_images == []


def test_ask_with_image():
    r = client.post(
        "/ask",
        data={"question": "what is this?"},
        files={"image": ("x.png", PNG_1PX, "image/png")},
    )
    assert r.status_code == 200
    assert fake.last_images == [PNG_1PX]


def test_rejects_wrong_file_type():
    r = client.post(
        "/ask",
        data={"question": "?"},
        files={"image": ("x.txt", b"not an image", "text/plain")},
    )
    assert r.status_code == 415


def test_rejects_empty_question():
    r = client.post("/ask", data={"question": ""})
    assert r.status_code == 422


def test_ask_is_logged_without_image_bytes(request_log):
    client.post(
        "/ask",
        data={"question": "what is this?"},
        files={"image": ("board.png", PNG_1PX, "image/png")},
    )
    [record] = read_log(request_log)
    assert record["question"] == "what is this?"
    assert record["answer"] == "echo: what is this?"
    assert record["image_name"] == "board.png"
    assert record["image_kb"] == round(len(PNG_1PX) / 1024, 1)
    assert record["error"] is None
    assert "image" not in record  # never store the image itself


def test_backend_error_is_logged(request_log):
    fake.fail = True
    r = client.post("/ask", data={"question": "hello"})
    assert r.status_code == 502
    [record] = read_log(request_log)
    assert record["answer"] is None
    assert "ollama down" in record["error"]


def test_logging_can_be_disabled(request_log, monkeypatch):
    monkeypatch.setattr(config, "REQUEST_LOG_PATH", "")
    client.post("/ask", data={"question": "hello"})
    assert not request_log.exists()
