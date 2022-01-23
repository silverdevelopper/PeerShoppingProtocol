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
from uuid import uuid4


class TrackerConnectionThread(threading.Thread):
    def __init__(
        self, tracker: Tracker, cli_socket: socket.socket, cli_address: Tuple[str, int]
    ):
        threading.Thread.__init__(self)
        self.cli_socket = cli_socket
        self.tracker = tracker
        self.cli_address = cli_address
        self.is_listening = True
        self.client_peer_info = None

    def run(self):
        self.cli_socket.send(f"HE::{self.tracker.uuid}\n".encode())

        while self.is_listening:
            request = self.cli_socket.recv(1024).decode().strip()
            logging.info(f"{self.cli_address[0]} > {request}")
            is_understood = self.parse_request(request)

            if not is_understood:
                try:
                    self.cli_socket.send("ER\n".encode())
                except Exception as e:
                    logging.error(e)
                    print(e)
                    self.is_listening = False
                    # raise Exception(str(e)+"\n Request:"+request)

    def parse_request(self, request: str):
        request_type, *request_tokens = request.split("::")

        if request_type == "RG":
            peer_info = self.tracker.register(request)
            response = "RN" if peer_info is None else "RO"
            self.cli_socket.send(f"{response}\n".encode())
            logging.info(f"{self.cli_address[0]} < {response}")
            self.client_peer_info = peer_info
            return True

        # all requests below this point require peer to be registered
        if self.client_peer_info is None:
            return False

        if request_type == "IG":
            self.cli_socket.send(f"OG::{self.tracker.uuid}\n".encode())

        elif request_type == "QU":
            self.cli_socket.send("BY\n".encode())
            self.cli_socket.close()
            logging.info(f"Connection ended with IP: {self.cli_address[0]}\n")
            self.is_listening = False

        elif request_type == "CS":
            peers = self.tracker.get_peers()
            counter = 0

            if len(request_tokens) == 2:
                geo = request_tokens[0]
                num = int(request_tokens[1])
            elif len(request_tokens) == 0:
                num = -1
            else:
                num = 0
                return False

            self.cli_socket.send("CO::BEGIN\n".encode())
            time.sleep(0.1)
            for peer_info in peers:
                if counter == num:
                    break
                self.cli_socket.send(f"{peer_info.to_string(prefix='CO')}\n".encode())
                counter += 1
                time.sleep(0.1)

            self.cli_socket.send("CO::END\n".encode())

        else:
            return False

        return True


class PeerConnectionThread(TrackerConnectionThread):
    def __init__(
        self,
        peer: Peer,
        cli_socket: socket.socket,
        cli_address: Tuple[str, int],
    ):
        super().__init__(peer, cli_socket, cli_address)
        # This is just for naming it as "peer"
        self.peer = peer

    def parse_request(self, request: str):
        request_type, *request_tokens = request.split("::")

        is_understood = super().parse_request(request)
        if is_understood:
            return True

        # all requests below this point require peer to be registered
        if self.client_peer_info is None:
            return False

        elif request_type == "DM":
            if len(request_tokens) != 2:
                return False

            mode = request_tokens[0]
            demands_to_send: list[Demand]

            if mode == "N":
                amount = int(request_tokens[1])

                if amount < 0:
                    return False
                
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

            self.cli_socket.send("DO::BEGIN\n".encode())
            time.sleep(0.1)

            for demand in demands_to_send:
                self.cli_socket.send(f"{demand.to_string('DO')}\n".encode())
                time.sleep(0.1)

            self.cli_socket.send("DO:END\n".encode())

        # This is pretty much identical to demands
        elif request_type == "OF":
            if len(request_tokens) != 2:
                return False

            mode = request_tokens[0]
            offers_to_send: list[Offer]

            if mode == "N":
                amount = int(request_tokens[1])

                if amount < 0:
                    return False
                
                offers_to_send = self.peer.offers[:amount]

            elif mode == "K":
                keywords = request_tokens[1].split(",")
                offers_to_send = [
                    offer 
                    for offer in self.peer.offers 
                    if offer.has_keywords(keywords)
                ]
            else:
                return False

            self.cli_socket.send("OO::BEGIN\n".encode())
            time.sleep(0.1)

            for offer in offers_to_send:
                self.cli_socket.send(f"{offer.to_string('OO')}\n".encode())
                time.sleep(0.1)

            self.cli_socket.send("OO:END\n".encode())

        elif request_type == "MS":
            message = "::".join(request_tokens)
            self.peer.receive_message(message, self.peer.info)
            self.cli_socket.send("MO\n".encode())

        elif request_type == "SB":
            mode = request_tokens[0]
            if mode == "T":
                self.peer.add_subscriber(self.client_peer_info.uuid)
                self.cli_socket.send("SO\n".encode())
                logging.info(f"New subscriber {self.client_peer_info.uuid}")
                print("Subscriber added successfully")
            elif mode == "F":
                self.peer.remove_subscriber(self.client_peer_info.uuid)
                self.cli_socket.send("SO\n".encode())
                logging.info(f"Subscriber removed {self.client_peer_info.uuid}")
                print("Someone unsubscribed...")
            else:
                return False

        elif request_type == "TR":
            if len(request_tokens) != 5:
                return False

            (
                mode,
                demand_offer_uuid,
                exchange_name,
                exchange_unit,
                exchange_amount,
            ) = request_tokens

            if mode == "D":
                offer_or_demand = self.peer.get_demand_by_id(demand_offer_uuid) 
            elif mode == "O":
                offer_or_demand = self.peer.get_offer_by_id(demand_offer_uuid)
            else:
                self.cli_socket.send("TN".encode())
                return True

            if offer_or_demand is None:
                self.cli_socket.send("TN".encode())
                return True

            product = Product(exchange_name, exchange_unit, exchange_amount)
            request = TransactionRequest(uuid4(), mode, self.peer.uuid, demand_offer_uuid, product)

            response = self.peer.handle_transaction_request(request)
            self.cli_socket.send(response.encode())

        elif request_type == "BL":
            is_blocked = request_tokens[0]

            if is_blocked == "T":
                self.peer.add_peer_to_blocked_from(self.client_peer_info.uuid)
                self.cli_socket.send("BO\n".encode())
            elif is_blocked == "F":
                self.peer.remove_peer_from_blocked_from(self.client_peer_info.uuid)
                self.cli_socket.send("BO\n".encode())
            else:
                return False

        else:
            return False
        return True
