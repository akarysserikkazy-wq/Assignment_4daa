"""Implement algorithm bodies. See docs/guide/CONTRACTS.md; inputs and outputs are dictionaries."""
from collections import deque

def lcs(request):
    """Compare two versions of a sequence while preserving the order of shared characters. Implement lcs according to docs/guide/CONTRACTS.md."""
    a, b = request["a"], request["b"]
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        ai, row, prev = a[i - 1], dp[i], dp[i - 1]
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                row[j] = prev[j - 1] + 1
            else:
                row[j] = prev[j] if prev[j] >= row[j - 1] else row[j - 1]
    out = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return {"length": dp[n][m], "sequence": "".join(reversed(out))}

def merge(request):
    """Plan the cheapest sequence of adjacent block merges when the original order must be preserved. Implement merge according to docs/guide/CONTRACTS.md."""
    s = request["sizes"]
    n = len(s)
    if n <= 1:
        return {"cost": 0, "plan": []}
    pre = [0]
    for x in s:
        pre.append(pre[-1] + x)
    INF = float("inf")
    dp = [[0] * n for _ in range(n)]
    sp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for l in range(0, n - length + 1):
            r = l + length - 1
            best, bk = INF, l
            for k in range(l, r):
                c = dp[l][k] + dp[k + 1][r]
                if c < best:
                    best, bk = c, k
            dp[l][r] = best + pre[r + 1] - pre[l]
            sp[l][r] = bk
    plan = []
    # iterative post-order: children's merges come before the parent's
    stack = [(0, n - 1, False)]
    while stack:
        l, r, done = stack.pop()
        if l == r:
            continue
        k = sp[l][r]
        if done:
            plan.append([l, k, r])
        else:
            stack.append((l, r, True))
            stack.append((k + 1, r, False))
            stack.append((l, k, False))
    return {"cost": dp[0][n - 1], "plan": plan}

def tree(request):
    """Choose a maximum-value set when neighbouring vertices are incompatible and conflicts form a tree. Implement tree according to docs/guide/CONTRACTS.md."""
    n = request["n"]
    if n == 0:
        return {"weight": 0, "selected": []}
    w = request["weights"]
    adj = [[] for _ in range(n)]
    for u, v in request["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    parent = [-1] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    for u in order:  # BFS (list grows while iterating)
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                order.append(v)
    take = [w[i] for i in range(n)]
    skip = [0] * n
    for u in reversed(order):
        p = parent[u]
        if p >= 0:
            take[p] += skip[u]
            skip[p] += max(take[u], skip[u])
    chosen = [False] * n
    chosen[0] = take[0] > skip[0]
    for u in order[1:]:
        p = parent[u]
        chosen[u] = (not chosen[p]) and take[u] > skip[u]
    return {"weight": max(take[0], skip[0]),
            "selected": [i for i in range(n) if chosen[i]]}

def naive(request):
    """Establish a simple exact-search baseline against which the other two searches can be checked. Implement naive according to docs/guide/CONTRACTS.md."""
    t, p = request["text"], request["pattern"]
    n, m = len(t), len(p)
    if m == 0:
        return {"positions": list(range(n + 1))}
    res = []
    for i in range(n - m + 1):
        j = 0
        while j < m and t[i + j] == p[j]:
            j += 1
        if j == m:
            res.append(i)
    return {"positions": res}

def kmp(request):
    """Reuse information about matched prefixes to avoid restarting the search after every mismatch. Implement kmp according to docs/guide/CONTRACTS.md."""
    t, p = request["text"], request["pattern"]
    n, m = len(t), len(p)
    if m == 0:
        return {"positions": list(range(n + 1))}
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k and p[i] != p[k]:
            k = pi[k - 1]
        if p[i] == p[k]:
            k += 1
        pi[i] = k
    res = []
    j = 0
    for i in range(n):
        while j and t[i] != p[j]:
            j = pi[j - 1]
        if t[i] == p[j]:
            j += 1
        if j == m:
            res.append(i - m + 1)
            j = pi[m - 1]
    return {"positions": res}

def rk(request):
    """Reject windows with unequal fingerprints and verify every equal-hash candidate. Implement rk according to docs/guide/CONTRACTS.md."""
    t, p = request["text"], request["pattern"]
    n, m = len(t), len(p)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}
    B, M = 31, 101
    hp = hw = 0
    for i in range(m):
        hp = (hp * B + ord(p[i])) % M
        hw = (hw * B + ord(t[i])) % M
    high = pow(B, m - 1, M)
    res = []
    for i in range(n - m + 1):
        if hw == hp:
            j = 0
            while j < m and t[i + j] == p[j]:
                j += 1
            if j == m:
                res.append(i)
        if i + m < n:
            hw = ((hw - ord(t[i]) * high) * B + ord(t[i + m])) % M  # Python % is non-negative
    return {"positions": res}

def suffix(request):
    """Order the text suffixes and use adjacent common prefixes to find repeated substrings. Implement suffix according to docs/guide/CONTRACTS.md."""
    t = request["text"]
    n = len(t)
    if n == 0:
        return {"sa": [], "lcp": [], "repeated": ""}
    rank = [ord(c) for c in t]
    sa = sorted(range(n), key=rank.__getitem__)
    new = [0] * n
    for idx in range(1, n):
        new[sa[idx]] = new[sa[idx - 1]] + (rank[sa[idx]] != rank[sa[idx - 1]])
    rank = new
    k = 1
    while rank[sa[-1]] < n - 1 and k < n:
        base = n + 2
        keys = [rank[i] * base + (rank[i + k] + 1 if i + k < n else 0) for i in range(n)]
        sa.sort(key=keys.__getitem__)
        new = [0] * n
        for idx in range(1, n):
            new[sa[idx]] = new[sa[idx - 1]] + (keys[sa[idx]] != keys[sa[idx - 1]])
        rank = new
        k <<= 1
    # Kasai
    rk_ = [0] * n
    for i, s in enumerate(sa):
        rk_[s] = i
    lcp = [0] * n
    h = 0
    for i in range(n):
        r = rk_[i]
        if r > 0:
            j = sa[r - 1]
            while i + h < n and j + h < n and t[i + h] == t[j + h]:
                h += 1
            lcp[r] = h
            if h > 0:
                h -= 1
        else:
            h = 0
    best = max(range(n), key=lcp.__getitem__)
    L = lcp[best]
    rep = t[sa[best]:sa[best] + L] if L > 0 else ""
    return {"sa": sa, "lcp": lcp, "repeated": rep}

def aho(request):
    """Build one dictionary automaton and count its patterns in several independent texts. Implement aho according to docs/guide/CONTRACTS.md."""
    pats, texts = request["patterns"], request["texts"]
    go = [{}]
    term = []
    for p in pats:
        s = 0
        for ch in p:
            nxt = go[s].get(ch)
            if nxt is None:
                go.append({})
                nxt = len(go) - 1
                go[s][ch] = nxt
            s = nxt
        term.append(s)
    S = len(go)
    fail = [0] * S
    order = []
    q = deque()
    for v in go[0].values():
        q.append(v)
    while q:
        u = q.popleft()
        order.append(u)
        for ch, v in go[u].items():
            f = fail[u]
            while f and ch not in go[f]:
                f = fail[f]
            fail[v] = go[f].get(ch, 0)
            q.append(v)
    rev = order[::-1]
    counts = []
    for text in texts:
        vis = [0] * S
        st = 0
        for ch in text:
            while st and ch not in go[st]:
                st = fail[st]
            st = go[st].get(ch, 0)
            vis[st] += 1
        for u in rev:
            vis[fail[u]] += vis[u]
        counts.append([vis[term[i]] for i in range(len(pats))])
    return {"counts": counts}
