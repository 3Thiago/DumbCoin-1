from transaction.transaction import Transaction
from transaction.signature import Signature
from proof import proof
import hashlib

work_factor = 4 # global work factor
seed_coins = 1000000 # given to miner of Gensis node
god_public_key = None # store the public key of the entity that creates seed coins

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
                    if not Signature.verify(tx.from_pk, tx.to_string_for_hashing(), tx.signature):
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
        if not genesis_tx.from_pk == god_public_key:
            print("Genesis transaction appears not be divine!")
            return
        # verify signature
        if not Signature.verify(tx.from_pk, tx.to_string_for_hashing(), tx.signature):
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
        tx_hash = HashAssist.hash_value(tx.to_string_for_hashing())
        # 3. validate header
        header_string = block.prev_hash + tx_hash + block.nonce
        header_hash = HashAssist.hash_value(header_string)
        if not block.header_hash == header_hash:
            print("Block header invalid!")
            return
        self.blocks.append(block)

    # * validates a transaction's signature & amount *
    def validate_transaction(self, tx):
        # 1. validate signature
        isValid = Signature.verify(tx.from_pk, tx.to_string_for_hashing(), tx.signature)
        if not isValid:
            print("Signature not valid")
            return False
        # 2. validate sender balance
        balance = BlockAssist.get_balance(tx.from_pk, self.blocks)
        if tx.amount > balance:
            print("Sender doesn't have sufficient funds for this transaction!")
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

    def create_from_transaction(tx, prev_hash):
        tx_hash = HashAssist.hash_value(tx.to_string_for_hashing())
        print("Mining nonce....")
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
        if chainB.get_size() > chainA.get_size():
            if BlockAssist.validate_all_transactions_and_blocks(chainB):
                print("ChainB is longer and valid!")
                return chainB
        else:
            return chainA



if __name__ == "__main__":

    pk, sk = Signature.generate_keys()

    print("Firing up a new node!")

    print("Your public key is:")
    print(pk)

    print("Your secret key is:")
    print(sk)

    # Generate God keys to create seed transaction
    god_pk, god_sk = Signature.generate_keys()
    god_public_key = god_pk # store in global variable

    # Create two blockchains and implement fork choice
    new_blockchain = None
    for i in range(4):
        # if there's no blockchain, we must mine the Genesis node
        if not new_blockchain:
            tx = Transaction(god_pk, pk, seed_coins)
            tx.sign(god_sk)
            new_blockchain = Blockchain([tx])
        else:
            to_pk = input("Give seed money to:")
            amount = int(input("Amount:"))
            tx = Transaction(pk, to_pk, amount) # all transactions sent from God node
            tx.sign(sk)
            new_blockchain.add_transactions([tx])

    new_blockchain_2 = None
    for i in range(3):
        # if there's no blockchain, we must mine the Genesis node
        if not new_blockchain_2:
            tx = Transaction(god_pk, pk, seed_coins)
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

    if BlockAssist.fork_choice(new_blockchain, new_blockchain_2) == new_blockchain_2:
        print("We should update our node's blockchain to blockchain 2!")
    else:
        print("Our first blockchain was the longest, valid chain!")


    # test balance function
    # for i in range(2):
    #     search_pk = input("Get balance of public key:")
    #     balance = BlockAssist.get_balance(search_pk, new_blockchain.blocks)
    #     print(balance)
