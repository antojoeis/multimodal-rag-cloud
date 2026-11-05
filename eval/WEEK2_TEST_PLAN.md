# Week 2: Test Plan for the Vision Model

Goal: find out **where `qwen2.5vl:3b` is good and where it fails** on real
hardware-testing images, with numbers. These results become the test set for
Week 3 (RAG) and the baseline for comparing Bedrock in Week 5.

## Rules

- Keep work images in `data/` on the machine you test from. `data/` is in
  `.gitignore`, and **images never go to GitHub**.
- Write findings in your own words. Describe the image ("board photo, connector
  J3 half-inserted") instead of sharing it.
- Ask each question through the web UI or `/docs`. Every request is logged
  automatically to `logs/requests.jsonl` on the device.

## What to test: 10 images × 2–3 questions

Pick images that cover different types:

| # | Image type | Example |
|---|---|---|
| 1–3 | Board / hardware photos | PCB, connectors, cables, LEDs |
| 4–5 | Screenshots of test tools | test result window, BIOS screen, error dialog |
| 6–7 | Logs or terminal output | serial log, `dmesg`, a failing test log |
| 8 | Labels / text close-up | serial number sticker, chip marking |
| 9 | Charts or diagrams | waveform, block diagram, table |
| 10 | Something tricky | blurry, dark, rotated, or very busy photo |

For each image, ask from these question types:

| Type | Example question | What it tests |
|---|---|---|
| **Describe** | "What is in this image?" | General understanding |
| **Read text (OCR)** | "What is the serial number?" | Small text reading |
| **Find a problem** | "Is anything wrong or failing here?" | Reasoning, defect spotting |
| **Count / locate** | "How many LEDs are on?" | Precision |
| **Trick question** | "Why is the red LED on?" when no red LED is on | **Hallucination**: does it invent things? |

The trick question matters most. A model that confidently describes
something that isn't there is dangerous in test automation.

## How to grade

After testing, generate the grading sheet (see below) and fill in `grade`:

| Grade | Meaning |
|---|---|
| `correct` | Right and useful |
| `partial` | Partly right, or right but vague |
| `wrong` | Wrong answer |
| `hallucination` | Confidently made something up |

Add a short `note` for anything other than `correct`, e.g.
"misread 8 as B in serial number", "didn't notice bent pin".

## Generate the report

On the device:

```bash
cd ~/multimodal-rag-cloud
.venv/bin/python scripts/log_report.py --since 2026-11-05 --csv eval/week2_results.csv
```

- Prints a summary: number of requests, latency (average and p95), errors,
  how many images were resized.
- Writes `eval/week2_results.csv` with empty `grade` and `note` columns. It
  contains your questions and answers about work images, so it stays local
  (ignored by git). Only the summary in `WEEK2_RESULTS.md` goes to GitHub.
  Open it in Excel, fill them in, then run again with `--graded` to get accuracy:

```bash
.venv/bin/python scripts/log_report.py --graded eval/week2_results.csv
```

## Write-up (end of Week 2)

Fill in `eval/WEEK2_RESULTS.md`, in your own words:

1. Accuracy per question type (describe / OCR / problem / count / trick)
2. Latency: first request (cold) vs. the rest
3. Top 3 failure patterns, with one example each (described, not the image)
4. What you'd try next: bigger model (7B), better prompts, or RAG with reference images

This becomes your interview story: "I evaluated a 3B VLM on N real
hardware images; it reached X% on descriptions but only Y% on small text, so..."
