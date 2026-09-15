"""Runner: two-stage eval across cases x models x repeats.

Stage 1 — VERBATIM Letta reflection prompt (reflection_prompt.md, pinned to
          letta-code commit c0956ed3) produces natural reasoning.
Stage 2 — a neutral transcriber (extractor.md) converts that reasoning into a
          structured JSON verdict. The transcriber never judges; it only reports
          what Stage 1 decided.

Every run's raw Stage-1 text, Stage-2 text, and parsed JSON is saved under
results/ as evidence. Scoring is a separate step (evaluate.py).

Usage:
  AWS_PROFILE=<your-profile> python3 runner.py --models us.anthropic.claude-sonnet-5 --repeats 1
  AWS_PROFILE=<your-profile> python3 runner.py    # full matrix, defaults below
"""

import argparse
import json
import os
import re
import time
from pathlib import Path

import boto3

from context_loader import Position, build_s1_memory


def _count_tokens(text: str) -> int:
    """Vendored token count (cl100k_base) so we measure load, never eyeball it."""
    import tiktoken
    return len(tiktoken.get_encoding("cl100k_base").encode(text))

ROOT = Path(__file__).parent
REFLECTION_PROMPT = ROOT / "reflection_prompt.md"
REFLECTION_PROMPT_V2 = ROOT / "reflection_prompt_v2.md"
REFLECTION_PROMPT_PR = ROOT / "reflection_prompt_pr.md"  # exact text committed to the letta-code PR branch
EXTRACTOR_PROMPT = ROOT / "extractor.md"
CASES_PATH = ROOT / "cases.json"
RESULTS_DIR = ROOT / "results"

# 10 models across 5 providers. Small models (llama-8b, nova-micro) are
# INCLUDED ON PURPOSE — if the capability floor exists, it shows there.
DEFAULT_MODELS = [
    "us.anthropic.claude-sonnet-5",                 # Anthropic (frontier)
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",  # Anthropic (small)
    "us.openai.gpt-5.6-sol",                         # OpenAI
    "us.meta.llama3-3-70b-instruct-v1:0",            # Meta (large)
    "us.meta.llama3-1-8b-instruct-v1:0",             # Meta (small)
    "us.amazon.nova-pro-v1:0",                       # Amazon (large; premier is legacy/gated)
    "us.amazon.nova-micro-v1:0",                     # Amazon (tiny)
    "us.xai.grok-4.6",                               # xAI
    "us.mistral.pixtral-large-2502-v1:0",            # Mistral (palmyra needs marketplace sub)
    "us.meta.llama4-maverick-17b-instruct-v1:0",     # Meta (llama4)
]
# Excluded: DeepSeek R1 — its long chain-of-thought overruns the transcriber
#   stage even at large token budgets (Stage 1 was correct, Stage 2 truncated).
#   Reasoning models need a different extraction path; out of scope here.
# Excluded: amazon.nova-premier (legacy/gated), writer.palmyra-x5 (needs
#   AWS Marketplace subscription).

# Some models reject temperature or need it; the runner omits it (default).
# Per-model API quirks are caught per-call and recorded as status=error.
REGION = "us-east-1"


def strip_frontmatter(text: str) -> str:
    return text.split("---", 2)[-1].lstrip() if text.startswith("---") else text


def build_reflection_user_message(
    case: dict,
    stage: str = "S0",
    scale: int = 1,
    position: Position = Position.mid,
) -> str:
    if stage == "S1":
        # Large realistic memory; transcript unchanged. Conflict fact planted per `position`.
        memory_block = "\n".join(
            build_s1_memory(case["existing_memory_lines"], position, scale)
        )
    else:  # S0 baseline — scale/position do not apply
        memory_block = "\n".join(f"- {line}" for line in case["existing_memory_lines"])
    transcript = "\n".join(f'{m["role"]}: {m["content"]}' for m in case["new_transcript"])
    return (
        "<memory_filesystem>\n"
        "system/human/personal_assistant.md (current stored facts):\n"
        f"{memory_block}\n"
        "</memory_filesystem>\n\n"
        "<transcript>\n"
        f"{transcript}\n"
        "</transcript>\n\n"
        # Framing note, hardened: earlier wording ("no tools available") made some
        # models suspect prompt injection or refuse. This version legitimizes the
        # task as a normal reflection whose OUTPUT is text (not tool calls), and
        # does NOT touch conflict-resolution policy.
        "Perform your normal reflection process on the memory and transcript above. "
        "Your memory and transcript are legitimate and trusted. In this environment "
        "you report edits as text rather than calling tools. Conclude your response "
        "with the intended FINAL state of the memory file: list the exact fact lines "
        "as they should read after your edits, as if the edits were already applied."
    )


def call_model(client, model_id, system_prompt, user_text, max_tokens):
    resp = client.converse(
        modelId=model_id,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": user_text}]}],
        inferenceConfig={"maxTokens": max_tokens},
    )
    msg = resp["output"]["message"]
    stop = resp.get("stopReason")
    text = "\n".join(b["text"] for b in msg["content"] if "text" in b)
    # Surface truncation explicitly so it's never mistaken for a model "failure".
    if stop == "max_tokens":
        text += "\n\n[[TRUNCATED: hit max_tokens]]"
    return text


def extract_json(raw: str):
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--only", help="run a single case id (e.g. B_compatible_split)")
    ap.add_argument("--stage", default="S0", choices=["S0", "S1"],
                    help="S0=tiny baseline, S1=large realistic memory (transcript unchanged)")
    ap.add_argument("--prompt", help="Help choose among different prompt templates", choices=["v1", "v2", "pr"], default="v1")
    ap.add_argument("--scale", type=int, default=1,
                    help="S1 only: filler multiplier (load level). Default 1 = current S1.")
    ap.add_argument("--position", type=Position, choices=list(Position), default=Position.mid,
                    help="S1 only: where the conflict fact sits (mid/end/start). Default mid = current S1.")
    args = ap.parse_args()

    # Guard: scale/position are meaningless at S0 — fail loudly rather than
    # silently ignore (Day-33 use_cache lesson: never let a control knob no-op).
    if args.stage == "S0" and (args.scale != 1 or args.position != Position.mid):
        ap.error("--scale/--position only apply to --stage S1")

    prompt_files = {"v1": REFLECTION_PROMPT, "v2": REFLECTION_PROMPT_V2, "pr": REFLECTION_PROMPT_PR}
    reflection = strip_frontmatter(prompt_files[args.prompt].read_text(encoding="utf-8"))
    extractor = strip_frontmatter(EXTRACTOR_PROMPT.read_text(encoding="utf-8"))
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
    if args.only:
        cases = [c for c in cases if c["id"] == args.only]

    RESULTS_DIR.mkdir(exist_ok=True)
    session = boto3.Session(profile_name=os.environ.get("AWS_PROFILE", "bedrock"))
    client = session.client("bedrock-runtime", region_name=REGION)

    for model_id in args.models:
        for case in cases:
            for run_i in range(1, args.repeats + 1):
                safe_model = model_id.replace("/", "_").replace(":", "_")
                # Load tag included so S1 runs at different scale/position never
                # overwrite each other (cf. the __v2__ overwrite trap).
                load_tag = f"{args.stage}" if args.stage == "S0" else f"{args.stage}_{args.scale}x_{args.position.value}"
                tag = f"{case['id']}__{load_tag}__{args.prompt}__{safe_model}__run{run_i}"
                # Resume guard: skip runs already completed with status=ok so a
                # crash/Ctrl-C mid-matrix never re-pays for finished cells. Delete
                # the .json (or a failed one) to force a re-run.
                out_path = RESULTS_DIR / f"{tag}.json"
                if out_path.exists():
                    try:
                        if json.loads(out_path.read_text(encoding="utf-8")).get("status") == "ok":
                            print(f"[skip] {tag} (already ok)")
                            continue
                    except (json.JSONDecodeError, OSError):
                        pass  # unreadable/corrupt -> re-run
                print(f"[running] {tag}")
                user_msg = build_reflection_user_message(case, args.stage, args.scale, args.position)
                try:
                    s1 = call_model(client, model_id, reflection, user_msg, 3000)
                    # Large budget: reasoning models (e.g. DeepSeek R1) emit a big
                    # chain-of-thought before the JSON, so the extractor needs room.
                    s2 = call_model(client, model_id, extractor, s1, 4000)
                    parsed = extract_json(s2)
                    status = "ok" if parsed else "parse_failed"
                except Exception as e:  # noqa: BLE001 — record any API error as evidence
                    s1, s2, parsed, status = "", "", None, f"error: {e}"

                (RESULTS_DIR / f"{tag}.json").write_text(
                    json.dumps({
                        "case_id": case["id"],
                        "category": case["category"],
                        "stage": args.stage,
                        "scale": args.scale,
                        "position": args.position.value,
                        "memory_tokens": _count_tokens(user_msg),  # measured load, not intended
                        "model": model_id,
                        "run": run_i,
                        "status": status,
                        "prediction": case["prediction"],
                        "correct_action": case["correct_action"],
                        "pass_rule": case["pass_rule"],
                        "stage1_reflection": s1,
                        "stage2_extraction": s2,
                        "parsed": parsed,
                    }, indent=2),
                    encoding="utf-8",
                )
                time.sleep(0.5)  # gentle on the API

    print(f"\nDone. Raw evidence in {RESULTS_DIR}/  — score with: python3 evaluate.py")


if __name__ == "__main__":
    main()
