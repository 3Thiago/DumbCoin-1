from .signature import Signature

class Transaction(object):
    def __init__(self, from_pk, to_pk, amount, signature=""):
        self.from_pk = from_pk
        self.to_pk = to_pk
        self.amount = amount
        self.signature = signature

    # * signs transaction with secret key *
    def sign(self, sk):
        string_to_sign = self.to_string_for_hashing()
        self.signature = Signature.sign(string_to_sign, sk)

    # * returns proper message string for hashing and signing
    def to_string_for_hashing(self):
        signature_string_format = "%s||%s||%s"
        string_for_hashing = signature_string_format % (self.from_pk, self.to_pk, self.amount)
        return string_for_hashing

    # * modifying default python __str__ method to use custom string format *
    def __str__(self):
        transaction_string_format = "%s||%s||%s||%s"
        # appending length of keys & signature for readability
        return transaction_string_format % (self.from_pk[0:30], self.to_pk[0:30], str(self.amount), self.signature[0:30])



if __name__ == "__main__":
    pass
