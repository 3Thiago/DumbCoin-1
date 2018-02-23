from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Signature
from Crypto import Random

class Signature(object):
    def generate_keys(self):
        # return secret_key, public_key
        pass

    def sign(message, secret_key):
        # should do: secret_key.encrypt(message)
        pass

    def verify(public_key, message, signature):
        # should do: public_key.decrypt(signature) == message
        pass


if __name__ == "__main__":
    # Experimenting with pycryptodome Library
    # Using video: https://www.youtube.com/watch?v=OKg4PqD01Z0

    random_generator = Random.new().read
    keyPair = RSA.generate(1024, random_generator)
    pubKey = keyPair.publickey()

    data_to_sign = "This is a sample transaction".encode('utf-8')

    hashA = SHA256.new(data_to_sign).digest()
    signature = keyPair.sign(hashA, '')

    print("Hash of transaction: %s" % hashA)
    print("Signature: %s" % repr(signature))

    data_to_verify = "This is a sample transaction".encode('utf-8')

    if pubKey.verify(hashA, signature):
        print("Signature is valid!")
    else:
        print("Signature is not valid!")
