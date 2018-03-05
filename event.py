import datetime
import pickle
from nacl.hash import sha512



class Event(object):

    def __init__(self, d, parents, t=None):
        self.d = d
        self.parents = parents
        self.t = datetime.datetime.now() if t is None else t
        self.verify_key = None
        self.signature = None

    @property
    def description(self):
        return pickle.dumps((self.d, self.parents, self.t, self.verify_key))

    def sign(self, signing_key):
        self.verify_key = signing_key.verify_key
        signature = signing_key.sign(self.description).signature
        self.signature = signature

    def __getstate__(self):
        return self.d, self.parents, self.t, self.verify_key, self.signature

    def __setstate__(self, state):
        self.d, self.parents, self.t, self.verify_key, self.signature = state

    @property
    def sha512(self):
        return sha512(pickle.dumps(self))