# Experiment: does a system prompt reduce hallucination?

**Model:** `qwen2.5vl:3b` on Ollama, GTX 1660 6 GB. Same 11 images and 28
questions as the baseline (`QUESTIONS.md`), same grading rules.

A **system prompt** is an instruction sent before every user question. It
changes the model's behaviour without retraining.

## Prompts tested

| Run | System prompt | File |
|---|---|---|
| Baseline | none | `results_3b.csv` |
| v1 | "Only state what you see. If the question assumes something that isn't there, say so. If unsure, say so. Never guess brand names or values. **Keep answers short.**" | `results_3b_sysprompt.csv` |
| v2 | Same anti-hallucination rules, without "keep answers short". Adds: "Read text exactly as printed and give the complete text. When asked what failed, list every problem, including warnings." | `results_3b_sysprompt_v2.csv` |

The full v2 text is `DEFAULT_SYSTEM_PROMPT` in `app/config.py`.

## Results (correct answers)

| Question type | Baseline | v1 | v2 |
|---|---:|---:|---:|
| Trick (false premise) | 1/4 | **3/4** | **3/4** |
| Find a problem | 2/4 | 1/4 | 2/4 |
| Count | 3/5 | 2/5 | 2/5 |
| Describe | 2/5 | 2/5 | 2/5 |
| Read text (OCR) | 4/10 | 4/10 | 4/10 |
| **Total correct** | **12/28** | **12/28** | **13/28** |
| **Hallucinations** | **3** | **2** | **1** |

## What changed

- **False premises are mostly fixed.** With the system prompt, the model said
  "the graphics card is not visible" instead of inventing an NVIDIA Quadro, and
  "the memory test passed with 0 errors" instead of explaining a failure that
  never happened. With v2, it no longer claims the empty power connector is
  "properly seated".
- **"Keep answers short" backfired (v1).** The model dropped facts: chip text
  shrank to just "MEXICO", it missed the USB3 warning, and the 24-pin connector
  became "12 pins". v2 removed that rule and recovered most of these.
- **Still failing:** "Why is R106 burnt?" ("R106 is burnt."), small or embossed
  text (`OC PASSED`, `TDP`), counting dense objects (8 LEDs, 28 pins). A prompt
  can't fix what the model can't see. That needs a bigger model, higher
  resolution or reference images (RAG, Week 3).
- **New bug found:** in v2, question #9 got stuck in a repetition loop (400+
  lines, 108 s). Fixed by capping output length (`MAX_OUTPUT_TOKENS=1024`,
  Ollama `num_predict`).

## Caveats

- One run per prompt. Answers can vary between runs, so a difference of one
  question is within noise. The drop in hallucinations (3 → 1) and in trick
  failures is the clear signal.
- The "not sure" instruction was never used. The model still prefers a
  confident answer over admitting uncertainty.

## Decision

v2 is the new default. Turn it off with `SYSTEM_PROMPT=` (empty) in `.env` to
reproduce the baseline.
