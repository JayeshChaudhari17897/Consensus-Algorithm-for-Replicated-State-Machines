
from collections import defaultdict
from eve import Event
from pickle import dumps,loads
from itertools import zip_longest
from maj import majority
from functools import reduce
from bfs import bfs
from dfs import dfs
from topsort import toposort
from random_generator import randrange
from nacl.bindings import crypto_sign
from signing import VerifyKey,SigningKey



C = 6
class Node:

    def __init__(self, signing_key, network, no_of_nodes, stake):

        self.no_of_nodes = no_of_nodes
        self.stake_of_this_node = stake
        self.total_stake = sum(stake.values())
        self.min_stake =  (2 * self.total_stake)/3

        self.signing_key = signing_key
        self.network = network


        self.hashgraph = {}
        self.head = None
        self.round_nos_of_all_events = {}
        self.rounds_to_be_decided = set()
        self.all_ordered_transactions= []
        self.idx = {}
        self.height = {}


        self.votes = defaultdict(dict)
        self.witnesses = defaultdict(dict)
        self.famous = {}
        self.can_see = {}

        @property
        def id(self):
            #assert isinstance(self.signing_key.verify_key,)
            return self.signing_key.verify_key

        def new_event(self, d, parents):
            assert parents == () or len(parents) == 2
            assert parents == () or self.hashgraph[parents[0]].verify_key == self.id
            assert parents == () or self.hashgraph[parents[1]].verify_key != self.id

            ev = Event(d, parents)
            ev.sign(self.signing_key)

            return ev

        def is_valid_event(self, h, event: Event):
            try:
                event.verify_key.verify(event.description, event.signature)
            except ValueError:
                return False

            return (event.sha512 == h and (event.parents == () or (len(event.parents) == 2 and event.parents[0] in self.hg and event.parents[1] in self.hg and self.hg[event.parents[0]].verify_key == event.verify_key and self.hg[event.parents[1]].verify_key != event.verify_key)))

        def add_event(self, ev: Event):
            h = ev.sha512
            self.hashgraph[h] = ev
            self.rounds_to_be_decided.add(h)
            if ev.parents == ():
                self.height[h] = 0
            else:
                self.height[h] = max(self.height[parent] for parent in ev.parents) + 1

        def sync(self, node_id, payload):

            message = dumps({c: self.height[h] for c, h in self.can_see[self.head].items()})
            signed_message = self.signing_key.sign(message)
            signed_reply = self.network[node_id](self.id, signed_message)
            serialized_reply = node_id.verify(signed_reply)

            remote_head, remote_hg = loads(serialized_reply)
            new = tuple(toposort(remote_hg.keys() - self.hashgraph.keys(),
                                 lambda u: remote_hg[u].parents))

            for h in new:
                ev = remote_hg[h]
                if self.is_valid_event(h, ev):
                    self.add_event(ev)

            if self.is_valid_event(remote_head, remote_hg[remote_head]):
                ev = self.new_event(payload, (self.head, remote_head))
                self.add_event(ev)
                self.head = ev.sha512
                h = ev.sha512

            return new + (h,)

        def ask_sync (self, pk, info):

            msg = pk.verify(info)
            cs = loads(msg)

            subset = {h: self.hg[h] for h in bfs(
                (self.head,),
                lambda u: (p for p in self.hg[u].parents
                           if self.hg[p].verify_key not in cs or self.height[p] > cs[self.hg[p].verify_key]))}
            msg = dumps((self.head, subset))

            return self.signing_key.sign(msg)

        def ancestors(self, c):
            while True:
                yield c
                if not self.hashgraphashgraph[c].parents:
                    return
                c = self.hashgraph[c].parents[0]

        def maxi(self, a, b):
            if self.higher(a, b):
                return a
            else:
                return b

        def _higher(self, a, b):
            for x, y in zip_longest(self.ancestors(a), self.ancestors(b)):
                if x == b or y is None:
                    return True
                elif y == a or x is None:
                    return False

        def higher(self, a, b):
            return a is not None and (b is None or self.height[a] >= self.height[b])

        def divide_rounds(self, events):
            for h in events:
                ev = self.hashgraph[h]
                if ev.parents == ():  # this is a root event
                    self.round[h] = 0
                    self.witnesses[0][ev.verify_key] = h
                    self.can_see[h] = {ev.verify_key: h}
                else:
                    r = max(self.round[p] for p in ev.parents)


                    p0, p1 = (self.can_see[p] for p in ev.parents)
                    self.can_see[h] = {c: self.maxi(p0.get(c), p1.get(c))
                                       for c in p0.keys() | p1.keys()}
                    hits = defaultdict(int)
                    for c, k in self.can_see[h].items():
                        if self.round[k] == r:
                            for c_, k_ in self.can_see[k].items():
                                if self.round[k_] == r:
                                    hits[c_] += self.stake[c]
                    # check if i can strongly see enough events
                    if sum(1 for x in hits.values() if x > self.min_s) > self.min_s:
                        self.round[h] = r + 1
                    else:
                        self.round[h] = r
                    self.can_see[h][ev.verify_key] = h
                    if self.round[h] > self.round[ev.parents[0]]:
                        self.witnesses[self.round[h]][ev.verify_key] = h

        def decide_fame(self):
            max_r = max(self.witnesses)
            max_c = 0
            while max_c in self.consensus:
                max_c += 1

            # helpers to keep code clean
            def iter_undetermined(r_):
                for r in range(max_c, r_):
                    if r not in self.consensus:
                        for w in self.witnesses[r].values():
                            if w not in self.famous:
                                yield r, w

            def iter_voters():
                for r_ in range(max_c + 1, max_r + 1):
                    for w in self.witnesses[r_].values():
                        yield r_, w

            done = set()

            for r_, y in iter_voters():

                hits = defaultdict(int)
                for c, k in self.can_see[y].items():
                    if self.round[k] == r_ - 1:
                        for c_, k_ in self.can_see[k].items():
                            if self.round[k_] == r_ - 1:
                                hits[c_] += self.stake[c]
                s = {self.witnesses[r_ - 1][c] for c, n in hits.items()
                     if n > self.min_s}

                for r, x in iter_undetermined(r_):
                    if r_ - r == 1:
                        self.votes[y][x] = x in s
                    else:
                        v, t = majority((self.stake[self.hashgraph[w].verify_key], self.votes[w][x]) for w in s)
                        if (r_ - r) % C != 0:
                            if t > self.min_s:
                                self.famous[x] = v
                                done.add(r)
                            else:
                                self.votes[y][x] = v
                        else:
                            if t > self.min_s:
                                self.votes[y][x] = v
                            else:
                                
                                self.votes[y][x] = bool(self.hashgraph[y].signature[0] // 128)

            new_c = {r for r in done
                     if all(w in self.famous for w in self.witnesses[r].values())}
            self.consensus |= new_c
            return new_c

        def find_order(self, new_c):
            to_int = lambda x: int.from_bytes(self.hashgraph[x].signature, byteorder='big')

            for r in sorted(new_c):
                f_w = {w for w in self.witnesses[r].values() if self.famous[w]}
                white = reduce(lambda a, b: a ^ to_int(b), f_w, 0)
                ts = {}
                seen = set()
                for x in bfs(filter(self.tbd.__contains__, f_w),
                             lambda u: (p for p in self.hashgraph[u].parents if p in self.tbd)):
                    c = self.hashgraph[x].verify_key
                    s = {w for w in f_w if c in self.can_see[w]
                         and self.higher(self.can_see[w][c], x)}
                    if sum(self.stake[self.hashgraph[w].verify_key] for w in s) > self.tot_stake / 2:
                        self.tbd.remove(x)
                        seen.add(x)
                        times = []
                        for w in s:
                            a = w
                            while (c in self.can_see[a]
                                   and self.higher(self.can_see[a][c], x)
                                   and self.hashgraph[a].parents):
                                a = self.hashgraph[a].p[0]
                            times.append(self.hashgraph[a].t)
                        times.sort()
                        ts[x] = .5 * (times[len(times) // 2] + times[(len(times) + 1) // 2])
                final = sorted(seen, key=lambda x: (ts[x], white ^ to_int(x)))
                for i, x in enumerate(final):
                    self.idx[x] = i + len(self.transactions)
                self.transactions += final
            if self.consensus:
                print(self.consensus)

        def main(self):
            

            new = ()
            while True:
                payload = (yield new)

                
                node_id = tuple(self.network.keys() - {self.id})[randrange(self.n - 1)]
                new = self.sync(node_id, payload)
                self.divide_rounds(new)

                new_c = self.decide_fame()
                self.find_order(new_c)











