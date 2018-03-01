from flask import Flask, request, jsonify, render_template
from blockchain.transaction import signature, transaction
from blockchain import blockchain
import requests
import json
import sys
import random
import threading
import webbrowser
import pickle
import jsonpickle

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
        self.network_state = {} # {'port1': 'public_key1', 'port2': 'public_key2', etc.}
        self.blockchain = None
        self.message_cache = []
        self.last_message = None
        self.peer_ports = self.get_peer_port()

        # generate node's public and private keys
        self.generate_keys()

        # if there are no peer ports, create God transaction & blockchain
        if not self.peer_ports:
            god_tx = blockchain.create_god_transaction(self.public_key)
            self.blockchain = blockchain.Blockchain([god_tx])
        else:
            self.gossip()

    # this would normally be a network call, using terminal for convenience
    def get_peer_port(self):
        while True:
            user_input = input("Seed node at port (type 'GOD' if God node): ")
            if user_input == 'GOD':
                # TODO - REMOVE HARD-CODED SEED BELOW
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

    def gossip(self, TTL=1, peers=1):

        print("Gossiping, with TTL: %s" % TTL)

        # prepare message to post to peer
        message = self.generate_update_message(TTL)

        # Gossip to x peers!
        if self.peer_ports:
            for i in range(0, peers):
                self.post_message_to_random_peer(message)


    # Nodes communicate via their latest blockchain
    def generate_update_message(self, TTL=1):

        # Create message
        message = {}
        message['originating_port'] = self.port
        message['originating_public_key'] = self.public_key
        message['originating_peer_ports'] = self.peer_ports
        message['TTL'] = TTL
        message['blockchain'] = self.blockchain

        # return message as json
        return jsonpickle.encode(message)

    def post_message_to_random_peer(self, message):

        # Create URL path for random peer node's gossip endpoint
        post_to_url = host_url + (":%s" % random.choice(self.peer_ports)) + '/gossip'

        try:
            # send POST request with new state
            print("Sending POST request to URL: %s" % post_to_url)
            resp = requests.post(post_to_url, json=message)

            # they'll respond with message that includes blockchain
            resp_json = json.dumps(resp.json())
            decoded_json = jsonpickle.decode(resp_json)
            self.save_message_to_cache(decoded_json) # save response to cache

            # retrieve blockchain and run fork choice
            peer_blockchain = decoded_json['blockchain']
            if peer_blockchain:
                self.blockchain = blockchain.fork_choice(self.blockchain, peer_blockchain)
            node.update_network_state_with_message(decoded_json)
        except:
            print("POST Request failed!")

    def save_message_to_cache(self, message):
        self.message_cache.append(message)

    def add_peer(self, port):
        if not str(port) == self.port: # don't add own port...
            self.peer_ports.append(port)

    def update_network_state_with_message(self, message):
        originating_port = message['originating_port']
        originating_public_key = message['originating_public_key']
        self.network_state[originating_port] = originating_public_key

        # Add peer & their known peers to our known peer ports
        known_peers = message['originating_peer_ports']
        known_peers.append(originating_port)
        for port in known_peers:
            if int(port) not in self.peer_ports:
                self.add_peer(int(port))
                print("New peer port value: %s" % self.peer_ports)



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

    # new transaction from form
    if request.method == "POST":
        print("POST request received with form data:")
        error = ""
        try:
            new_tx = create_transaction_with_form_data(request.form)
            node.blockchain.add_transactions([new_tx])
            node.gossip(TTL=2, peers=2) # gossip new blockchain, with time to live of 2
        except Exception as exception:
            error = exception.args[0]
            print("Exception.args: %s" % error)

        return render_front_page(errors=error)

def create_transaction_with_form_data(form):
    to_pk = form['to_public_key']
    amount = int(form['amount'])
    sk = form['secret_key']

    tx = transaction.Transaction(node.public_key, to_pk, amount)
    tx.sign(sk)

    node.blockchain.validate_transaction(tx, throw_exception=True)
    return tx



@app.route("/gossip", methods = ['GET', 'POST'])
def handle_gossip():

    if request.method == "GET":
        return render_front_page()

    if request.method == "POST":
        # save message to cache
        request_json = request.get_json()
        decoded_json = jsonpickle.decode(request_json)
        node.save_message_to_cache(decoded_json)

        # retrieve blockchain and run fork choice
        peer_blockchain = decoded_json['blockchain']
        if peer_blockchain:
            node.blockchain = blockchain.fork_choice(node.blockchain, peer_blockchain)
        node.update_network_state_with_message(decoded_json)

        # check message's TTL to see if we need to gossip
        # message_ttl = decoded_json['TTL']
        # print("Message received with TTL: %s" % message_ttl)
        # if message_ttl > 1:
        #     new_ttl = message_ttl - 1
        #     node.gossip(TTL=new_ttl)

        return node.generate_update_message()



if __name__ == "__main__":

    # * Create Node *
    node = Node()

    # view node in web browser in new tab
    # webbrowser.open(host_url + (":%s" % node.port), new=2)

    app.run(host="127.0.0.1", port=int(node.port))
