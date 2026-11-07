"""Own tests for A4. Run from repository root:  python tests/student/test_student.py"""
import itertools, pathlib, random, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "Python" / "source"))
import algorithms as A


def is_subseq(s, t):
    it = iter(t)
    return all(c in it for c in s)


def occurrences(t, p):  # independent oracle: slicing, not the course algorithms
    if p == "":
        return list(range(len(t) + 1))
    return [i for i in range(len(t) - len(p) + 1) if t[i:i + len(p)] == p]


class Lcs(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(A.lcs({"a": "", "b": "abc"}), {"length": 0, "sequence": ""})
        self.assertEqual(A.lcs({"a": "", "b": ""}), {"length": 0, "sequence": ""})

    def test_subsequence_not_substring(self):
        r = A.lcs({"a": "tea_time", "b": "team"})
        self.assertEqual((r["length"], r["sequence"]), (4, "team"))

    def test_random_vs_bruteforce(self):
        R = random.Random(1)
        for _ in range(300):
            a = "".join(R.choice("abc") for _ in range(R.randint(0, 7)))
            b = "".join(R.choice("abc") for _ in range(R.randint(0, 7)))
            best = max(len(s) for k in range(len(a) + 1)
                       for s in map("".join, itertools.combinations(a, k)) if is_subseq(s, b))
            r = A.lcs({"a": a, "b": b})
            self.assertEqual(r["length"], best)
            self.assertTrue(len(r["sequence"]) == best and is_subseq(r["sequence"], a) and is_subseq(r["sequence"], b))


class Merge(unittest.TestCase):
    def test_small(self):
        r = A.merge({"sizes": [2, 3, 4]})
        self.assertEqual(r["cost"], 14)
        self.assertEqual(r["plan"], [[0, 0, 1], [0, 1, 2]])

    def test_zero_one_and_large(self):
        self.assertEqual(A.merge({"sizes": []}), {"cost": 0, "plan": []})
        self.assertEqual(A.merge({"sizes": [7]}), {"cost": 0, "plan": []})
        self.assertEqual(A.merge({"sizes": [10 ** 9] * 3})["cost"], 5 * 10 ** 9)

    def test_adjacent_not_greedy(self):
        self.assertEqual(A.merge({"sizes": [1, 100, 1]})["cost"], 203)  # 104 would be non-adjacent merging


class Tree(unittest.TestCase):
    def test_example(self):
        r = A.tree({"n": 3, "weights": [4, 9, 6], "edges": [[0, 1], [1, 2]]})
        self.assertEqual(r["weight"], 10)

    def test_all_negative_and_empty(self):
        self.assertEqual(A.tree({"n": 0, "weights": [], "edges": []}), {"weight": 0, "selected": []})
        self.assertEqual(A.tree({"n": 2, "weights": [-1, -2], "edges": [[0, 1]]})["weight"], 0)

    def test_deep_chain_no_recursion_error(self):
        n = 100000
        r = A.tree({"n": n, "weights": [1] * n, "edges": [[i, i + 1] for i in range(n - 1)]})
        self.assertEqual(r["weight"], n // 2 + n % 2)
        s = set(r["selected"])
        self.assertTrue(all(i + 1 not in s for i in s))


class Search(unittest.TestCase):
    def test_all_three_agree(self):
        R = random.Random(2)
        for _ in range(500):
            t = "".join(R.choice("ab ") for _ in range(R.randint(0, 20)))
            p = "".join(R.choice("ab ") for _ in range(R.randint(0, 4)))
            e = occurrences(t, p)
            req = {"text": t, "pattern": p}
            self.assertEqual(A.naive(req)["positions"], e)
            self.assertEqual(A.kmp(req)["positions"], e)
            self.assertEqual(A.rk(req)["positions"], e)

    def test_empty_pattern_gives_n_plus_1(self):
        for f in (A.naive, A.kmp, A.rk):
            self.assertEqual(f({"text": "abc", "pattern": ""})["positions"], [0, 1, 2, 3])

    def test_rk_collision_ab_dj(self):
        self.assertEqual(A.rk({"text": "abdj", "pattern": "ab"})["positions"], [0])
        self.assertEqual(A.rk({"text": "bcek", "pattern": "bc"})["positions"], [0])


class Suffix(unittest.TestCase):
    def test_banana(self):
        r = A.suffix({"text": "banana"})
        self.assertEqual(r["sa"], [5, 3, 1, 0, 4, 2])
        self.assertEqual(r["lcp"], [0, 1, 3, 0, 0, 2])
        self.assertEqual(len(r["repeated"]), 3)

    def test_edges(self):
        self.assertEqual(A.suffix({"text": ""}), {"sa": [], "lcp": [], "repeated": ""})
        self.assertEqual(A.suffix({"text": "$"}), {"sa": [0], "lcp": [0], "repeated": ""})
        self.assertEqual(A.suffix({"text": "aaaa"})["lcp"], [0, 1, 2, 3])

    def test_random_vs_direct(self):
        R = random.Random(3)
        for _ in range(300):
            t = "".join(R.choice("abc") for _ in range(R.randint(0, 15)))
            sa = sorted(range(len(t)), key=lambda i: t[i:])
            self.assertEqual(A.suffix({"text": t})["sa"], sa)


class Aho(unittest.TestCase):
    def test_duplicates_and_suffix_patterns(self):
        r = A.aho({"patterns": ["he", "she", "he"], "texts": ["sheshe", "sheshe", ""]})
        self.assertEqual(r["counts"], [[2, 2, 2], [2, 2, 2], [0, 0, 0]])

    def test_empty_cases(self):
        self.assertEqual(A.aho({"patterns": [], "texts": ["a", ""]})["counts"], [[], []])
        self.assertEqual(A.aho({"patterns": ["a"], "texts": []})["counts"], [])

    def test_random_vs_oracle(self):
        R = random.Random(4)
        for _ in range(300):
            pats = ["".join(R.choice("ab") for _ in range(R.randint(1, 3))) for _ in range(R.randint(0, 5))]
            texts = ["".join(R.choice("ab") for _ in range(R.randint(0, 12))) for _ in range(3)]
            self.assertEqual(A.aho({"patterns": pats, "texts": texts})["counts"],
                             [[len(occurrences(t, p)) for p in pats] for t in texts])


if __name__ == "__main__":
    unittest.main(verbosity=2)