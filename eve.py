#Author - Jayesh Chaudhari
#python version used 3.5.2
#pycharm2017 edition

import datetime
import  pickle

from nacl.hash import sha512

class Event():

    def __init__(self,d, parents , timestamp = None):
        self.d = d
        self.parents = parents
        if timestamp is None:
            self.timestamp = datetime.datetime.now()
        else :
            self.timestamp = timestamp

        self.verify_key = None
        self.signature = None


    @property
    def description(self):
        return pickle.dumps((self.d,self.parents,self.verify_key , self.timestamp))

    def sign(self , signing_key):
        self.verify_key = signing_key.verify_key
        #   print(self.verify_key)

    def  __getstate__(self):
        return self.d, self.parents, self.timestamp , self.verify_key, self. signature

    def __setstate__(self, state):

       # assert isinstance(state, self)
        self.d, self.parents, self.timestamp, self.verify_key, self.signature = state

    @property
    def sha512(self):
        return sha512(pickle.dumps(self))















