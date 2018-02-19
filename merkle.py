# * merkle.py *
# Creating merkle trees from raw data

import hashlib

raw_data = ["We", "hold", "these", "truths", "to", "be", "self-evident", "that"]

hash_concat_format = "%s||%s"


# * Custom Node Class *

class MerkleNode(object):
    def __init__(self, left_hash="", right_hash="", node_hash=""):
        self.left_hash = left_hash
        self.right_hash = right_hash
        self.hash = node_hash
        if not self.hash:
            self.hash = self.create_hash(left_hash, right_hash)

    def create_hash(self, left_hash, right_hash):
        header = hash_concat_format % (left_hash, right_hash)
        h = hashlib.sha256()
        h.update(header.encode('utf-8'))
        return h.hexdigest()

    def print_node(self):
        print("NODE")
        print("self.left_hash: %s" % self.left_hash)
        print("self.right_hash: %s" % self.right_hash)
        print("self.hash: %s" % self.hash)
        print("______________________________")



# * Create A Merkle Tree *

def create_merkle_tree(data):

    nodes = []
    current_level = []
    merkle_tree = []

    left_block_hash = ""
    right_block_hash = ""

    # first, convert raw data to nodes
    for item in data:
        h = hashlib.sha256()
        h.update(item.encode('utf-8'))
        node = MerkleNode(node_hash=h.hexdigest())
        nodes.append(node)

    while True:
        for node in nodes:
            # if we have a left and right hash, make a new node!
            if left_block_hash and right_block_hash:
                n = MerkleNode(left_block_hash, right_block_hash)
                current_level.append(n)
                # reset left & right nodes
                left_block_hash, right_block_hash = node.hash, ""
            elif not left_block_hash:
                left_block_hash = node.hash
            else:
                right_block_hash = node.hash

        # if we any nodes remaining, add them to our layer!
        if left_block_hash and right_block_hash:
            n = MerkleNode(left_block_hash, right_block_hash)
            current_level.append(n)
            left_block_hash, right_block_hash = "", ""
        elif left_block_hash:
            # if there's a single left block, there was an odd number of nodes
            # we pair the hash with itself and create a new node
            n = MerkleNode(left_block_hash, left_block_hash)
            current_level.append(n)
            left_block_hash, right_block_hash = "", ""

        # Now, add the new nodes to the list we'll use to create the next level
        nodes = []
        for node in current_level:
            nodes.append(node)

        # add current layer to merkle_tree
        merkle_tree.append(current_level)

        if len(current_level) == 1: # if current layer only has one item, we've reached the root
            return merkle_tree
        else:
            current_level = [] # otherwise, reset stage and re-loop



# * Visualization Helper Functions *

def get_merkle_root(merkle_tree):
    for level in merkle_tree:
        if len(level) == 1: # the merkle root should be the only stage with one item
            return level[0].hash


def print_each_layer_in_tree(merkle_tree):
    for i, level in enumerate(merkle_tree):
        print("Level %s:" % i)
        for node in level:
            node.print_node()



# * Run a simple test *

# m = create_merkle_tree(raw_data)
# print("The merkle root for our data is: %s" % get_merkle_root(m))
# print_each_layer_in_tree(m)
