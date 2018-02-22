import hashlib
from random import choice
from string import ascii_letters, digits

class Signature(object):
    def generate_keys(self):

        # choose arbitrary string length + character set
        string_length = 64
        chars = ascii_letters + digits

        # generate random strings
        public_key = ''.join([choice(chars) for n in range(string_length)])
        secret_key = ''.join([choice(chars) for n in range(string_length)])

        # hash strings
        h1, h2 = hashlib.sha256(), hashlib.sha256(),
        h1.update(public_key.encode('utf-8'))
        h2.update(secret_key.encode('utf-8'))
        public_key, secret_key = h1.hexdigest(), h2.hexdigest()

        return public_key, secret_key

    def sign(message, secret_key):
        message = str(message) # ensure message is a string
        h = hashlib.sha256()
        h.update((message + secret_key).encode('utf-8'))
        return h.hexdigest()

    def verify(public_key, message, signature):
        # return isValid (Bool)
        pass


if __name__ == "__main__":
    print("Generating public and private keys...")
    pk, sk = Signature().generate_keys()
    print("Public key: %s" % pk)
    print("Secret key: %s" % sk)
