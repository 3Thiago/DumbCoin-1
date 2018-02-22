import proof
import hashlib

work_factor = 4 # global work factor

class Blockchain(object):
    def __init__(self, data):
        self.blocks = []

        if not data:
            raise Exception("Can't create a blockchain without data!")

        if not type(data) == list:
            raise Exception("Data must be a list of strings!")

        for i, item in enumerate(data):
            # ensure each item is a string
            item = str(item)

            print("Adding item to blockchain: %s" % item)

            # first item, so create genesis block
            if i == 0:
                prev_hash = "0" # arbitrary prev_hash for genesis block
                content = item
                nonce = proof.mint(prev_hash + content, work_factor)
                header_hash = self.hash_value(prev_hash + content + nonce)
                self.blocks.append(Block(header_hash, prev_hash, nonce, content))
            else:
                # create normal block
                prev_hash = self.blocks[i-1].header_hash
                content = item
                nonce = proof.mint(prev_hash + content, work_factor)
                header_hash = self.hash_value(prev_hash + content + nonce)
                self.blocks.append(Block(header_hash, prev_hash, nonce, content))

    def hash_value(self, value):
        h = hashlib.sha256()
        h.update(value.encode('utf-8'))
        return h.hexdigest()


class Block(object):
    def __init__(self, header_hash, prev_hash, nonce, content):
        self.header_hash = header_hash
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.content = content

    def print_block(self):
        print("Block details....")
        print("header_hash: %s" % self.header_hash)
        print("prev_hash: %s" % self.prev_hash)
        print("nonce: %s" % self.nonce)
        print("content: %s" % self.content)
        print("_______________________________")


if __name__ == "__main__":

    data_to_save = "I'm sorry, but I just don't find Big Bang Theory that funny."

    new_blockchain = Blockchain(data_to_save.split(" "))

    print("Created a blockchain with the following blocks...")

    for block in new_blockchain.blocks:
        block.print_block()
