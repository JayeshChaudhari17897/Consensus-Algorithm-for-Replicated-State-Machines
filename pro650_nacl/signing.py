from nacl import encoding
from nacl.signing import SignedMessage as pynacl_SignedMessage, \
    VerifyKey as pynacl_VerifyKey, SigningKey as pynacl_SigningKey


class SignedMessage(pynacl_SignedMessage):
    pass


class VerifyKey(pynacl_VerifyKey):

    def __bytes__(self):
        return self._key

    def __str__(self):
        return "VerifyKey(key={})".format(self.encode(encoding.Base64Encoder).decode('utf8'))

    def __eq__(self, other):
        return self._key == other._key

    def __hash__(self):
        return hash(self._key)


class SigningKey(pynacl_SigningKey):
    def __init__(self, seed, encoder=encoding.RawEncoder):
        super(SigningKey, self).__init__(seed, encoder)
        self.verify_key = VerifyKey(self.verify_key._key, encoder=encoding.RawEncoder)

    def __bytes__(self):
        return self._seed

    def __str__(self):
        return "SigningKey(seed={})".format(self.encode(encoding.Base64Encoder).decode('utf8'))

    def __eq__(self, other):
        return self._seed == other._seed

    def __hash__(self):
        return hash(self._seed)
