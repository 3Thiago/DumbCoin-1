from . import signature

class Transaction(object):
    def __init__(self, from_pk, to_pk, amount, signature=""):
        self.from_pk = from_pk
        self.to_pk = to_pk
        self.amount = amount
        self.signature = signature

    def sign(self, sk):
        """Signs transaction with secret key"""

        string_to_sign = self.to_string_for_hashing()
        self.signature = signature.sign(string_to_sign, sk)

    def to_string_for_hashing(self):
        """Returns proper message string for hashing and signing"""

        signature_string_format = "%s||%s||%s"
        string_for_hashing = signature_string_format % (self.from_pk, self.to_pk, self.amount)
        return string_for_hashing

    def __str__(self):
        """Modifies default python __str__ method to return custom string format"""

        transaction_string_format = "%s||%s||%s||%s"
        return transaction_string_format % (self.from_pk[0:30], self.to_pk[0:30], str(self.amount), self.signature[0:30])



if __name__ == "__main__":
    pass
