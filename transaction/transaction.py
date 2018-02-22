class Transaction(object):
    def __init__(self, from_pk, to_pk, amount, signature):
        self.from_pk = from_pk
        self.to_pk = to_pk
        self.amount = amount
        self.signature = signature
