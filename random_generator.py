from nacl.utils import  random
def randrange(n):
    a = (n.bit_length() + 7) // 8  # number of bytes to store n
    b = 8 * a - n.bit_length()     # number of shifts to have good bit number
    r = int.from_bytes(random(a), byteorder='big') >> b
    while r >= n:
        r = int.from_bytes(random(a), byteorder='big') >> b
    return r