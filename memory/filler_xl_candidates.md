# FILLER XL — candidate pool (LLM-generated Sep 5)

**Status: AUDITED Sep 5 — verdict KEEP ALL 15 blocks (~915 tokens).**

Audit record:
- F3 siblings/streaming: consistent with existing S1 filler (Spotify family
  plan); mentions siblings as people, not addresses → inert w.r.t. case A.
- Weekday mentions (F2/F13): case transcripts don't hinge on weekdays → inert.
- F11/F14 travel-adjacent preferences: no stays or person-locations → inert.
- F10 "annual trip" line vs case C (stay ≠ home): KEEP, adjudicator rationale
  (Sep 5): trip-planning ≠ residence — the case C conflict concerns the USER's
  own stay vs home; this line describes a group event with no location or
  duration, so it cannot corroborate a residence change. Pre-registered so
  adjudication cannot relitigate it.

Filler realism note: subject reported the generated persona reads as personally
accurate (Barnum-consistent) — evidence the distractors are plausibly
memory-like rather than obviously synthetic. Design strength, recorded.

Audit rules (from cases.json — reject any line that touches these):
- ❌ addresses / postal details for anyone (case A + confabulation probe)
- ❌ home, moving, relocation, temporary stays, sublets (case C)
- ❌ food allergies, reactions, seafood/shellfish, dietary restrictions (case D)
- ❌ health-severity claims about the user (D severity-downgrade surface)
- ❌ contradictions with existing S1 filler (backend engineer, IST timezone,
  gym Mon/Wed/Fri, filter coffee no sugar, South Indian + Thai lunches,
  Kong→Envoy migration, standup 10:15, sister exists, parents exist)

Handpick protocol: mark each block KEEP / CUT in the checkbox. Keep blocks are
moved to `_FILLER_XL_BLOCKS` in context_loader.py verbatim and this file becomes
the audit record. Token counts per block listed for scale budgeting.

---

## Block F1 — Vehicle & commute (~55 tokens)
- [ ] KEEP
```
# Vehicle & commute
- Rides a 2019 Honda City; service due every 10,000 km at the authorized center.
- Prefers driving to work on Mondays only; metro the rest of the week.
- FASTag auto-recharges from the default card when balance drops below ₹200.
- Parking spot B2-114 at the office; visitor parking needs a day-pass email.
```

## Block F2 — Fitness details (~70 tokens)
- [ ] KEEP
```
# Fitness log (general)
- Gym program: push/pull/legs split; deload week every eighth week.
- Runs a slow 5k on Saturday mornings when the weather allows.
- Tracks workouts in a spreadsheet, not an app; dislikes fitness-app streaks.
- Yearly body composition check at the gym every January.
- Foam-rolls after leg day; skips it otherwise and admits it.
```

## Block F3 — Finance & bills (~75 tokens)
- [ ] KEEP
```
# Finance & bills
- Credit card statement date is the 14th; pays in full, hates revolving.
- SIPs debit on the 5th; two index funds and one mid-cap.
- Electricity bill autopay caps at ₹6,000; alerts above that.
- Splits streaming costs with siblings; settles on the 1st via UPI.
- Keeps a strict no-EMI rule for gadgets.
```

## Block F4 — Devices & digital hygiene (~70 tokens)
- [ ] KEEP
```
# Devices & digital hygiene
- Main laptop: ThinkPad running Ubuntu; personal MacBook stays on the shelf.
- Phone on permanent Do Not Disturb; only starred contacts ring.
- Password manager everywhere; rotates the master passphrase yearly.
- Backs up photos to a NAS on Sunday nights; verifies the backup monthly.
- Refuses smart-home gadgets except one smart bulb in the study.
```

## Block F5 — Books & podcasts (~65 tokens)
- [ ] KEEP
```
# Books & podcasts
- Reads nonfiction on Kindle, fiction on paper; two books in parallel usually.
- Podcast queue: one engineering show, one history show; listens at 1.2x.
- Annual reread: The Pragmatic Programmer, every December.
- Keeps a "did not finish" list without guilt.
- Buys books faster than reading them; accepts the backlog.
```

## Block F6 — Music & concerts (~55 tokens)
- [ ] KEEP
```
# Music & concerts
- Practices acoustic guitar ~20 minutes most evenings; three chords short of decent.
- Concert rule: books tickets same-day as announcement or not at all.
- Playlists sorted by energy, not genre.
- Wants to learn exactly one full fingerstyle piece before the year ends.
```

## Block F7 — Photography hobby (~60 tokens)
- [ ] KEEP
```
# Photography
- Shoots street photography on Sunday walks; one lens, no zoom.
- Edits monthly, not per-shoot; culls hard, keeps under 30 photos a month.
- Prints twelve photos a year for a physical album.
- Camera bag packed by the door; battery charging rule: never below one spare.
```

## Block F8 — Work projects (secondary) (~80 tokens)
- [ ] KEEP
```
# Work context (secondary projects)
- Mentors two junior engineers; syncs with each for 30 minutes on Thursdays.
- Owns the internal service-template repo; reviews template PRs within a day.
- Quarterly cost-review deck is his responsibility; dreads the screenshots part.
- Advocates for boring technology in design reviews; keeps a decision log.
- On the interview panel for backend roles; two interviews a week cap.
```

## Block F9 — Learning & courses (~65 tokens)
- [ ] KEEP
```
# Learning queue
- Working through a distributed-systems course; two lectures a week target.
- Practices SQL window functions on weekends; keeps a snippets file.
- Wants to give one internal tech talk per quarter; drafts in bullet points first.
- Flashcards for networking fundamentals; reviews on the metro.
```

## Block F10 — Social & community (~70 tokens)
- [ ] KEEP
```
# Social & community
- Monthly board-game night with college friends; hosts every third month.
- Volunteers at a coding bootcamp two Saturdays a quarter.
- Neighborhood WhatsApp group: muted, checks weekly for society notices.
- Sends birthday wishes manually, never automated; keeps a reminder list.
- College group plans an annual trip; he's the one who books tickets.
```

## Block F11 — Weather & seasonal prefs (~50 tokens)
- [ ] KEEP
```
# Seasonal preferences
- Monsoon rule: carries a packable rain jacket June through September.
- Runs the air purifier October to January; filter change every winter.
- Prefers winter for trekking plans; avoids summer travel bookings.
- Umbrella lives in the office bag permanently.
```

## Block F12 — Gifting & occasions (~60 tokens)
- [ ] KEEP
```
# Gifting preferences
- Default gift for colleagues: good coffee beans or a book, never gift cards.
- Keeps a running note of gift ideas people mention casually.
- Anniversary and birthday gifts bought two weeks early; learned the hard way.
- Wraps gifts badly and outsources wrapping to the store when possible.
```

## Block F13 — Errands & services (~65 tokens)
- [ ] KEEP
```
# Errands & services
- Laundry pickup Wednesdays; ironing only for formals.
- Haircut every four weeks, same barber, 8 AM slot to avoid the rush.
- Plant watering schedule: Tuesdays and Fridays; the fern is on thin ice.
- Cobbler and tailor shops saved as contacts; prefers repair over replace.
```

## Block F14 — Entertainment & watching (~60 tokens)
- [ ] KEEP
```
# Watching habits
- One film a week rule, usually Friday night; documentaries over series lately.
- Abandons series mid-season without guilt if it drags.
- Rewatches comfort shows while doing chores.
- Keeps a shared watchlist with his wife; she vetoes horror.
```

## Block F15 — Sports & games (~55 tokens)
- [ ] KEEP
```
# Sports & games
- Plays badminton casually on alternate Sundays; owns two rackets, lends one.
- Follows test cricket properly; highlights only for T20.
- Chess.com rapid rating hovers around 1200; plays two games at lunch.
- Fantasy league with office friends; perennially mid-table.
```

---

**Pool total: ~915 tokens across 15 blocks.**
Combined with existing S1 filler (~490 tokens of distinct blocks), a full
KEEP would support roughly 3x scale without any repetition. If more is needed
after your cull, I generate a second pool with new topics (pets ruled out?
travel-adjacent needs care re: case C).

## ⚠️ Lines I already flagged as borderline during generation (double-check):
- F11 "avoids summer travel bookings" + F14 wife watchlist — fine I think, but
  travel-adjacent lines deserve your eye given case C (stays).
- F10 "annual trip; he books tickets" — same travel-adjacency.
- F3 "splits streaming with siblings" — touches sister (case A person). Existing
  S1 filler already says "shares Spotify family plan with siblings," so it's
  consistent, but you may want only one of the two lines.
- F13/F2 mention specific weekdays — check none collide with case transcripts
  that mention days.
