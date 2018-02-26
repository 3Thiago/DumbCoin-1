from .signature import Signature

class Transaction(object):
    def __init__(self, from_pk, to_pk, amount, signature=None):
        self.from_pk = from_pk
        self.to_pk = to_pk
        self.amount = amount
        self.signature = signature

    # * signs transaction with secret key *
    def sign(self, sk):
        signature_string_format = "%s||%s||%s"
        message_to_sign = signature_string_format % (self.from_pk, self.to_pk, self.amount)
        self.signature = Signature.sign(message_to_sign.encode('utf-8'), sk)

    # * modifying default python __str__ method to use custom string format *
    def __str__(self):
        transaction_string_format = "%s||%s||%s||%s"
        return transaction_string_format % (self.from_pk, self.to_pk, str(self.amount), self.signature)



if __name__ == "__main__":
    pass
