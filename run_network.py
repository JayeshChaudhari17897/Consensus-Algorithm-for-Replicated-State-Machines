from random_generator import randrange
from pro650_nacl.signing import SigningKey
from Node import Node
from pro650_nacl.signing import SigningKey

def run_network(n_nodes, n_turns):
    signing_keys = [SigningKey.generate() for _ in range(n_nodes)]

    for singing_key in signing_keys:
        print(singing_key)


    network = {}
    stake = {signing_key.verify_key: 1 for signing_key in signing_keys}
    nodes = [Node(signing_key, network, n_nodes, stake) for signing_key in signing_keys]
    for n in nodes:
        network[n.id] = n.ask_sync
    mains = [n.main() for n in nodes]
    for m in mains:
        next(m)
    for i in range(n_turns):
        r = randrange(n_nodes)
        print("Event no - %i   Node working - %i" % ( i,r))
        next(mains[r])
    return nodes

