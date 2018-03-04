from collections import deque

def bfs(s, succ):
    s = tuple(s)
    seen = set(s)
    q = deque(s)
    while q:
        u = q.popleft()
        yield u
        for v in succ(u):
            if not v in seen:
                seen.add(v)
                q.append(v)