from random import choice
from random import randint
from string import ascii_letters
from string import digits

import hashlib


def mint(challenge, work_factor):
    nonce = 0
    while True:
        nonce_str = str(nonce)
        if verify(challenge, work_factor, nonce_str):  # ensure nonce is correct
            return nonce_str
        nonce += 1

def verify(challenge, work_factor, nonce):
    """Checks if nonce starts with sufficient 0's"""

    full_header = challenge + nonce
    h = hashlib.sha256()
    h.update(full_header.encode("utf-8"))
    hash_output = h.hexdigest()
    for i in range(0, work_factor):  
        if not hash_output[i] == str(0):
            return False
    return True

def generate_challenge_string(length=16):
    chars = ascii_letters + digits
    return ''.join([choice(chars) for n in range(length)])



if __name__ == '__main__':

    work_factor = 4
    challenge = generate_challenge_string()

    print("Challenge: %s" % challenge)
    print("Mining...")

    nonce = mint(challenge, work_factor)
    
    print("Nonce: %s" % nonce)
