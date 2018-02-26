import rsa
import base64

class Signature(object):

    # * generates keys and returns them as b64 of DER format *
    def generate_keys(length=2048):
        pub_key, priv_key = rsa.newkeys(length)
        pub_key_b64 = base64.b64encode(pub_key.save_pkcs1(format='DER'))
        priv_key_b64 = base64.b64encode(priv_key.save_pkcs1(format='DER'))
        return pub_key_b64, priv_key_b64

    # * hashes the message, signs the hash, returns b64 of signature *
    def sign(message, secret_key):
        sk_object = rsa.PrivateKey.load_pkcs1(base64.b64decode(secret_key), format='DER')
        signature = rsa.sign(message, sk_object, 'SHA-256')
        return base64.b64encode(signature)

    # * using rsa library's verify function for convenience *
    def verify(public_key, message, signature):
        pk_object = rsa.PublicKey.load_pkcs1(base64.b64decode(public_key), format='DER')
        isValid = False
        try:
            isValid = rsa.verify(message, signature, pk_object)
            if isValid:
                print("signature is valid!")
        except:
            print("signature is not valid!")



if __name__ == "__main__":

    msg = "This is the data we we'll sign!".encode('utf-8')

    print("Generating keys...")
    pk, sk = Signature.generate_keys()

    print("Signing data: %s" % msg)
    signature = Signature.sign(msg,sk)
    print("Successfully signed with signature: %s" % signature)

    print("Verifying signature...")
    Signature.verify(pk, msg, signature)
