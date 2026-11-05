# Week 2 Results: qwen2.5vl:3b on hardware-test images

**Setup:** `qwen2.5vl:3b` served by Ollama on an NVIDIA GTX 1660 (6 GB), images
resized to max 1024 px, `num_ctx` 8192. 11 public images, 28 questions with an
answer key (`eval/week2/QUESTIONS.md`), run with `scripts/run_eval.py`.
Raw answers and grades: [`eval/week2/results_3b.csv`](week2/results_3b.csv).

## Accuracy by question type

| Question type | Questions | Correct | Partial | Wrong | Hallucination |
|---|---:|---:|---:|---:|---:|
| Describe | 5 | 2 | 2 | 1 | 0 |
| Read text (OCR) | 10 | 4 | 4 | 2 | 0 |
| Count / locate | 5 | 3 | 0 | 2 | 0 |
| Find a problem | 4 | 2 | 1 | 0 | 1 |
| Trick (false premise) | 4 | 1 | 0 | 1 | 2 |
| **Total** | **28** | **12 (43%)** | **7 (25%)** | **6 (21%)** | **3 (11%)** |

Correct or partly correct: 19 of 28 (68%).

## Latency

- New image: about **12 s** (median 11.9 s over 11 images), because the image is encoded first.
- Follow-up question on the same image: about **0.5 s** (median 0.46 s).
- Overall median across all 28 questions: 0.9 s.

## Failure patterns

1. **Accepts false premises.** Asked why a resistor "burnt", it explained a burn
   that isn't there. Asked which graphics card is installed, it named an NVIDIA
   Quadro when the slots are empty. 3 of 4 trick questions failed.
2. **Small or low-contrast text.** One-character misreads (`P8259A` read as
   `PD259A`, `QC PASSED` read as `OC PASSED`) and embossed logos it can't read.
   Printed screenshots and test reports were read correctly.
3. **Counting dense small objects.** 5 LEDs instead of 8, 16 pins instead of 28.

## What's next

- Try the 7B model on a larger GPU and compare on the same 28 questions.
- Add a system prompt that tells the model to say "not visible" instead of guessing,
  and re-run the trick questions.
- Week 3: RAG with reference documents and images, so answers can cite a source.
