def toposort(nodes, parents):
    seen = {}
    def visit(u):
        if u in seen:
            if seen[u] == 0:
                raise ValueError('not a DAG')
        elif u in nodes:
            seen[u] = 0
            for v in parents(u):
                yield from visit(v)
            seen[u] = 1
            yield u
    for u in nodes:
        yield from visit(u)