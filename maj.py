def majority(it):
    hits = [0, 0]
    for s, x in it:
        hits[int(x)] += s
    if hits[0] > hits[1]:
        return False, hits[0]
    else:
        return True, hits[1]
