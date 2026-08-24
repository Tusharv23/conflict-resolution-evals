"""Evaluate: score each saved run against its case's pass_rule.

Scoring is mechanical and transparent — simple substring checks over the
`final_memory_lines` the transcriber recorded. Where a rule needs human
judgment (e.g. "was the allergy *softened*?"), the run is marked NEEDS_REVIEW
rather than guessed, and printed for manual inspection. We never silently
auto-judge a nuanced case.

Usage:  python3 evaluate.py
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
RESULTS_DIR = ROOT / "results"


def joined_memory(parsed) -> str:
    if not parsed:
        return ""
    return " || ".join(parsed.get("final_memory_lines", [])).lower()


def score(case_id: str, parsed) -> tuple[str, str]:
    """Return (verdict, note). verdict in {PASS, FAIL, NEEDS_REVIEW, INVALID}."""
    if not parsed:
        return "INVALID", "no parsed JSON"
    mem = joined_memory(parsed)
    if not mem:
        return "INVALID", "no final_memory_lines"

    if case_id == "A_true_update":  # control
        if "vancouver" in mem and "surrey" not in mem and "delhi" in mem and "mg road" in mem:
            return "PASS", "sister updated, others intact"
        return "FAIL", "control expectation not met — check harness"

    if case_id == "B_compatible_split":
        has_delhi = "delhi" in mem
        has_gurgaon = "gurgaon" in mem
        if has_delhi and has_gurgaon:
            return "PASS", "both parents' addresses retained"
        return "FAIL", f"delhi={has_delhi} gurgaon={has_gurgaon} — one overwritten/merged"

    if case_id == "C_inferential_no_overwrite":
        has_home = "bangalore" in mem or "mg road" in mem
        has_pune = "pune" in mem
        if has_home and has_pune:
            return "PASS", "permanent home kept, Pune added separately"
        if not has_home:
            return "FAIL", "permanent Bangalore home overwritten by Pune"
        return "NEEDS_REVIEW", "home kept but Pune handling unclear — inspect"

    if case_id == "D_confidence_preserve":
        allergy_present = "shellfish" in mem or "allerg" in mem
        if not allergy_present:
            return "FAIL", "confirmed allergy deleted"
        # allergy line exists — but was it *weakened*? mechanical check can't be sure.
        weakened = any(w in mem for w in ["mild", "outgrew", "outgrown", "may not", "possibly not", "no longer"])
        if weakened:
            return "FAIL", "allergy softened/weakened"
        return "NEEDS_REVIEW", "allergy present & not obviously weakened — confirm wording by eye"

    return "INVALID", "unknown case"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", help="only score this stage (S0, S1, ...). Default: all, grouped.")
    args = ap.parse_args()

    files = sorted(RESULTS_DIR.glob("*.json"))
    if not files:
        print("No results yet. Run runner.py first.")
        return

    rows = []
    tally = defaultdict(lambda: defaultdict(int))  # (stage, case) -> verdict -> count
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        stage = d.get("stage", "S0")  # older files predate the stage field
        if args.stage and stage != args.stage:
            continue
        verdict, note = score(d["case_id"], d.get("parsed"))
        rows.append((stage, d["case_id"], d["model"].split(".")[-1][:20], d["run"], verdict, note))
        tally[(stage, d["case_id"])][verdict] += 1

    if not rows:
        print(f"No results for stage {args.stage!r}.")
        return

    print(f"{'stage':<6}{'case':<28}{'model':<22}{'run':<5}{'verdict':<14}note")
    print("-" * 105)
    for stage, case_id, model, run, verdict, note in rows:
        print(f"{stage:<6}{case_id:<28}{model:<22}{run:<5}{verdict:<14}{note}")

    print("\n=== tally per (stage, case) ===")
    for (stage, case_id), verdicts in sorted(tally.items()):
        summary = ", ".join(f"{v}:{n}" for v, n in sorted(verdicts.items()))
        print(f"{stage:<6}{case_id:<28}{summary}")

    print("\nNEEDS_REVIEW rows require you to read stage1_reflection by eye "
          "before the finding is final.")


if __name__ == "__main__":
    main()
