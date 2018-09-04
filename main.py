import json
import random
import threading
import webbrowser

import jsonpickle
import requests

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

from transaction import transaction
from transaction import signature
import blockchain


app = Flask(__name__)
HOST_URL = "http://127.0.0.1"



# * Classes *
class Node(object):
    def __init__(self):

        self.port = str(input("Create new node on port: "))
        self.public_key = ""
        self.secret_key = ""
        self.network_state = {}
        self.blockchain = None
        self.message_cache = []
        self.peer_ports = self.get_peer_port()

        self.generate_keys()

        if not self.peer_ports:
            god_tx = blockchain.create_god_transaction(self.public_key)
            self.blockchain = blockchain.Blockchain([god_tx])
        else:
            self.gossip()

    def get_peer_port(self):
        while True:
            user_input = input("Seed with node (type 'GOD' if God node): ")
            if user_input == 'GOD':
                return []
            else:
                seed_port = int(user_input)
                if seed_port == int(self.port):
                    print("Can't seed with your own port!")
                else:
                    return [seed_port]

    def generate_keys(self):
        """Generates node's public and private keys"""
        pk, sk = signature.generate_keys()
        self.public_key = pk
        self.secret_key = sk

    def gossip(self, prev_message=None, TTL=1, num_peers=1):
        """Chooses peers to receive gossip message"""

        exclude_peer = None
        if prev_message:
            exclude_peer = int(prev_message.get('originating_port'))
        random_peers = self.select_random_peers(num_peers=num_peers, exclude_peers=[exclude_peer])

        if random_peers:
            for i in range(0, len(random_peers)):
                message = self.generate_update_message(TTL)
                self.post_message_to_peer(message, random_peers[i])

    def select_random_peers(self, num_peers=1, exclude_peers=[]):
        result = []
        peers = self.peer_ports
        if exclude_peers:
            for p in exclude_peers:
                try:
                    peers.remove(p)
                except:
                    pass

        if len(peers) <= num_peers:
            result = peers
        else:
            for i in range(0, num_peers):
                selected = random.choice(peers)
                peers.remove(selected)
                result.append(selected)
        return result

    def generate_update_message(self, TTL=1):
        """Generates gossip message to broadcast to other nodes"""

        message = {}
        message['originating_port'] = self.port
        message['originating_public_key'] = self.public_key
        message['originating_peer_ports'] = self.peer_ports
        message['TTL'] = TTL
        message['blockchain'] = self.blockchain

        return jsonpickle.encode(message)

    def post_message_to_peer(self, message, peer):
        post_to_url = HOST_URL + (":%s" % peer) + '/gossip'
        try:
            print("Sending POST request to URL: %s" % post_to_url)
            resp = requests.post(post_to_url, json=message)

            resp_json = json.dumps(resp.json())
            decoded_json = jsonpickle.decode(resp_json) 
            self.save_message_to_cache(decoded_json)

            peer_blockchain = decoded_json['blockchain']  # Peer's response includes their blockchain
            if peer_blockchain:
                self.blockchain = blockchain.fork_choice(self.blockchain, peer_blockchain)
            node.update_network_state_with_message(decoded_json)
        except:
            print("POST Request failed!")

    def save_message_to_cache(self, message):
        self.message_cache.append(message)

    def add_peer(self, port):
        if not str(port) == self.port:  # No need to include ourselves as a peer...
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



# * Templating *
def render_front_page(errors="", balance=0):
    if node.blockchain:
        balance = blockchain.get_balance(node.public_key, node.blockchain.blocks)
    balance = "{:,.2f}".format(balance)
    return render_template('template.html', node=node, errors=errors, balance=balance)



# * Routes *
@app.route("/", methods = ['GET', 'POST'])
def main():
    if request.method == "GET":
        return render_front_page()

    if request.method == "POST":  # POST requests indicate a new transaction submission
        error = ""
        try:
            new_tx = create_transaction_with_form_data(request.form)
            node.blockchain.add_transactions([new_tx])
            node.gossip(TTL=2, num_peers=3)
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
        # 1. Save message to cache
        request_json = request.get_json()
        decoded_json = jsonpickle.decode(request_json)
        node.save_message_to_cache(decoded_json)

        # 2. Retrieve blockchain and run fork choice
        peer_blockchain = decoded_json['blockchain']
        if peer_blockchain:
            node.blockchain = blockchain.fork_choice(node.blockchain, peer_blockchain)
        node.update_network_state_with_message(decoded_json)

        # 3. Check message's TTL to see if we need to gossip
        message_ttl = decoded_json['TTL']
        if message_ttl > 1:
            new_ttl = message_ttl - 1
            threading.Timer(.5, node.gossip, [decoded_json, new_ttl]).start()

        return node.generate_update_message()



if __name__ == "__main__":

    node = Node()

    webbrowser.open(HOST_URL + (":%s" % node.port), new=2)

    app.run(host="127.0.0.1", port=int(node.port))