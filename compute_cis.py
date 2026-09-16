from compute_deltas import OVERRIDES, MODELS, SCALES, PROMPTS, RUNS, verdict

from math import sqrt

# Baseline (Aug 24-25 adjudication, original 120-run matrix): nova-A 0/3 fail, llama-D 2/3 fail

def wilson_score_interval(successes, total, z=1.96):
    if total == 0:
        return (0.0, 0.0)
    
    p = successes / total
    denominator = 1 + z**2 / total
    centre_adjusted_probability = p + z**2 / (2 * total)
    adjusted_standard_deviation = sqrt((p * (1 - p) + z**2 / (4 * total)) / total)
    
    lower_bound = max((centre_adjusted_probability - z * adjusted_standard_deviation) / denominator, 0.0)
    upper_bound = min((centre_adjusted_probability + z * adjusted_standard_deviation) / denominator, 1.0)
    EPS = 1e-9
    if lower_bound <= p + EPS and p <= upper_bound + EPS:
        return (lower_bound, upper_bound)

    raise ValueError(f"Wilson score interval out of bounds: lower_bound={lower_bound}, upper_bound={upper_bound}, p={p}")


def tally(cases, model, scales=SCALES):
    """Count PASS/FAIL/INVALID over the given cases+scales (all prompts, all runs).
    Returns (fails, valid_n) — fail-side, INVALID excluded from the denominator."""
    p = f = i = 0
    for case in cases:
        for scale in scales:
            for prompt in PROMPTS:
                for run in RUNS:
                    v = verdict(case, scale, prompt, model, run)
                    if v == "P":
                        p += 1
                    elif v == "F":
                        f += 1
                    else:
                        i += 1
    return f, p + f


def pct_ci(fails, n):
    """Wilson fail-rate CI as an integer-percent (lo, hi) tuple."""
    return tuple(round(x * 100) for x in wilson_score_interval(fails, n))


def overlaps(a, b):
    """Do two (lo, hi) intervals overlap at all?"""
    return not (a[1] < b[0] or b[1] < a[0])


def calculateCI():
    """Fail-rate CIs for every bucket, then the three overlap checks + verdict table."""

    print("=" * 70)
    print("BUCKET 1 — fail-rate CI per (case, model), scales+prompts pooled (n<=18)")
    print("=" * 70)
    for case in ["A", "B", "C", "D"]:
        for model in MODELS:
            f, n = tally([case], model)
            print(f"  {case}  {model:8} {f}/{n} fail -> CI {pct_ci(f, n)}")
        print("-" * 70)

    print("\n" + "=" * 70)
    print("BUCKET 2 — capability axis: C+D pooled (n<=36)")
    print("=" * 70)
    for model in ["sonnet", "llama"]:
        f, n = tally(["C", "D"], model)
        print(f"  {model:8} C+D  {f}/{n} fail -> CI {pct_ci(f, n)}")

    print("\n" + "=" * 70)
    print("BUCKET 3 — baseline (Aug 24-25 adjudication, original 120-run matrix, n=3)")
    print("=" * 70)
    print(f"  nova  A  0/3 fail -> CI {pct_ci(0, 3)}   (comedy-wide by design)")
    print(f"  llama D  2/3 fail -> CI {pct_ci(2, 3)}")

    print("\n" + "=" * 70)
    print("BUCKET 4 — load gradient: llama-C fail-rate per scale (n=6 each)")
    print("=" * 70)
    for scale in SCALES:
        f, n = tally(["C"], "llama", scales=[scale])
        print(f"  {scale}x  {f}/{n} fail -> CI {pct_ci(f, n)}")

    print("\n" + "=" * 70)
    print("OVERLAP CHECKS — do baseline and load CIs overlap? (overlap => can't distinguish)")
    print("=" * 70)

    nova_a_base = pct_ci(0, 3)
    nova_a_load = pct_ci(*tally(["A"], "nova"))
    print(f"  nova-A confab under load: baseline {nova_a_base} vs load {nova_a_load} "
          f"-> {'OVERLAP, does NOT survive' if overlaps(nova_a_base, nova_a_load) else 'no overlap, survives'}")

    llama_d_base = pct_ci(2, 3)
    llama_d_load = pct_ci(*tally(["D"], "llama"))
    print(f"  llama-D worsens under load: baseline {llama_d_base} vs load {llama_d_load} "
          f"-> {'OVERLAP, does NOT survive' if overlaps(llama_d_base, llama_d_load) else 'no overlap, survives'}")

    print("  nova-C 'better under load': measurement INVALID (elision artifact) -> CI not computed")

    # Capability axis: sonnet C+D vs llama C+D
    son_cd = pct_ci(*tally(["C", "D"], "sonnet"))
    lla_cd = pct_ci(*tally(["C", "D"], "llama"))
    print(f"  capability axis (sonnet vs llama C+D): {son_cd} vs {lla_cd} "
          f"-> {'OVERLAP' if overlaps(son_cd, lla_cd) else 'NO overlap, survives'}")

    # Gradient endpoints: llama-C 1x vs 3x
    c1 = pct_ci(*tally(["C"], "llama", scales=[1]))
    c3 = pct_ci(*tally(["C"], "llama", scales=[3]))
    print(f"  gradient endpoints (llama-C 1x vs 3x): {c1} vs {c3} "
          f"-> {'OVERLAP' if overlaps(c1, c3) else 'NO overlap, endpoints separable'}")

    print("\n" + "=" * 70)
    print("VERDICT TABLE (matches journal/day-49.md hand table)")
    print("=" * 70)
    print("  capability axis dominates        | no overlap | SURVIVES")
    print("  nova-A confab emerges under load | overlap    | does NOT survive")
    print("  llama-D worsens under load       | overlap    | does NOT survive")
    print("  load gradient at END (llama-C)   | 1x vs 3x no overlap | endpoints survive; adjacent scales don't")


if __name__ == "__main__":

    assert tuple(round(x*100) for x in wilson_score_interval(2, 3)) == (21, 94)
    assert tuple(round(x*100) for x in wilson_score_interval(26, 36)) == (56, 84)
    assert tuple(round(x*100) for x in wilson_score_interval(1, 36)) == (0, 14) 
    assert tuple(round(x*100) for x in wilson_score_interval(6, 6)) == (61, 100)
    assert tuple(round(x*100) for x in wilson_score_interval(18, 18)) == (82, 100)
    calculateCI()
