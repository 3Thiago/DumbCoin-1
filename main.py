from flask import Flask, request, jsonify, render_template
from blockchain.transaction import signature, transaction
from blockchain import blockchain
import requests
import json
import sys
import random
import threading
import uuid
import webbrowser

app = Flask(__name__)

host_url = "http://127.0.0.1"


# * High-Level Notes *
# - Nodes Gossip by sharing their latest blockchain
# - This state is communicated in both POST /gossip/ requests & responses
# - A node updates its current blockchain each time it receives another node's blockchain
# (^ which can be via a request or response)



# * Node Class *

class Node(object):
    def __init__(self):

        self.port = str(input("Create new node on port: ")) # Because we'll use port as a key in JSON, convert to string
        self.public_key = ""
        self.secret_key = ""
        self.version = 0
        self.network_state = {}
        self.blockchain = None
        self.message_cache = []
        self.peer_ports = self.get_peer_port()

        # generate node's public and private keys
        self.generate_keys()

        # if there are no peer ports, create God transaction & blockchain
        if not self.peer_ports:
            god_tx = blockchain.create_god_transaction(self.public_key)
            self.blockchain = blockchain.Blockchain([god_tx])
    # this would normally be a network call, using terminal for convenience
    def get_peer_port(self):
        while True:
            user_input = input("Seed node at port (type 'GOD' if God node): ")
            if user_input == 'GOD':
                return []
                pass
            else:
                seed_port = int(user_input)
                if seed_port == int(self.port):
                    print("Can't seed with your own port!")
                else:
                    return [seed_port]

    def generate_keys(self):
        pk, sk = signature.generate_keys()
        self.public_key = pk
        self.secret_key = sk

    def update_favorite_letter(self):

        # increment version
        self.version = self.version + 1

        # choose & assign new favorite letter
        self.favorite_letter = random.choice(["a", "b", "c", "d", "e"])

        # update network state with new values for self
        self.network_state[self.port] = {"version": self.version, "favorite_letter": self.favorite_letter}

        # prepare message to post to peer
        message = self.generate_update_message()

        # Gossip!
        if self.peer_ports:
            self.post_message_to_random_peer(message)

        # begin 10 second timer
        # threading.Timer(10, self.update_favorite_letter).start()

    # Nodes communicate via their latest network_state
    def generate_update_message(self):

        # Create message
        message = {}
        message['UUID'] = str(uuid.uuid4()) # generate random UUID
        message['originating_port'] = self.port
        message['version'] = self.version
        message['TTL'] = 1
        message['network_state'] = self.network_state

        # return message as json
        return json.dumps(message)

    def post_message_to_random_peer(self, message):

        # Select randome peer
        rand_idx = random.randint(0,len(self.peer_ports) - 1)

        # Create URL path for peer node's gossip endpoint
        post_to_url = host_url + (":%s" % self.peer_ports[rand_idx]) + '/gossip'

        try:
            # send POST request with new state
            print("Sending POST request to URL: %s" % post_to_url)
            resp = requests.post(post_to_url, json=message)

            # they'll respond with message that includes network_state
            resp_json = resp.json()
            self.save_message_to_cache(resp_json) # save response to cache

            peer_network_state = resp_json["network_state"]
            self.update_network_state_with_peer_state(peer_network_state)
        except:
            print("POST Request failed!")

    def save_message_to_cache(self, message):
        self.message_cache.append(message)

    def add_peer(self, port):
        if not str(port) == self.port: # don't add own port...
            self.peer_ports.append(port)

    def update_network_state_with_peer_state(self, peer_network_state):
        # for each port in our peer's network state...
        for key in peer_network_state:
            # see if we already have a value stored...
            if key in self.network_state:
                # and if our version is out of date...
                if self.network_state[key]["version"] < peer_network_state[key]["version"]:
                    # update it!
                    self.network_state[key] = peer_network_state[key]

            # Add peer to our known peer ports
            if int(key) not in self.peer_ports:
                self.add_peer(int(key))

            else:
                # if we don't have any data on that port saved, add it!
                self.network_state[key] = peer_network_state[key]



# * Rendering Functionality *

def render_front_page(errors="", balance=0):
    if node.blockchain:
        balance = blockchain.get_balance(node.public_key, node.blockchain.blocks)
    balance = "{:,.2f}".format(balance)
    return render_template('template.html', node=node, errors=errors, balance=balance)



# * App Functionality *

@app.route("/", methods = ['GET', 'POST'])
def main():

    if request.method == "GET":
        return render_front_page()

    if request.method == "POST":
        print("POST request received with form data:")
        new_tx = create_transaction_with_form_data(request.form)
        node.blockchain.add_transactions([new_tx])
        print("Added a new transaction to the block!")
        return render_front_page()

def create_transaction_with_form_data(form):
    to_pk = form['to_public_key']
    amount = int(form['amount'])
    sk = form['secret_key']

    tx = transaction.Transaction(node.public_key, to_pk, amount)
    tx.sign(sk)

    return tx



@app.route("/gossip", methods = ['GET', 'POST'])
def gossip():

    if request.method == "GET":
        return render_front_page()

    if request.method == "POST":
        # save message to cache
        request_json = request.get_json()
        node.save_message_to_cache(request_json)

        # update self.network_state with peer's network state from payload
        peer_network_state = json.loads(request_json)["network_state"]
        node.update_network_state_with_peer_state(peer_network_state)

        # Return self.network_status as a response
        return node.generate_update_message()



if __name__ == "__main__":

    # ask the user if this is the God node

    # * Create Node *
    node = Node()

    # view node in web browser in new tab
    webbrowser.open(host_url + (":%s" % node.port), new=2)

    app.run(host="127.0.0.1", port=int(node.port))
