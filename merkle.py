# * merkle.py *
# Creating merkle trees from raw data

import hashlib

data_blocks = ["We", "hold", "these", "truths", "to", "be", "self-evident", "that"]

node_string_format = "%s||%s"



# * Create A Merkle Tree *

def create_merkle_tree(data):

    blocks = []
    current_layer = []
    merkle_tree = []

    left_block_hash = ""
    right_block_hash = ""

    # first, convert raw data to hashes
    for item in data:
        h = hashlib.sha256()
        h.update(item.encode('utf-8'))
        blocks.append(h.hexdigest())

    while True:
        for item in blocks:
            # if we have a left and right hash, make a new node!
            if left_block_hash and right_block_hash:
                new_node = create_new_node(hash_left=left_block_hash, hash_right=right_block_hash)
                current_layer.append(new_node)

                # reset left & right blocks
                left_block_hash, right_block_hash = item, ""
            elif not left_block_hash:
                left_block_hash = item
            else:
                right_block_hash = item

        # if we any blocks remaining, add them to our layer!
        if left_block_hash and right_block_hash:
            new_node = create_new_node(hash_left=left_block_hash, hash_right=right_block_hash)
            current_layer.append(new_node)
            left_block_hash, right_block_hash = "", ""
        elif left_block_hash:
            # if there's a single left block, there was an odd number of blocks
            # we pair the hash with itself and create a new node
            new_node = create_new_node(hash_left=left_block_hash, hash_right=left_block_hash)
            current_layer.append(new_node)
            left_block_hash, right_block_hash = "", ""

        # Now, add the hashes of each new node to the list we'll use to create the next stage
        blocks = []
        for item in current_layer:
            blocks.append(item["hash"])

        # add current layer to merkle_tree
        merkle_tree.append(current_layer)

        if len(current_layer) == 1: # if current layer only has one item, we've reached the root
            return merkle_tree
        else:
            current_layer = [] # otherwise, reset stage and re-loop



# * Merkle Helper Functions *

def create_new_node(hash_left, hash_right):
    new_node_hash_string = node_string_format % (hash_left, hash_right)
    h = hashlib.sha256()
    h.update(new_node_hash_string.encode('utf-8'))
    new_node_hash = h.hexdigest()

    new_node = {"hash": new_node_hash,
                "left": hash_left,
                "right": hash_right}
    return new_node



# * Visualization Helper Functions *

def get_merkle_root(merkle_tree):
    for item in merkle_tree:
        if len(item) == 1: # the merkle root should be the only stage with one item
            return item[0]["hash"]


def print_each_layer_in_tree(merkle_tree):
    for i, item in enumerate(merkle_tree):
        print("Layer %s:" % i)
        print(item)



# * Run a simple test *

m = create_merkle_tree(data_blocks)
print("The merkle root for our data is: %s" % get_merkle_root(m))
print_each_layer_in_tree(m)
