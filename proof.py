import hashlib
from random import choice, randint
from string import ascii_letters, digits

def mint(challenge, work_factor):
    nonce = 0
    while True:
        # convert nonce to string to append to header
        nonce_str = str(nonce)
        # check if our guess produces the desired hash
        if verify(challenge, work_factor, nonce_str):
            return nonce_str
        nonce += 1


def verify(challenge, work_factor, nonce):
    # create properly-formatted header
    full_header = challenge + nonce
    # get SHA256 hash of header
    h = hashlib.sha256()
    h.update(full_header.encode('utf-8'))
    hash_output = h.hexdigest()
    # check if hash starts with sufficient 0's
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
    nonce = mint(challenge, work_factor)
