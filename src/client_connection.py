import logging
import threading
import socket
import time
from typing import Tuple
from models.demand import Demand
from models.offer import Offer
from models.product import Product
from models.transaction import TransactionRequest
from tracker import Tracker
from peer import Peer
from models.peer_info import PeerInfo


class TrackerConnectionThread(threading.Thread):
    def __init__(
        self, tracker: Tracker, cli_socket: socket.socket, cli_address: Tuple[str, int]
    ):
        threading.Thread.__init__(self)
        self.cli_socket = cli_socket
        self.tracker = tracker
        self.cli_address = cli_address
        self.is_listening = True

    def run(self):
        self.cli_socket.send(f"HE::{self.tracker.uuid}".encode())

        while self.is_listening:
            request = self.cli_socket.recv(1024).decode().strip()
            logging.info(f"{self.cli_address[0]} > {request}")
            is_understood = self.parse_request(request)

            if not is_understood:
                try:
                    self.cli_socket.send("ER".encode())
                except Exception as e:
                    logging.error(e)
                    print(e)
                    self.is_listening = False
                    #raise Exception(str(e)+"\n Request:"+request)

    def parse_request(self, request: str):
        request_type = request.split("::")[0]
        if request_type == "IG":
            self.cli_socket.send(f"OG::{self.tracker.uuid}".encode())

        elif request_type == "QU":
            self.cli_socket.send("BY".encode())
            self.cli_socket.close()
            logging.info(f"Connection ended with IP: {self.cli_address[0]}")
            self.is_listening = False

        elif request_type == "RG":
            peer = self.tracker.register(request)
            response = "RN" if peer is None else "RO"
            self.cli_socket.send(response.encode())
            logging.info(f"{self.cli_address[0]} < {response}")

        elif request_type == "CS":
            peers = self.tracker.get_peers()

            self.cli_socket.send("CO::BEGIN".encode())
            time.sleep(0.1)
            for peer in peers:
                self.cli_socket.send(peer.to_string(prefix="CO").encode())
                time.sleep(0.1)

            self.cli_socket.send("CO::END".encode())

        else:
            return False

        return True


class PeerConnectionThread(TrackerConnectionThread):
    def __init__(
        self,
        peer: Peer,
        client_peer_info: PeerInfo,
        cli_socket: socket.socket,
        cli_address: Tuple[str, int],
    ):
        super().__init__(peer, cli_socket, cli_address)
        # This is just for naming it as "peer"
        self.peer = peer
        self.client_peer_info = client_peer_info

    def parse_request(self, request: str):
        request_type, *request_tokens = request.split("::")

        is_understood = super().parse_request(request)
        if is_understood:
            return True

        elif request_type == "DM":
            if len(request_tokens) != 2:
                return False

            mode = request_tokens[0]
            demands_to_send: list[Demand]

            if mode == "N":
                amount = int(request_tokens[1])
                demands_to_send = self.peer.demands[:amount]

            elif mode == "K":
                keywords = request_tokens[1].split(",")
                demands_to_send = [
                    demand
                    for demand in self.peer.demands
                    if demand.has_keywords(keywords)
                ]
            else:
                return False

            self.cli_socket.send("DO::BEGIN".encode())
            time.sleep(0.1)

            for demand in demands_to_send:
                self.cli_socket.send(demand.to_string("DO").encode())
                time.sleep(0.1)

            self.cli_socket.send("DO:END".encode())

        # This is pretty much identical to demands
        elif request_type == "OF":
            if len(request_tokens) != 2:
                return False

            mode = request_tokens[0]
            offers_to_send: list[Offer]

            if mode == "N":
                amount = int(request_tokens[1])
                offers_to_send = self.peer.offers[:amount]

            elif mode == "K":
                keywords = request_tokens[1].split(",")
                offers_to_send = [
                    offer for offer in self.peer.offers if offer.has_keywords(keywords)
                ]
            else:
                return False

            self.cli_socket.send("OO::BEGIN".encode())
            time.sleep(0.1)

            for offer in offers_to_send:
                self.cli_socket.send(offer.to_string("OO").encode())
                time.sleep(0.1)

            self.cli_socket.send("OO:END".encode())

        elif request_type == "MS":
            message = request_tokens[0]
            print("received message:", message)
            self.cli_socket.send("MO".encode())

        elif request_type == "SB":
            mode = request_tokens[0]
            if mode == "T":
                self.peer.add_subscriber(self.client_peer_info.uuid)
                logging.info(f"New subscriber {self.client_peer_info.uuid}")
                print("Subscriber added successfully")
            elif mode == "F":
                self.peer.remove_subscriber(self.client_peer_info.uuid)
                logging.info(f"Subscriber removed {self.client_peer_info.uuid}")
                print("Someone unsubscribed...")
            else:
                return False

        elif request_type == "TR":
            if len(request_tokens) != 5:
                return False

            (
                mode,
                demand_or_offer_id,
                exchange_name,
                exchange_unit,
                exchange_amount,
            ) = request_tokens

            offer_or_demand = self.peer.get_demand_by_id(
                demand_or_offer_id
            ) or self.peer.get_offer_by_id(demand_or_offer_id)

            if offer_or_demand is None:
                self.cli_socket.send("TN".encode())
                return True

            product = Product(exchange_name, exchange_unit, exchange_amount)
            request = TransactionRequest(mode, self.peer.uuid, offer_or_demand, product)

            response = self.peer.handle_transaction_request(request)
            self.cli_socket.send(response.encode())

        else:
            return False
        return True
