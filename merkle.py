# * merkle.py *
# Creating merkle trees from raw data

import hashlib

raw_data = ["We", "hold", "these", "truths", "to", "be", "self-evident", "that"]

hash_concat_format = "%s||%s"


# * Custom Node Class *

class MerkleNode(object):
    def __init__(self, left=None, right=None, node_hash=""):
        self.left = left
        self.right = right
        self.hash = node_hash
        if not self.hash:
            self.hash = self.create_hash(left, right)

    def create_hash(self, left_node, right_node):
        header = hash_concat_format % (left_node.hash, right_node.hash)
        h = hashlib.sha256()
        h.update(header.encode('utf-8'))
        return h.hexdigest()

    def print_node(self):
        print("NODE")
        if self.left and self.right:
            print("self.left.hash: %s" % self.left.hash)
            print("self.right.hash: %s" % self.right.hash)
        print("self.hash: %s" % self.hash)
        print("______________________________")



# * Create A Merkle Tree *

def create_merkle_tree(data):

    nodes = []
    current_level = []
    merkle_tree = []

    left_child = ""
    right_child = ""

    # first, convert raw data to nodes
    for item in data:
        h = hashlib.sha256()
        h.update(item.encode('utf-8'))
        node = MerkleNode(node_hash=h.hexdigest())
        nodes.append(node)

    while True:
        for node in nodes:
            # if we have a left and right child, make a new node!
            if left_child and right_child:
                n = MerkleNode(left_child, right_child)
                current_level.append(n)
                # reset left & right nodes
                left_child, right_child = node, ""
            elif not left_child:
                left_child = node
            else:
                right_child = node

        # if we any nodes remaining, add them to our layer!
        if left_child and right_child:
            n = MerkleNode(left_child, right_child)
            current_level.append(n)
            left_child, right_child = "", ""
        elif left_child:
            # if there's a single left block, there was an odd number of nodes
            # we pair the hash with itself and create a new node
            n = MerkleNode(left_child, left_child)
            current_level.append(n)
            left_child, right_child = "", ""

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
    return merkle_tree[-1][0].hash


def print_each_layer_in_tree(merkle_tree):
    for i, level in enumerate(merkle_tree):
        print("Level %s:" % i)
        for node in level:
            node.print_node()



# * Run a simple test *

# m = create_merkle_tree(raw_data)
# print("The merkle root for our data is: %s" % get_merkle_root(m))
# print_each_layer_in_tree(m)
