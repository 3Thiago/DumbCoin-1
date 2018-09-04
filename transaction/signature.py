import base64
import hashlib

import rsa



def generate_keys(length=2048):
    """Generates keys and returns them as a string."""

    print("Generating keys...")
    pub_key, priv_key = rsa.newkeys(length)
    pub_key_b64 = base64.b64encode(pub_key.save_pkcs1(format='DER'))
    priv_key_b64 = base64.b64encode(priv_key.save_pkcs1(format='DER'))

    return pub_key_b64.decode('utf-8'), priv_key_b64.decode('utf-8')

def sign(message, secret_key):
    """Hashes the message, signs the hash, returns b64 string of signature"""

    msg_bytes = message.encode('utf-8')
    sk_bytes = secret_key.encode('utf-8')
    sk_object = rsa.PrivateKey.load_pkcs1(base64.b64decode(sk_bytes), format='DER')
    signature = rsa.sign(msg_bytes, sk_object, 'SHA-256')

    return base64.b64encode(signature).decode('utf-8')

def verify(public_key, message, signature):
    """Verifies that signature was created from secret key"""

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
        isValid = rsa.verify(msg, sig_decoded, pk_object)
    except:
        print("signature is not valid!")
    return isValid



if __name__ == "__main__":
    pass