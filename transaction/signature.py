from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pkcs1_15

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
    secret_key = keyPair.exportKey()
    pubKey = keyPair.publickey()

    # imagine I'm a random person encrypting data for public key above...
    data_to_encrypt = b"Encryption is deceptively hard."
    recipient_key = pubKey

    # Encrypt data with the public RSA key
    sender_cipher_AES = AES.new(pubKey.exportKey(), AES.MODE_EAX)
    encrypted_data = sender_cipher_AES.encrypt_and_digest(data_to_encrypt)

    recipient_cipher_rsa = PKCS1_OAEP.new(secret_key)
    decrypted_data = recipient_cipher_rsa.decrypt(encrypted_data)


    print("Secret key is: %s" % secret_key)
    print("")
    print("Public key is: %s" % pubKey.exportKey())
    print("")
    print("Encrypted data is: %s" % encrypted_data)
    print("")
    print("Decrypted data is: %s" % decrypted_data)


'''
    data_to_sign = b"This is a sample transaction"

    hashA = SHA256.new(data_to_sign)

    signature = pkcs1_15.new(keyPair).sign(hashA)

    print("Hash of transaction: %s" % hashA)
    print("Signature: %s" % signature)

    data_to_verify = b"This is a sample transaction"

    if pkcs1_15.new(pubKey).verify(hashA, signature):
        print("Signature is valid!")
    else:
        print("Signature is not valid!")

        '''
