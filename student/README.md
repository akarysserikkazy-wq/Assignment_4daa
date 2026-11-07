# Own tests

Own tests and benchmark for Assignment 4 (language: Python). Run all commands from the repository root.

## Files

- `test_student.py`: 18 unit tests for all eight commands (lcs, merge, tree, naive, kmp, rk, suffix, aho). Small inputs are checked against independently written oracles (brute force for lcs, merge and tree, slicing for string search, direct sorting of suffixes for suffix, per-pattern occurrence counting for aho). It also covers boundary cases: empty inputs, empty pattern, the `ab`/`dj` hash collision, a 100000-vertex chain, duplicate and suffix patterns, empty dictionary and no texts.
- `bench.py`: benchmark of naive, KMP and exact RK on the same inputs (random and repetitive text, n = 500, 1000, 3000). It checks that all three outputs are identical before timing and prints a Markdown table.

## How to run

    python tests/student/test_student.py
    python tests/student/bench.py

Expected result of the first command: `Ran 18 tests ... OK`.

The table of test cases, expected and actual results, and the defect each case detects are in `ANALYSIS.md` (section "Own tests"). The benchmark results and their discussion are in `ANALYSIS.md` (section "Search comparison").