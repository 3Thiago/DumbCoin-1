from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pkcs1_15
import ast
import binascii
import hashlib

class Signature(object):
    def generate_keys(self):
        # return secret_key, public_key
        pass

    def sign(message, secret_key):
        # so your signature should probably do: `priv_key.encrypt(hash(to, from, amount))
        pass

    def verify(public_key, message, signature):
        # and verify should roughly check: pub_key.decrypt(signature) == hash(to, from, amount)
        pass




def bin2hex(binStr):
    return binascii.hexlify(binStr)

def hex2bin(hexStr):
    return binascii.unhexlify(hexStr)



if __name__ == "__main__":
    # Experimenting with pycryptodome Library
    # Using video: https://www.youtube.com/watch?v=OKg4PqD01Z0
    # and: https://stackoverflow.com/questions/21327491/using-pycrypto-how-to-import-a-rsa-public-key-and-use-it-to-encrypt-a-string/26988465#26988465

    key = RSA.generate(2048)

    message = b"This is the message"
    tampered_message = b"This i th message"

    binary_public_key = key.exportKey('DER')
    binary_private_key = key.publickey().exportKey('DER')

    public_cipher = PKCS1_OAEP.new(key)
    private_cipher = PKCS1_OAEP.new(key.publickey())

    encrypted = public_cipher.encrypt(tampered_message)

    sig = private_cipher.encrypt(message)

    decrypted_message = public_cipher.decrypt(ast.literal_eval(str(encrypted)))

    decrypted_signature = public_cipher.decrypt(ast.literal_eval(str(sig)))


    print("This is the signature: %s" % bin2hex(sig))
    print("")
    print("This is the encrypted message: %s" % bin2hex(encrypted))
    print("")
    print("Decrypted signature: %s" % decrypted_signature)
    print("")
    print("Decrypted message: %s" % decrypted_message)

    if decrypted_signature == decrypted_message:
        print("Holy shit, the signature is valid!")
    else:
        print("Signature is NOT valid!")
