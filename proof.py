import hashlib
from random import choice
from string import ascii_letters

def mint(challenge, work_factor):

    while True:
        # generate random token - create full test string
        token = generate_random_string()
        input_string = str(challenge) + "||" + token

        # run through hash function
        h = hashlib.sha256()
        h.update(input_string.encode('utf-8'))
        hash_output = h.hexdigest()

        print("Token: %s" % token)
        print("Hash Output: %s" % hash_output)

        # check if output matches desired work_factor
        if verify_hash(hash_output, work_factor):
            print("FOUND THE MAGIC TOKEN")
            return hash_output


def verify_hash(hash_string, work_factor):
    for i in range(0, work_factor):
        if not hash_string[i] == str(0):
            return False
    return True


def generate_random_string(length=10):
    return (''.join(choice(ascii_letters) for i in range(length)))


mint(431, 3)
