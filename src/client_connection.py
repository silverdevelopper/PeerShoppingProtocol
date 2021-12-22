import logging
import threading
import socket
from models.demand import Demand
from models.offer import Offer
from tracker import Tracker
from peer import Peer


class TrackerConnectionThread(threading.Thread):
    __is_listening = True

    def __init__(self, tracker: Tracker, cli_socket: socket.socket, cli_address):
        threading.Thread.__init__(self)
        self.cli_socket = cli_socket
        self.tracker = tracker
        self.cli_address = cli_address

    def run(self):
        self.cli_socket.send(f"HE::{self.tracker.uuid}".encode())

        while self.__is_listening:
            request = self.cli_socket.recv(1024).decode().strip()
            logging.info(f"{self.cli_address[0]} > {request}")
            is_understood = self.__parse_request(request)

            if not is_understood:
                self.cli_socket.send("ER".encode())

    def __parse_request(self, request: str):
        request_type = request.split("::")[0]
        if request_type == "IG":
            self.cli_socket.send(f"OG::{self.tracker.uuid}".encode())
        elif request_type == "QU":
            self.cli_socket.send("BY".encode())
            self.cli_socket.close()
            logging.info(f"Connection ended with IP: {self.cli_address[0]}")
            self.__is_listening = False
        elif request_type == "RG":
            response = self.tracker.register(request)
            self.cli_socket.send(response.encode())
            logging.info(f"{self.cli_address[0]} < {response}")
        elif request_type == "CS":
            peers = self.tracker.get_peers()

            self.cli_socket.send("CO::BEGIN".encode())
            for peer in peers:
                self.cli_socket.send(peer.to_string(prefix="CO").encode())
            self.cli_socket.send("CO::END".encode())
        else:
            return False

        return True


class PeerConnectionThread(TrackerConnectionThread):
    def __init__(self, peer: Peer, cli_socket: socket.socket, cli_address):
        super().__init__(peer, cli_socket, cli_address)
        # This is just for naming it as "peer"
        self.peer = peer

    def __parse_request(self, request: str):
        request_type, *request_tokens = request.split("::")

        is_understood = super().__parse_request(request)
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

            self.cli_socket.send("DO::BEGIN")
            for demand in demands_to_send:
                self.cli_socket.send(demand.to_string("DO").encode())
            self.cli_socket.send("DO:END")

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

            self.cli_socket.send("OO::BEGIN")
            for offer in offers_to_send:
                self.cli_socket.send(offer.to_string("OO").encode())
            self.cli_socket.send("OO:END")

        elif request_type == "MS":
            message = request_tokens[0]
            print("received message:", message)
            self.cli_socket.send("MO".encode())

        else:
            return False
        return True
