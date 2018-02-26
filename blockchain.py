from proof import proof
from transaction.transaction import Transaction
from transaction.signature import Signature
import hashlib

work_factor = 5 # global work factor
seed_coins = 1000000 # given to miner of Gensis node

class Blockchain(object):
    def __init__(self, transactions=None):
        self.blocks = []

        if not transactions:
            raise Exception("Can't create a blockchain without data!")

        if not type(transactions) == list:
            raise Exception("Data must be a list of transactions!")

        for i, tx in enumerate(transactions):
            print("Adding transaction to blockchain: %s" % str(tx))
            # Create genesis block with first item
            if i == 0:
                # we'll only verify the signature for the genesis block since nobody holds a balance yet
                if not Signature.verify(tx.from_pk, tx.to_string_for_hashing(), tx.signature):
                    print("Genesis transaction signature is NOT valid.")
                    return
                prev_hash = "0" # arbitrary prev_hash for genesis block
                new_block = Block.create_from_transaction(tx, prev_hash)
                self.blocks.append(new_block)
            else:
                # TODO: Add balance verification!
                if not Signature.verify(tx.from_pk, tx.to_string_for_hashing(), tx.signature):
                    print("Transaction signature is NOT valid.")
                    return
                new_block = Block.create_from_transaction(tx, self.blocks[-1].header_hash)
                self.blocks.append(new_block)

    def add_transactions(self, transactions):
        if not transactions:
            print("Can't create a blockchain without a transaction!")
            return

        if not type(transactions) == list:
            print("Transactions must be a sent in a list!")
            return

        for i, tx in enumerate(transactions):
            print("Adding transaction to blockchain: %s" % tx)
            # TODO: Add balance verification!
            if not Signature.verify(tx.from_pk, tx.to_string_for_hashing(), tx.signature):
                print("Transaction signature is NOT valid.")
                return
            new_block = Block.create_from_transaction(tx, self.blocks[-1].header_hash)
            self.blocks.append(new_block)

    def remove_data(self, data):
        raise Exception("This is the blockchain, brah. No data shall be removed.")

    def validate_transaction(tx):
        # check if signature is valid
        isValid = Signature.verify(tx.from_pk, tx.to_string_for_hashing(), tx.signature)
        if not isValid:
            return False
        # check if sender has sufficient funds
        balance = BlockAssist.get_balance(self, tx.from_pk)
        if tx.amount > balance:
            print("Sender doesn't have sufficient funds for this transaction!")
            return False
        return True

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

    def create_from_transaction(tx, prev_hash):
        tx_hash = HashAssist.hash_value(tx.to_string_for_hashing())
        print("Mining for nonce....")
        nonce = proof.mint(prev_hash + tx_hash, work_factor) # mine for nonce
        header_hash = HashAssist.hash_value(prev_hash + tx_hash + nonce)
        return Block(header_hash, prev_hash, nonce, tx_hash, tx)

    def print_block(self):
        print("Block details....")
        print("header_hash: %s" % self.header_hash)
        print("prev_hash: %s" % self.prev_hash)
        print("nonce: %s" % self.nonce)
        print("transactions_hash: %s" % self.transactions_hash)
        print("transactions: %s" % self.transactions)
        print("_______________________________")



# * Helper Functions *
class HashAssist(object):
    def hash_value(value):
        h = hashlib.sha256()
        h.update(value.encode('utf-8'))
        return h.hexdigest()

class BlockAssist(object):
    def get_balance(blockchain, pub_key):
        balance = 0
        for block in blockchain.blocks:
            if block.transactions.to_pk == pub_key:
                balance += block.transactions.amount
            if block.transactions.from_pk == pub_key:
                balance -= block.transactions.amount
        return balance



if __name__ == "__main__":

    pk, sk = Signature.generate_keys()

    print("Your public key is:")
    print(pk)

    print("Your secret key is:")
    print(sk)

    # Create a few seed transactions and add to blockchain
    new_blockchain = None
    for i in range(4):
        # if there's no blockchain, we must mine the Genesis node
        if not new_blockchain:
            god_pk, god_sk = Signature.generate_keys()
            tx = Transaction(god_pk, pk, seed_coins)
            tx.sign(god_sk)
            new_blockchain = Blockchain([tx])
        else:
            to_pk = input("Give seed money to:")
            amount = int(input("Amount:"))
            tx = Transaction(pk, to_pk, amount) # all transactions sent from God node
            tx.sign(sk)
            new_blockchain.add_transactions([tx])

    # test balance function
    for i in range(3):
        search_pk = input("Get balance of public key:")
        balance = BlockAssist.get_balance(new_blockchain, search_pk)
        print(balance)

    new_blockchain.print_all_blocks()
