class Transaction(object):
    def __init__(self, from_pk, to_pk, amount, signature):
        self.from_pk = from_pk
        self.to_pk = to_pk
        self.amount = amount
        self.signature = signature

    def __str__(self):
        # override default python __str__ method to convert transaction to custom string
        transaction_string_format = "%s||%s||%s||%s"
        return transaction_string_format % (self.from_pk, self.to_pk, str(self.amount), self.signature)
