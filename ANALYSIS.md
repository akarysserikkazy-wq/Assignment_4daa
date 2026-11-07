# Assignment 4 — analysis (complete in English)

## Environment and commands

- Language/runtime: Python 3.12.4
- OS / CPU / RAM: Windows 11, Intel Core i3-1315U, 8 GB RAM
- Setup: `python tools/run.py --setup`
- Public checks: `python tools/run.py --check` (44 public cases + repeated mixed batch: all PASS)
- Own tests: `python tests/student/test_student.py`
- Benchmark: `python tests/student/bench.py`
- Final commit URL is recorded in Moodle.

## Algorithm explanations

### lcs
- State: `dp[i][j]` = length of an LCS of the first `i` characters of `a` and the first `j` of `b`. Row 0 and column 0 are the base case (0).
- Transition: if `a[i-1]==b[j-1]` then `dp[i-1][j-1]+1`, else `max(dp[i-1][j], dp[i][j-1])`.
- Order: rows top to bottom; every cell depends only on the row above and the cell to the left, so dependencies are ready.
- Correctness: on a mismatch the last character of at least one string is unused, so the optimum is one of the two smaller subproblems; on a match, taking the character is never worse.
- Reconstruction: walk from `(n,m)`: on a match take the character and go diagonally; otherwise move to the larger neighbour (ties: up). Any optimal sequence is accepted.
- Time/memory: O(nm) / O(nm) (table of (n+1)(m+1) integers); output O(min(n,m)).
- Boundary test: either string empty -> length 0 and `""`; detects wrong base cases.

### merge
- State: `dp[l][r]` = minimum cost to merge the original blocks `l..r` into one, preserving order. `dp[i][i]=0`.
- Transition: `dp[l][r] = min over k in [l,r-1] of dp[l][k]+dp[k+1][r] + sum(sizes[l..r])` (prefix sums give the sum in O(1)). `k` is the last split.
- Order: by increasing interval length, so both sub-intervals are already computed.
- Correctness: the final merge joins `[l,k]` and `[k+1,r]` and pays the full interval size; the two parts are independent optimal subproblems.
- Reconstruction: the best `k` is stored in `split[l][r]`; an iterative post-order traversal emits `[l,k,r]` after the plans of both children (chronological order). `n-1` merges for `n>1`.
- Time/memory: O(n^3) / O(n^2); no recursion (depth is not a problem for n<=200 anyway).
- Boundary test: `sizes=[1,100,1]` has cost 203, not 104; detects non-adjacent greedy merging. `[1e9,1e9,1e9]` -> 5e9 checks large sums (Python ints are exact).

### tree
- State: `take[u]` = best weight in the subtree of `u` if `u` is selected; `skip[u]` = best weight if `u` is not selected. `take[u]=w[u]+sum(skip[c])`, `skip[u]=sum(max(take[c],skip[c]))`.
- Order: BFS from vertex 0 gives a parent array; processing the BFS order in reverse is a post-order, so children are done before parents. No recursion, so a 100000-vertex chain is safe.
- Answer: `max(take[root], skip[root])`; the empty set is allowed, so all-negative inputs give 0. The root choice only fixes the computation order, not the optimum.
- Reconstruction: top-down in BFS order: the root is selected iff `take>skip`; a child is selected only if its parent is not selected and `take[c]>skip[c]` (ties choose "skip").
- Time/memory: O(n) / O(n).
- Boundary test: deep chain of 100000 vertices (detects recursion failure); all-negative weights (detects forcing a selection).

### naive
- Try every start `i=0..n-m`, compare `j=0..m-1` character by character; report `i` when all `m` match. Overlaps are counted because every start is tested independently.
- Empty pattern: return `0..n` (n+1 boundaries). Pattern longer than text: empty list.
- Time O(nm + z); auxiliary memory O(1) plus output.
- Boundary test: `text="aaaa", pattern="aa"` -> `[0,1,2]`; detects missing the last start or skipping after a match.

### kmp
- `pi[i]` = length of the longest proper prefix of `pattern[0..i]` that is also its suffix.
- Search keeps `j` = matched prefix length. On a mismatch `j=pi[j-1]` (the text index does not move back); on a full match record `i-m+1` and set `j=pi[m-1]`, which keeps overlapping matches.
- Correctness: `pi` lists every border, so no possible match start is skipped by falling back to the longest border first.
- Time O(n+m+z), auxiliary memory O(m). Empty pattern returns `0..n` before any indexing.
- Boundary test: `text="abababa", pattern="aba"` -> `[0,2,4]`; detects resetting `j=0` after a match.

### rk
- Rolling polynomial hash, base 31, modulus 101, ASCII codes, leftmost character has the highest power. Slide: `h = ((h - ord(old)*31^(m-1))*31 + ord(new)) mod 101`; Python's `%` is non-negative, which normalizes negative remainders.
- Equal hashes are only candidates: every candidate is verified character by character before it is reported.
- Time: O(n+m+c*m) where `c` is the number of equal-hash windows. With modulus 101 collisions are frequent, and on repetitive inputs `c` can be about `n`, so the worst case is O(nm). No linear worst-case claim is made.
- Memory: O(1) auxiliary plus output (rolling window).
- Boundary test: `abdj` / `ab` (`ab` and `dj` both hash to 75) -> `[0]`; `bcek` / `bc` -> `[0]`. Detects reporting by hash equality alone.

### suffix
- Prefix doubling: ranks of the first `k` characters of each suffix; a round sorts suffixes by the pair `(rank[i], rank[i+k] or -1)` and assigns equal pairs equal ranks, then `k` doubles. Stops when all ranks are distinct. Comparison sorting gives O(n log^2 n) time overall (O(log n) rounds, each O(n log n)); memory O(n).
- Kasai: `rank[sa[i]]=i`; for suffixes in text order, compare with the previous suffix in `sa` starting from the previously known `h`, then do `h-=1`. The LCP of the next text suffix is at least `h-1`, so total character comparisons are O(n). `lcp[0]=0`.
- Repeated substring: `max(lcp)` is the longest substring occurring at two distinct starts (overlaps allowed); it is `text[sa[i]:sa[i]+lcp[i]]` for the best `i`; `""` if the maximum is 0.
- No sentinel and no empty suffix are used in the output.
- Boundary tests: empty text -> `[]`, `[]`, `""`; `"aaaa"` -> `lcp=[0,1,2,3]`, repeated `"aaa"` (overlapping occurrences).

### aho
- Trie of all patterns; `term[i]` is the trie state of pattern `i`, so duplicates share a state but keep separate output columns.
- Failure links by BFS: the link of a child is found by following the parent's failure chain until a state has the same edge. Transitions on a mismatch follow failure links while scanning the text (amortized O(|text|)).
- Counting: during scanning only the visit count of the current state is incremented. After the text, counts are propagated along failure links in reverse BFS order (`vis[fail[u]] += vis[u]`), so every pattern that is a suffix of a visited state is counted without iterating over matches.
- Each text starts with fresh state and counts (independent texts); an empty dictionary gives an empty row per text; no texts gives `[]`.
- Time: O(L + S + p) construction (dict-based transitions, alphabet 95), O(|text| + S + p) per text; memory O(S + p) plus output O(q*p).
- Boundary tests: patterns `["he","she","he"]` on `"sheshe"` -> `[2,2,2]` (suffix pattern and duplicate); empty text -> zeros.

## Own tests

Run: `python tests/student/test_student.py` (18 tests, expected: OK).

|Command|Input or fixture path|Expected result|Actual result / log|What it checks|
|---|---|---|---|---|
|lcs|`a="",b="abc"`|length 0, `""`|PASS|empty input base case|
|lcs|`tea_time` / `team`|length 4, `team`|PASS|subsequence, not substring|
|lcs|300 random small pairs|length equals brute force, valid witness|PASS|DP transition and reconstruction|
|merge|`[1,100,1]`|cost 203|PASS|adjacency is respected|
|merge|`[1e9,1e9,1e9]`|cost 5000000000|PASS|large sums|
|merge|`[]`, `[7]`|cost 0, empty plan|PASS|0/1 blocks|
|tree|chain of 100000 vertices|weight 50000, no adjacent chosen|PASS|no recursion failure|
|tree|all negative weights|weight 0, empty set|PASS|empty set allowed|
|naive/kmp/rk|500 random small cases|equal to slicing oracle|PASS|all three agree incl. overlaps|
|naive/kmp/rk|empty pattern, `abc`|`[0,1,2,3]`|PASS|n+1 boundaries|
|rk|`abdj`/`ab`, `bcek`/`bc`|`[0]`|PASS|hash collision is rejected|
|suffix|`banana`|sa `[5,3,1,0,4,2]`, lcp `[0,1,3,0,0,2]`|PASS|doubling + Kasai|
|suffix|empty, `$`, `aaaa`|see tests|PASS|edges, no sentinel|
|suffix|300 random strings|sa equals sorting suffixes directly|PASS|independent oracle|
|aho|`he, she, he` on `sheshe`|`[2,2,2]`|PASS|suffix patterns, duplicates|
|aho|empty dictionary / no texts|`[[],[]]` / `[]`|PASS|empty cases|
|aho|300 random cases|equal to per-pattern occurrence counts|PASS|overlaps, reset between texts|


## Search comparison

Command: `python tests/student/bench.py` (same inputs for naive/KMP/RK; correctness of identical outputs is checked before timing, outside the timed region). Timed scope: one call of the algorithm function on an already-parsed request (no JSON parsing, no process start). One untimed warm-up call, then 3 timed runs with `time.perf_counter`; Python has no JIT. Cases: `random` (alphabet `abcd`, pattern copied from the text, m=n/10) and `repetitive` (text `a`*n, pattern `a`*(m-1)+`b`, m=n/3, no full match). Seeds are in the table.

# Python 3.14.8 | Windows-11-10.0.26300-SP0 | Intel64 Family 6 Model 186 Stepping 3, GenuineIntel
|Case|n|m|Seed/generator|Algorithm|Run 1 (ms)|Run 2 (ms)|Run 3 (ms)|Median (ms)|Correct outputs checked|
|---|---:|---:|---|---|---:|---:|---:|---:|---|
|random|500|50|seed 12845, random|naive|0.093|0.094|0.093|0.093|identical, 1 starts|
|random|500|50|seed 12845, random|kmp|0.058|0.054|0.054|0.054|identical, 1 starts|
|random|500|50|seed 12845, random|rk|0.098|0.098|0.097|0.098|identical, 1 starts|
|random|1000|100|seed 13345, random|naive|0.126|0.119|0.118|0.119|identical, 1 starts|
|random|1000|100|seed 13345, random|kmp|0.111|0.110|0.110|0.110|identical, 1 starts|
|random|1000|100|seed 13345, random|rk|0.198|0.262|0.196|0.198|identical, 1 starts|
|random|3000|300|seed 15345, random|naive|0.350|0.328|0.349|0.349|identical, 1 starts|
|random|3000|300|seed 15345, random|kmp|0.387|0.318|0.302|0.318|identical, 1 starts|
|random|3000|300|seed 15345, random|rk|0.599|0.594|0.582|0.594|identical, 1 starts|
|repetitive|500|166|seed 12845, repetitive|naive|3.790|4.882|5.867|4.882|identical, 0 starts|
|repetitive|500|166|seed 12845, repetitive|kmp|0.161|0.160|0.159|0.160|identical, 0 starts|
|repetitive|500|166|seed 12845, repetitive|rk|0.155|0.155|0.156|0.155|identical, 0 starts|
|repetitive|1000|333|seed 13345, repetitive|naive|16.624|16.404|16.904|16.624|identical, 0 starts|
|repetitive|1000|333|seed 13345, repetitive|kmp|0.245|0.245|0.240|0.245|identical, 0 starts|
|repetitive|1000|333|seed 13345, repetitive|rk|0.204|0.212|0.224|0.212|identical, 0 starts|
|repetitive|3000|1000|seed 15345, repetitive|naive|178.320|193.959|172.040|178.320|identical, 0 starts|
|repetitive|3000|1000|seed 15345, repetitive|kmp|0.689|0.684|0.714|0.689|identical, 0 starts|
|repetitive|3000|1000|seed 15345, repetitive|rk|0.633|0.827|0.656|0.656|identical, 0 starts|

Observations: On random text all three algorithms finish in well under 1 ms. KMP and naive are almost equal because naive usually rejects a window after the first mismatch; RK is about 1.7-2 times slower because it updates a hash at every position. On the repetitive text naive becomes much slower (4.9 ms, 16.6 ms and 178 ms for n=500, 1000 and 3000), which is consistent with its O(n*m) worst case (a pattern of the form a...ab fails only at the last character of each window), while KMP (0.16, 0.25, 0.69 ms) grows roughly linearly. RK is as fast as KMP here only because the hash of the pattern a...ab always differs from the hash of a window a...a, so there are no equal-hash candidates and no character comparisons. This benchmark does not exercise the RK worst case: when many windows have equal hashes (collisions with modulus 101, or many real matches), every candidate costs O(m) to verify and the time can become O(n*m). The measurements are only three sizes with three runs each on one computer, so they illustrate the behaviour but do not prove the asymptotic complexity.

## Sources and AI assistance

- Sources: course lectures (Week 8-10), the A4 specification and `docs/guide/*`, practice questions.
- AI assistance: I used Claude as an assistant to implement eight functions in Python, my own tests, and a test scenario. He explained which function to use in these cases, but I wrote the code myself. I ran python tools/run.py --check (all 44 open examples passed the check) and my own tests (18 tests passed). I studied each algorithm to be able to explain its state, transitions, correctness, and complexity. The benchmark results were obtained from my own tests on my own computer.
