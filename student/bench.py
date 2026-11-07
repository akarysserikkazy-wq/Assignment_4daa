"""Benchmark naive / KMP / exact RK. Run from repository root: python tests/student/bench.py"""
import pathlib, platform, random, statistics, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "Python" / "source"))
import algorithms as A

ALGS = [("naive", A.naive), ("kmp", A.kmp), ("rk", A.rk)]
SEED = 12345


def make_case(kind, n, m):
    R = random.Random(SEED + n)
    if kind == "random":      # alphabet abcd, pattern copied from the text
        t = "".join(R.choice("abcd") for _ in range(n))
        i = R.randint(0, n - m)
        return t, t[i:i + m]
    return "a" * n, "a" * (m - 1) + "b"  # repetitive: many partial matches, no full match


print(f"# Python {platform.python_version()} | {platform.platform()} | {platform.processor()}")
print("|Case|n|m|Seed/generator|Algorithm|Run 1 (ms)|Run 2 (ms)|Run 3 (ms)|Median (ms)|Correct outputs checked|")
print("|---|---:|---:|---|---|---:|---:|---:|---:|---|")
for kind in ("random", "repetitive"):
    for n in (500, 1000, 3000):
        m = n // 10 if kind == "random" else n // 3
        t, p = make_case(kind, n, m)
        req = {"text": t, "pattern": p}
        outs = [f(req)["positions"] for _, f in ALGS]          # correctness first, outside timing
        ok = outs[0] == outs[1] == outs[2]
        for name, f in ALGS:
            f(req)                                              # warm-up, not timed
            runs = []
            for _ in range(3):
                t0 = time.perf_counter()
                f(req)
                runs.append((time.perf_counter() - t0) * 1000)
            print(f"|{kind}|{n}|{m}|seed {SEED + n}, {kind}|{name}|" +
                  "|".join(f"{x:.3f}" for x in runs) +
                  f"|{statistics.median(runs):.3f}|{'identical, ' + str(len(outs[0])) + ' starts' if ok else 'MISMATCH'}|")