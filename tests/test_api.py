"""API tests with a fake backend, so they run without Ollama or a GPU."""
from fastapi.testclient import TestClient

from app.llm.base import VLMAnswer, VLMBackend
from app.main import app, get_backend


class FakeVLM(VLMBackend):
    def __init__(self):
        self.last_images: list[bytes] = []

    async def ask(self, question, images):
        self.last_images = images
        return VLMAnswer(text=f"echo: {question}", model="fake", latency_s=0.0)

    async def health(self):
        return True


fake = FakeVLM()
app.dependency_overrides[get_backend] = lambda: fake
client = TestClient(app)

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
