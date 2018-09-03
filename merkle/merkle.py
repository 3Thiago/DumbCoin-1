import hashlib

raw_data = ["We", "hold", "these", "truths", "to", "be", "self-evident", "that"]

HASH_CONCAT_FORMAT = "%s||%s"



# * Classes *

class MerkleTree(object):
    def __init__(self, data):
        self.is_ready = False
        self.node_table = {}
        self.root = self.create_merkle_tree_from_data(data)

    def create_merkle_tree_from_data(self, data):

        current_level = {}
        parent_level = []
        left_child = None
        right_child = None

        # 1. convert raw data to nodes
        for item in data:
            leaf = self.create_leaf(item)
            current_level[leaf.hash] = leaf

        # 2a. loop through all nodes and create corresponding parent nodes
        while not self.is_ready:
            for key in current_level:
                node = current_level[key]
                if left_child and right_child:
                    parent_node = MerkleNode(left_child, right_child)
                    current_level[left_child.hash].parent = parent_node
                    current_level[right_child.hash].parent = parent_node
                    parent_level.append(parent_node)
                    left_child, right_child = node, "" # reset left & right nodes
                elif not left_child:
                    left_child = node
                else:
                    right_child = node

            # 2b. After our loop, check if there are any nodes that still need a parent
            if left_child and right_child:
                parent_node = MerkleNode(left_child, right_child)
                current_level[left_child.hash].parent = parent_node
                current_level[right_child.hash].parent = parent_node
                parent_level.append(parent_node)
            elif left_child:
                # if there's a single left block, there was an odd number of nodes
                # we pair the hash with itself and create a new node
                parent_node = MerkleNode(left_child, left_child)
                current_level[left_child.hash].parent = parent_node
                parent_level.append(parent_node)

            # 2c. reset child nodes in anticipation of next loop
            left_child, right_child = "", ""

            # * temporary *
            # add items from current level to self.node_table
            for key in current_level:
                self.node_table[key] = current_level[key]

            # 2d. add the new parent nodes to the list we'll use to generate the next level
            current_level = {}
            for node in parent_level:
                current_level[node.hash] = node

            # 2e. check if current_level has only one item. If so, we've reached the root!
            if len(parent_level) == 1:
                root_node = parent_level[0]
                self.node_table[root_node.hash] = root_node
                self.is_ready = True
                return root_node
            else:
                parent_level = [] # otherwise, reset stage and re-loop

    def create_leaf(self, val):
        val = str(val)
        h = hashlib.sha256()
        h.update(val.encode('utf-8'))
        return MerkleNode(node_hash=h.hexdigest())

    def hash_value(self, val):
        val = str(val)
        h = hashlib.sha256()
        h.update(val.encode('utf-8'))
        return h.hexdigest()

    def get_root(self):
        if self.is_ready:
            return self.root.hash
        else:
            print("Tree is not ready!")

    def get_node(self, hash_val):
        return self.node_table.get(hash_val)




class MerkleNode(object):
    def __init__(self, left=None, right=None, parent=None, node_hash=""):
        self.parent = parent
        self.left = left
        self.right = right
        self.hash = node_hash
        if not self.hash:
            self.hash = self.create_hash(left, right)

    def create_hash(self, left_node, right_node):
        header = self.concat_hashes(left_node.hash, right_node.hash)
        h = hashlib.sha256()
        h.update(header.encode('utf-8'))
        return h.hexdigest()

    def concat_hashes(self, left_string, right_string):
        return HASH_CONCAT_FORMAT % (left_string, right_string)

    def print_node(self):
        print("NODE DETAILS:")
        print("self.hash: %s" % self.hash)
        print("self.parent: %s" % self.parent)
        if self.left and self.right:
            print("self.left.hash: %s" % self.left.hash)
            print("self.right.hash: %s" % self.right.hash)
        print("self.hash: %s" % self.hash)
        print("______________________________")







# * Helper Functions *

def generate_proof(tree, val):
    node = tree.node_table.get(tree.hash_value(val))
    if node:
        proof = []
        while node.parent:
            if node == node.parent.left:
                proof.append({"side": "right", "hash": node.parent.right.hash})
            else:
                proof.append({"side": "left", "hash": node.parent.left.hash})
            node = node.parent
        return proof
    else:
        raise Exception("Value '%s' doesn't exist in this tree!" % val)

def verify_inclusion(tree, val, proof=None):
    # generate proof if none given
    if not proof:
        try:
            proof = generate_proof(tree, val)
        except:
            return False

    proof_hash = tree.hash_value(val)

    for item in proof:
        if item["side"] == "right":
            concat = HASH_CONCAT_FORMAT % (proof_hash, item["hash"])
            proof_hash = tree.hash_value(concat)
        else:
            concat = HASH_CONCAT_FORMAT % (item["hash"], proof_hash)
            proof_hash = tree.hash_value(concat)

    return proof_hash == tree.get_root()



# * Run A Simple Test *

if __name__ == "__main__":

    m = MerkleTree(data=raw_data)

    print("Tree successfully created: %s" % m.root)

    search_value = "self-evident"

    print("Searching for '%s'..." % search_value)

    is_included = verify_inclusion(m, search_value)

    print("'%s' is included in Merkle Tree?: %s" % (search_value, is_included))
