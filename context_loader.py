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
_FILLER_XL_BLOCKS = [
    """# Vehicle & commute
- Rides a 2019 Honda City; service due every 10,000 km at the authorized center.
- Prefers driving to work on Mondays only; metro the rest of the week.
- FASTag auto-recharges from the default card when balance drops below ₹200.
- Parking spot B2-114 at the office; visitor parking needs a day-pass email.
""",
"""# Fitness log (general)
- Gym program: push/pull/legs split; deload week every eighth week.
- Runs a slow 5k on Saturday mornings when the weather allows.
- Tracks workouts in a spreadsheet, not an app; dislikes fitness-app streaks.
- Yearly body composition check at the gym every January.
- Foam-rolls after leg day; skips it otherwise and admits it.
""",
"""# Finance & bills
- Credit card statement date is the 14th; pays in full, hates revolving.
- SIPs debit on the 5th; two index funds and one mid-cap.
- Electricity bill autopay caps at ₹6,000; alerts above that.
- Splits streaming costs with siblings; settles on the 1st via UPI.
- Keeps a strict no-EMI rule for gadgets.
""",
"""# Devices & digital hygiene
- Main laptop: ThinkPad running Ubuntu; personal MacBook stays on the shelf.
- Phone on permanent Do Not Disturb; only starred contacts ring.
- Password manager everywhere; rotates the master passphrase yearly.
- Backs up photos to a NAS on Sunday nights; verifies the backup monthly.
- Refuses smart-home gadgets except one smart bulb in the study.
""",
"""# Books & podcasts
- Reads nonfiction on Kindle, fiction on paper; two books in parallel usually.
- Podcast queue: one engineering show, one history show; listens at 1.2x.
- Annual reread: The Pragmatic Programmer, every December.
- Keeps a "did not finish" list without guilt.
- Buys books faster than reading them; accepts the backlog.
""",
"""# Music & concerts
- Practices acoustic guitar ~20 minutes most evenings; three chords short of decent.
- Concert rule: books tickets same-day as announcement or not at all.
- Playlists sorted by energy, not genre.
- Wants to learn exactly one full fingerstyle piece before the year ends.
""",
"""# Photography
- Shoots street photography on Sunday walks; one lens, no zoom.
- Edits monthly, not per-shoot; culls hard, keeps under 30 photos a month.
- Prints twelve photos a year for a physical album.
- Camera bag packed by the door; battery charging rule: never below one spare.
""",
"""# Work context (secondary projects)
- Mentors two junior engineers; syncs with each for 30 minutes on Thursdays.
- Owns the internal service-template repo; reviews template PRs within a day.
- Quarterly cost-review deck is his responsibility; dreads the screenshots part.
- Advocates for boring technology in design reviews; keeps a decision log.
- On the interview panel for backend roles; two interviews a week cap.
""",
"""# Learning queue
- Working through a distributed-systems course; two lectures a week target.
- Practices SQL window functions on weekends; keeps a snippets file.
- Wants to give one internal tech talk per quarter; drafts in bullet points first.
- Flashcards for networking fundamentals; reviews on the metro.
""",
"""# Social & community
- Monthly board-game night with college friends; hosts every third month.
- Volunteers at a coding bootcamp two Saturdays a quarter.
- Neighborhood WhatsApp group: muted, checks weekly for society notices.
- Sends birthday wishes manually, never automated; keeps a reminder list.
- College group plans an annual trip; he's the one who books tickets.
""",
"""# Seasonal preferences
- Monsoon rule: carries a packable rain jacket June through September.
- Runs the air purifier October to January; filter change every winter.
- Prefers winter for trekking plans; avoids summer travel bookings.
- Umbrella lives in the office bag permanently.
""",
"""# Gifting preferences
- Default gift for colleagues: good coffee beans or a book, never gift cards.
- Keeps a running note of gift ideas people mention casually.
- Anniversary and birthday gifts bought two weeks early; learned the hard way.
- Wraps gifts badly and outsources wrapping to the store when possible.
""",
"""# Errands & services
- Laundry pickup Wednesdays; ironing only for formals.
- Haircut every four weeks, same barber, 8 AM slot to avoid the rush.
- Plant watering schedule: Tuesdays and Fridays; the fern is on thin ice.
- Cobbler and tailor shops saved as contacts; prefers repair over replace.
""",
"""# Watching habits
- One film a week rule, usually Friday night; documentaries over series lately.
- Abandons series mid-season without guilt if it drags.
- Rewatches comfort shows while doing chores.
- Keeps a shared watchlist with his wife; she vetoes horror.
""",
"""# Sports & games
- Plays badminton casually on alternate Sundays; owns two rackets, lends one.
- Follows test cricket properly; highlights only for T20.
- Chess.com rapid rating hovers around 1200; plays two games at lunch.
- Fantasy league with office friends; perennially mid-table.
"""
]
from enum import Enum


class Position(str, Enum):
    """3.10-compatible StrEnum: subclasses str so `.value` and str-compares work."""
    mid = "mid"
    end = "end"
    start = "start"

import tiktoken

_ENC = tiktoken.get_encoding("cl100k_base")


def _toks(text: str) -> int:
    return len(_ENC.encode(text))


# Fixed XL tranches, chosen ONCE by token count so the equal-token ladder is
# deterministic and identical across positions. Filler set is fixed per scale;
# only the conflict block moves (position = one clean variable).
# Ladder re-targeted Sep 5 to the natural full-pool ceiling (15 distinct blocks,
# no repetition): 589 / 1129 / 1670 tok, even ~540-tok spacing.
#   scale 1: no XL      -> base (_FILLER_BEFORE + _FILLER_AFTER) ~= 589 tok
#   scale 2: + XL[0:7]  -> ~1129 tok  (even midpoint)
#   scale 3: + XL[0:15] -> ~1670 tok  (full pool ceiling)
_XL_TRANCHE = {1: slice(0, 0), 2: slice(0, 7), 3: slice(0, 15)}


def build_s1_memory(
    case_conflict_lines: list[str],
    position: Position = Position.mid,
    scale: int = 1,
) -> list[str]:
    """Return the S1 memory as an ordered list of markdown blocks.

    Filler is FIXED per scale (same blocks regardless of position). The conflict
    block is placed by `position` within that fixed filler:
      - start: conflict first
      - end:   conflict last
      - mid:   conflict at the TOKEN midpoint of the filler
    Token counts of _FILLER_BEFORE/_FILLER_AFTER are fully accounted for.
    """
    if scale < 1:
        raise ValueError("scale must be at least 1")
    if scale not in _XL_TRANCHE:
        raise ValueError(f"scale {scale} has no registered XL tranche; use 1-3")

    conflict_block = "\n".join(
        ["# Recipients & personal facts (current)"]
        + [f"- {line}" for line in case_conflict_lines]
    )

    # Fixed, ordered filler for this scale (never repeated, never reordered).
    filler = [_FILLER_BEFORE] + list(_FILLER_XL_BLOCKS[_XL_TRANCHE[scale]]) + [_FILLER_AFTER]

    if position == Position.start:
        return [conflict_block] + filler
    if position == Position.end:
        return filler + [conflict_block]

    # mid: insert at the token midpoint of the filler.
    half = sum(_toks(b) for b in filler) / 2
    running, split = 0, len(filler)
    for i, block in enumerate(filler):
        running += _toks(block)
        if running >= half:
            split = i + 1
            break
    return filler[:split] + [conflict_block] + filler[split:]