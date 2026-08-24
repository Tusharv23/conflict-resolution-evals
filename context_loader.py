"""Context-load conditions for the eval.

Design: change ONE variable at a time so a failure is attributable.
- S0: tiny memory, tiny transcript (baseline; lives in cases.json directly).
- S1: LARGE realistic memory (~180 lines), transcript UNCHANGED.
- S2: tiny memory, LARGE noisy transcript. (follow-up)
- S3: both large. (capstone — only after S1/S2 isolate the cause)

Rule: filler is PLAUSIBLE agent memory (preferences, other contacts, project
notes), never adversarial decoys. Each case's real conflict fact is planted at a
fixed MID-FILE position so burial is consistent across cases.
"""

# Realistic personal-assistant memory filler — plausible, non-adversarial.
# Deliberately does NOT contain addresses/dietary facts that would collide with
# the case-specific conflict lines (those are injected per case).
_FILLER_BEFORE = """# Communication preferences
- Prefers concise, direct answers; dislikes filler and over-explanation.
- Wants to be asked before large multi-file changes; small fixes can proceed.
- Timezone: IST (UTC+5:30). Working hours roughly 10:00–19:00.
- Prefers metric units and DD-MM-YYYY dates.

# Work context
- Backend engineer; primary stack Python (FastAPI) and some TypeScript.
- Uses `uv` for Python envs — never bare pip. Corrected on this repeatedly.
- Conventional commits; feature branches, never commits to main directly.
- Runs lint before tests; prefers pytest with table-driven cases.
- Current project: migrating an API gateway from Kong to Envoy (replicate as-is).

# Calendar & routines
- Standup daily at 10:15. No meetings on Wednesday afternoons (focus block).
- Gym Mon/Wed/Fri mornings; prefers no early meetings those days.
- Reviews PRs end of day, not first thing.

# Food & ordering habits (general)
- Usual lunch order via Swiggy; likes South Indian and Thai.
- Coffee: filter coffee, no sugar. Orders beans monthly from Blue Tokai.
- Weekend cooking; buys groceries from the local market on Saturdays.

# Contacts (non-conflicting)
- Manager: Priya (priya@work.example) — prefers async updates on Slack.
- Best friend: Rohan — lives in Hyderabad, visits every couple of months.
- Landlord: Mr. Rao — contact only for maintenance, prefers WhatsApp.
- Doctor: Dr. Mehta clinic, Indiranagar — annual checkup in November.

# Shopping & subscriptions
- Amazon Prime member; frequent Amazon vendor for electronics.
- Netflix + Spotify; shares Spotify family plan with siblings.
- Prefers cash-on-delivery avoided; default card ending 4412.
"""

_FILLER_AFTER = """# Travel notes
- Prefers window seats, aisle only on long-haul.
- Frequent flyer with IndiGo; passport renewal due next year.
- Likes boutique stays over large hotels; books refundable rates.

# Project gotchas (index)
- The auth module is fragile — check existing tests before modifying.
- Legacy module paths deprecated after the monorepo consolidation.
- Staging DB resets nightly; don't rely on persisted test data there.

# Reading & learning
- Currently reading Chip Huyen's AI Engineering (inference optimization).
- Interested in KV cache, batching, PagedAttention, serving capacity.
- Keeps a 90-day learning journal under journal/.

# Misc preferences
- Likes dark-mode everything; terminal over GUI where possible.
- Names things clearly; dislikes cryptic abbreviations in code.
- Keeps memory tidy; periodically prunes stale notes.
"""


def build_s1_memory(case_conflict_lines: list[str]) -> list[str]:
    """Return ~180 lines of realistic memory with the case's conflict fact(s)
    planted mid-file, surrounded by plausible filler.

    case_conflict_lines: the case's existing_memory_lines (the fact(s) that the
    transcript will contradict) — planted verbatim so scoring still works.
    """
    before = _FILLER_BEFORE.strip("\n").splitlines()
    after = _FILLER_AFTER.strip("\n").splitlines()
    conflict_section = ["# Recipients & personal facts (current)"] + [
        f"- {line}" for line in case_conflict_lines
    ]
    # conflict fact sits after ~40 lines of filler and before ~30 more — buried,
    # not first and not last (avoids primacy/recency being trivially helpful).
    return before + [""] + conflict_section + [""] + after
