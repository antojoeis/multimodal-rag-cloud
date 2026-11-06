from app.llm.ollama_vlm import OllamaVLM


def test_system_prompt_sent_first():
    vlm = OllamaVLM(system_prompt="Only describe what you see.")
    messages = vlm.build_messages("What is this?", [b"img"])
    assert messages[0] == {"role": "system", "content": "Only describe what you see."}
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "What is this?"
    assert messages[1]["images"] == ["aW1n"]  # base64 of b"img"


def test_empty_system_prompt_is_skipped():
    messages = OllamaVLM(system_prompt="").build_messages("What is this?", [])
    assert [m["role"] for m in messages] == ["user"]
