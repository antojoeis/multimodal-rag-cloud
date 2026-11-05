"""Summarise logs/requests.jsonl and build a grading sheet for Week 2.

Examples:
  python scripts/log_report.py
  python scripts/log_report.py --since 2026-11-05 --csv eval/week2_results.csv
  python scripts/log_report.py --graded eval/week2_results.csv
"""
import argparse
import csv
import json
import statistics
from collections import Counter
from pathlib import Path

GRADES = ("correct", "partial", "wrong", "hallucination")
CSV_FIELDS = ["time", "image_name", "image_px", "question", "answer", "latency_s", "error",
              "question_type", "grade", "note"]


def load_log(path: Path, since: str | None) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if since and rec["time"] < since:
            continue
        records.append(rec)
    return records


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    k = max(0, min(len(ordered) - 1, round(pct / 100 * (len(ordered) - 1))))
    return ordered[k]


def summarise(records: list[dict]) -> None:
    ok = [r for r in records if not r.get("error")]
    latencies = [r["latency_s"] for r in ok if r.get("latency_s") is not None]
    print(f"Requests:        {len(records)}")
    print(f"Errors:          {len(records) - len(ok)}")
    print(f"With image:      {sum(1 for r in records if r.get('image_name'))}")
    print(f"Images resized:  {sum(1 for r in records if '->' in (r.get('image_px') or ''))}")
    if latencies:
        print(f"Latency avg:     {statistics.mean(latencies):.2f} s")
        print(f"Latency median:  {statistics.median(latencies):.2f} s")
        print(f"Latency p95:     {percentile(latencies, 95):.2f} s")
        print(f"Latency max:     {max(latencies):.2f} s  (first request after idle = model load)")
    suspicious = [r for r in ok if not (r.get("answer") or "").strip("? \n")]
    if suspicious:
        print(f"Empty/garbage answers: {len(suspicious)}")
        for r in suspicious:
            print(f"  {r['time']}  {r.get('image_name')}  {r.get('answer')!r}")


def write_sheet(records: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig so Excel shows non-English text correctly
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow({**r, "question_type": "", "grade": "", "note": ""})
    print(f"\nGrading sheet written to {out}")
    print("Fill in question_type (describe/ocr/problem/count/trick) and grade "
          f"({'/'.join(GRADES)}), then run with --graded {out}")


def report_graded(sheet: Path) -> None:
    with sheet.open(encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r.get("grade", "").strip()]
    if not rows:
        print("No graded rows yet.")
        return
    unknown = {r["grade"] for r in rows} - set(GRADES)
    if unknown:
        print(f"Warning: unknown grades {sorted(unknown)} (use {', '.join(GRADES)})")

    def line(label: str, group: list[dict]) -> None:
        counts = Counter(r["grade"].strip() for r in group)
        acc = 100 * counts["correct"] / len(group)
        detail = "  ".join(f"{g}={counts[g]}" for g in GRADES if counts[g])
        print(f"{label:<12} n={len(group):<3} correct={acc:5.1f}%   {detail}")

    print(f"Graded answers: {len(rows)}\n")
    line("ALL", rows)
    by_type: dict[str, list[dict]] = {}
    for r in rows:
        by_type.setdefault(r.get("question_type", "").strip() or "(untyped)", []).append(r)
    for qtype in sorted(by_type):
        line(qtype, by_type[qtype])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log", type=Path, default=Path("logs/requests.jsonl"))
    parser.add_argument("--since", help="only include requests from this date/time, e.g. 2026-11-05")
    parser.add_argument("--csv", type=Path, help="write a grading sheet to this CSV file")
    parser.add_argument("--graded", type=Path, help="report accuracy from a filled-in grading sheet")
    args = parser.parse_args()

    if args.graded:
        report_graded(args.graded)
        return
    records = load_log(args.log, args.since)
    if not records:
        print("No requests found.")
        return
    summarise(records)
    if args.csv:
        write_sheet(records, args.csv)


if __name__ == "__main__":
    main()
