import hashlib
from random import choice, randint
from string import ascii_letters

def mint(challenge, work_factor):

    nonce = 0

    while True:

        # convert nonce to string to append to header
        token = str(nonce)

        # check if our guess produces the desired hash
        if verify(challenge, work_factor, token):
            print("FOUND THE MAGIC TOKEN")
            print("On attempt number %s" % nonce)
            return token

        nonce += 1


def verify(challenge, work_factor, token):

    # create properly-formatted header
    full_header = str(challenge) + "||" + token

    # get SHA256 hash of header
    h = hashlib.sha256()
    h.update(full_header.encode('utf-8'))
    hash_output = h.hexdigest()

    # check if hash starts with sufficient 0's
    for i in range(0, work_factor):
        if not hash_output[i] == str(0):
            return False
    return True



if __name__ == '__main__':

    challenge = randint(0, 1000000000)
    work_factor = 4
    mint(challenge, work_factor)
