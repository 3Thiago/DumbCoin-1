from transaction.transaction import Transaction
from transaction import signature
from proof import proof
import hashlib
import sys

WORK_FACTOR = 5
SEED_COIN_SUPPLY = 21000000

class Blockchain(object):

    # * creates blockchain from seed transactions *
    def __init__(self, transactions=None):
        self.blocks = []
        if transactions:
            if not type(transactions) == list:
                raise Exception("Data must be a list of transactions!")

            for i, tx in enumerate(transactions):
                # Create genesis block with first item
                if i == 0:
                    # we'll only verify the signature for the genesis block since nobody holds a balance yet
                    if not signature.verify(tx.from_pk, tx.to_string_for_hashing(), tx.signature):
                        print("Genesis transaction signature is NOT valid.")
                        return
                    prev_hash = "0" # arbitrary prev_hash for genesis block
                    new_block = Block.create_from_transaction(tx, prev_hash)
                    self.blocks.append(new_block)
                else:
                    if not self.validate_transaction(tx):
                        print("Transaction is NOT valid.")
                        return
                    new_block = Block.create_from_transaction(tx, self.blocks[-1].header_hash)
                    self.validate_and_add_block(new_block)

    # * creates blockchain from a Genesis block *
    def init_with_genesis_block(self, block):
        # genesis block contains single seed transaction from God
        genesis_tx = block.transactions
        # we only verify the signature since we can't retain sk for God and create new transactions
        if not signature.verify(genesis_tx.from_pk, genesis_tx.to_string_for_hashing(), genesis_tx.signature):
            print("Genesis transaction signature is NOT valid.")
            return
        self.blocks.append(block)
        return self

    # * mines a new block with transaction(s) *
    def add_transactions(self, transactions):
        if not transactions:
            Exception("transactions cannot be empty!")
            return

        if not type(transactions) == list:
            Exception("Transactions must be a sent in a list!")
            return

        for i, tx in enumerate(transactions):
            if not self.validate_transaction(tx):
                return
            new_block = Block.create_from_transaction(tx, self.blocks[-1].header_hash)
            self.validate_and_add_block(new_block)

    # * validates a block before adding to current chain *
    def validate_and_add_block(self, block):
        # 1. validate transaction(s) in block
        tx = block.transactions
        if not self.validate_transaction(tx):
            print("Block contains invalid transactions.")
            return
        # 2. hash transaction(s)
        tx_hash = HashAssist.hash_value(value=tx.to_string_for_hashing())
        # 3. validate header
        header_string = block.prev_hash + tx_hash + block.nonce
        header_hash = HashAssist.hash_value(header_string)
        if not block.header_hash == header_hash:
            print("Block header invalid!")
            return
        self.blocks.append(block)

    # * validates a transaction's signature & amount *
    # * added throw_exception param so web client can retrieve error msg
    def validate_transaction(self, tx, throw_exception=False):
        # 1. validate signature
        isValid = signature.verify(tx.from_pk, tx.to_string_for_hashing(), tx.signature)
        if not isValid:
            error_msg = "Signature not valid!"
            if throw_exception:
                print(error_msg)
                raise Exception(error_msg)
            else:
                print(error_msg)
                return False
        # 2. validate sender balance
        balance = get_balance(tx.from_pk, self.blocks)
        if tx.amount > balance:
            error_msg = "Insufficient funds for this transaction!"
            if throw_exception:
                print(error_msg)
                raise Exception(error_msg)
            else:
                print(error_msg)
                return False
        return True

    def get_size(self):
        return len(self.blocks)

    def print_all_blocks(self):
        for block in self.blocks:
            block.print_block()

    def remove_data(self, data):
        raise Exception("This is the blockchain, brah. No data shall be removed.")



class Block(object):
    def __init__(self, header_hash, prev_hash, nonce, transactions_hash, transactions):
        self.header_hash = header_hash
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.transactions_hash = transactions_hash
        self.transactions = transactions
    
    @staticmethod
    def create_from_transaction(tx, prev_hash):
        tx_hash = HashAssist.hash_value(tx.to_string_for_hashing())
        print("Mining nonce....")
        nonce = proof.mint(prev_hash + tx_hash, WORK_FACTOR) # mine for nonce
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
    @classmethod
    def hash_value(self, value):
        h = hashlib.sha256()
        h.update(value.encode('utf-8'))
        return h.hexdigest()

# * returns unspent transaction balance for a public key *
def get_balance(pub_key, blocks):
    balance = 0
    for block in blocks:
        if block.transactions.to_pk == pub_key:
            balance += block.transactions.amount
        if block.transactions.from_pk == pub_key:
            balance -= block.transactions.amount
    return balance

# * validates all transactions and blocks in a chain *
def validate_all_transactions_and_blocks(blockchain):
    # recreates blockchain from scratch...
    new_blockchain = None
    # which runs all necessary checks as it builds and adds blocks...
    i = 0
    for block in blockchain.blocks:
        if i == 0:
            new_blockchain = Blockchain().init_with_genesis_block(block)
        else:
            try:
                new_blockchain.validate_and_add_block(block)
            except:
                print("Blockchain contains invalid blocks!")
                return False
        i += 1
    return True

# * returns the longest, valid chain *
# Assumes that chainA is node's current chain and has therefore already been validated!
def fork_choice(chainA, chainB):
    if not chainA:
        if validate_all_transactions_and_blocks(chainB):
            print("There's no ChainA, and ChainB is valid!")
            return chainB
    elif chainB.get_size() > chainA.get_size():
        if validate_all_transactions_and_blocks(chainB):
            print("ChainB is longer and valid!")
            return chainB
    return chainA

# * creates God transaction with seed coins
def create_god_transaction(to_pk):
    god_pk, god_sk = signature.generate_keys()
    tx = Transaction(god_pk, to_pk, SEED_COIN_SUPPLY)
    tx.sign(god_sk)
    return tx



if __name__ == "__main__":

    pk, sk = signature.generate_keys()

    print("Firing up a new node!")

    print("Your public key is:")
    print(pk)

    print("Your secret key is:")
    print(sk)

    # Generate God keys to create seed transaction
    god_pk, god_sk = signature.generate_keys()

    # Create two blockchains and implement fork choice
    new_blockchain = None
    for i in range(4):
        # if there's no blockchain, we must mine the Genesis node
        if not new_blockchain:
            tx = Transaction(god_pk, pk, SEED_COIN_SUPPLY)
            tx.sign(god_sk)
            new_blockchain = Blockchain([tx])
        else:
            to_pk = input("Give seed money to:")
            amount = int(input("Amount:"))
            tx = Transaction(pk, to_pk, amount) # all transactions sent from God node
            tx.sign(sk)
            new_blockchain.add_transactions([tx])

    print("Creating second blockchain...")

    new_blockchain_2 = None
    for i in range(3):
        # if there's no blockchain, we must mine the Genesis node
        if not new_blockchain_2:
            tx = Transaction(god_pk, pk, SEED_COIN_SUPPLY)
            tx.sign(god_sk)
            new_blockchain_2 = Blockchain([tx])
        else:
            to_pk = input("Give seed money to:")
            amount = int(input("Amount:"))
            tx = Transaction(pk, to_pk, amount) # all transactions sent from God node
            tx.sign(sk)
            new_blockchain_2.add_transactions([tx])

    print("We now have TWO blockchains.")
    print("Let's run a fork choice rule!")

    if fork_choice(new_blockchain, new_blockchain_2) == new_blockchain_2:
        print("We should update our node's blockchain to blockchain 2!")
    else:
        print("Our first blockchain was the longest, valid chain!")


    # test balance function
    # for i in range(2):
    #     search_pk = input("Get balance of public key:")
    #     balance = BlockAssist.get_balance(search_pk, new_blockchain.blocks)
    #     print(balance)
