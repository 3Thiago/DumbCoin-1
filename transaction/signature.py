import rsa
import base64
import hashlib

class Signature(object):
    # * generates keys and returns them as a string of the DER format *
    def generate_keys(length=2048):
        print("Generating keys...")
        pub_key, priv_key = rsa.newkeys(length)
        pub_key_b64 = base64.b64encode(pub_key.save_pkcs1(format='DER'))
        priv_key_b64 = base64.b64encode(priv_key.save_pkcs1(format='DER'))
        return pub_key_b64.decode('utf-8'), priv_key_b64.decode('utf-8')

    # * hashes the message, signs the hash, returns b64 string of signature *
    def sign(message, secret_key):
        msg_bytes = message.encode('utf-8')
        sk_bytes = secret_key.encode('utf-8')
        sk_object = rsa.PrivateKey.load_pkcs1(base64.b64decode(sk_bytes), format='DER')
        signature = rsa.sign(msg_bytes, sk_object, 'SHA-256')
        return base64.b64encode(signature).decode('utf-8')

    # * verifies that signature was created from secret key *
    def verify(public_key, message, signature):
        # convert from string to bytes...
        pk_bytes = public_key.encode('utf-8')
        sig_bytes = signature.encode('utf-8')
        msg = message.encode('utf-8')
        # ...to DER value
        pk_decoded = base64.b64decode(pk_bytes)
        sig_decoded = base64.b64decode(sig_bytes)

        pk_object = rsa.PublicKey.load_pkcs1(pk_decoded, format='DER')

        isValid = False
        try:
            # using rsa library's verify function for convenience
            isValid = rsa.verify(msg, sig_decoded, pk_object)
            if isValid:
                print("signature is valid!")
        except:
            print("signature is not valid!")
        return isValid



if __name__ == "__main__":

    msg = "This is the data we we'll sign!"

    pk, sk = Signature.generate_keys()

    signature = Signature.sign(msg,sk)
    print("Successfully signed with signature: %s" % signature)

    print("Verifying signature...")
    Signature.verify(pk, msg, signature)

    # The following is a simple working example
    #
    # message = "Go left at the blue tree".encode('utf-8')
    #
    # print("Message: %s" % message)
    # print("Type: %s" % type(message))
    #
    # (pubkey, privkey) = rsa.newkeys(1024)
    # signature = rsa.sign(message, privkey, 'SHA-1')
    #
    # print("Signature: %s" % signature)
    #
    # if rsa.verify(message, signature, pubkey):
    #     print("Signature is valid!")
    # else:
    #     print("Signature is not valid!")
