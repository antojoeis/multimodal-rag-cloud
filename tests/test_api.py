"""API tests with a fake backend, so they run without Ollama or a GPU."""
import io
import json

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

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


def _tiny_png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (1, 1), "white").save(buf, format="PNG")
    return buf.getvalue()


PNG_1PX = _tiny_png()


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


def test_large_image_is_resized_before_the_model(request_log):
    buf = io.BytesIO()
    Image.new("RGB", (4032, 3024), "blue").save(buf, format="JPEG")
    r = client.post(
        "/ask",
        data={"question": "what color?"},
        files={"image": ("photo.jpg", buf.getvalue(), "image/jpeg")},
    )
    assert r.status_code == 200
    [sent] = fake.last_images
    assert Image.open(io.BytesIO(sent)).size == (1024, 768)
    [record] = read_log(request_log)
    assert record["image_px"] == "4032x3024->1024x768"


def test_corrupt_image_returns_400():
    r = client.post(
        "/ask",
        data={"question": "?"},
        files={"image": ("broken.jpg", b"not really a jpeg", "image/jpeg")},
    )
    assert r.status_code == 400
