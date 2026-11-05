"""Run the Week 2 question set against the API and save answers for grading.

Reads the table in eval/week2/QUESTIONS.md, sends each question with its image
to POST /ask, and writes a CSV with the expected and actual answers side by side.

Examples:
  python scripts/run_eval.py --api http://localhost:8000
  python scripts/run_eval.py --api http://<device-ip>:8000 --out eval/week2/results_3b.csv
"""
import argparse
import csv
import mimetypes
import re
import time
from pathlib import Path

import httpx

ROW = re.compile(r"^\| (\d+) \| (\S+) \| (\w+) \| (.+?) \| (.+?) \|$")
FIELDS = ["id", "image", "question_type", "question", "expected", "answer",
          "latency_s", "error", "grade", "note"]


def load_questions(path: Path) -> list[dict]:
    questions = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line.strip())
        if m:
            qid, image, qtype, question, expected = m.groups()
            questions.append({"id": int(qid), "image": image, "question_type": qtype,
                              "question": question, "expected": expected})
    return questions


def ask(client: httpx.Client, api: str, question: str, image: Path) -> dict:
    mime = mimetypes.guess_type(image.name)[0] or "image/jpeg"
    with image.open("rb") as f:
        resp = client.post(f"{api}/ask", data={"question": question},
                           files={"image": (image.name, f, mime)})
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--questions", type=Path, default=Path("eval/week2/QUESTIONS.md"))
    parser.add_argument("--images", type=Path, default=Path("eval/week2/images"))
    parser.add_argument("--out", type=Path, default=Path("eval/week2/results.csv"))
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args()

    questions = load_questions(args.questions)
    print(f"{len(questions)} questions -> {args.api}\n")
    rows = []
    with httpx.Client(timeout=args.timeout) as client:
        for q in questions:
            row = {**q, "answer": "", "latency_s": "", "error": "", "grade": "", "note": ""}
            start = time.perf_counter()
            try:
                result = ask(client, args.api, q["question"], args.images / q["image"])
                row["answer"], row["latency_s"] = result["answer"].strip(), result["latency_s"]
            except (httpx.HTTPError, OSError) as exc:
                row["error"] = str(exc)
            took = time.perf_counter() - start
            short = (row["answer"] or "ERROR: " + row["error"]).replace("\n", " ")[:70]
            print(f"#{q['id']:<3} {took:5.1f}s  {q['question'][:40]:<40}  {short}")
            rows.append(row)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved {len(rows)} results to {args.out}. Fill in 'grade', then run:")
    print(f"  python scripts/log_report.py --graded {args.out}")


if __name__ == "__main__":
    main()
