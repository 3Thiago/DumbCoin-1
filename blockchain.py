from proof import proof
from transaction.transaction import Transaction
import hashlib

work_factor = 5 # global work factor

class Blockchain(object):
    def __init__(self, transactions):
        self.blocks = []

        if not transactions:
            raise Exception("Can't create a blockchain without data!")

        if not type(transactions) == list:
            raise Exception("Data must be a list of transactions!")

        for i, tx in enumerate(transactions):

            print("Adding transaction to blockchain: %s" % str(tx))

            # Create genesis block with first item
            if i == 0:
                prev_hash = "0" # arbitrary prev_hash for genesis block
                tx_hash = self.hash_value(str(tx))
                nonce = proof.mint(prev_hash + tx_hash, work_factor)
                header_hash = self.hash_value(prev_hash + tx_hash + nonce)
                self.blocks.append(Block(header_hash, prev_hash, nonce, tx_hash, tx))
            else:
                # validate tx and create block
                if not self.validate_transaction(tx.from_pk, tx.amount):
                    print("Transaction invalid! Insufficient funds.")
                    return
                prev_hash = self.blocks[-1].header_hash
                tx_hash = self.hash_value(str(tx))
                nonce = proof.mint(prev_hash + tx_hash, work_factor)
                header_hash = self.hash_value(prev_hash + tx_hash + nonce)
                self.blocks.append(Block(header_hash, prev_hash, nonce, tx_hash, tx))

    def add_transactions(self, transactions):
        if not transactions:
            print("Can't create a blockchain without a transaction!")
            return

        if not type(transactions) == list:
            print("Transactions must be a sent in a list!")
            return

        for i, tx in enumerate(transactions):

            if not self.validate_transaction(tx.from_pk, tx.amount):
                print("Transaction invalid! Insufficient funds.")
                return

            print("Adding transaction to blockchain: %s" % tx)
            prev_hash = self.blocks[-1].header_hash
            tx_hash = self.hash_value(str(tx))
            nonce = proof.mint(prev_hash + tx_hash, work_factor)
            header_hash = self.hash_value(prev_hash + tx_hash + nonce)
            self.blocks.append(Block(header_hash, prev_hash, nonce, tx_hash, tx))

    def remove_data(self, data):
        raise Exception("This is the blockchain, brah. No data shall be removed.")

    def get_balance(self, pub_key):
        balance = 0
        for block in self.blocks:
            if block.transactions.to_pk == pub_key:
                balance += block.transactions.amount
            if block.transactions.from_pk == pub_key:
                balance -= block.transactions.amount
        return balance

    def validate_transaction(self, pub_key, amount):
        balance = self.get_balance(pub_key)
        return balance >= amount

    def hash_value(self, value):
        h = hashlib.sha256()
        h.update(value.encode('utf-8'))
        return h.hexdigest()

    def print_all_blocks(self):
        for block in self.blocks:
            block.print_block()



class Block(object):
    def __init__(self, header_hash, prev_hash, nonce, transactions_hash, transactions):
        self.header_hash = header_hash
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.transactions_hash = transactions_hash
        self.transactions = transactions

    def print_block(self):
        print("Block details....")
        print("header_hash: %s" % self.header_hash)
        print("prev_hash: %s" % self.prev_hash)
        print("nonce: %s" % self.nonce)
        print("transactions_hash: %s" % self.transactions_hash)
        print("transactions: %s" % self.transactions)
        print("_______________________________")



if __name__ == "__main__":

    tx1 = Transaction("God", "Stew", 1000, "Signature Goes Here!")
    new_blockchain = Blockchain([tx1])

    print("Blockchain created with genesis block!")

    for i in range(3):
        print("Let's send some money around!")
        from_pk = input("From Public Key:")
        to_pk = input("To Public Key:")
        amount = int(input("Amount:"))

        new_tx = Transaction(from_pk, to_pk, amount, "Signature Goes Here!")
        new_blockchain.add_transactions([new_tx])

    new_blockchain.print_all_blocks()
