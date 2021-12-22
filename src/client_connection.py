import logging
import threading
import socket
from tracker import Tracker


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
            return True
        elif request_type == "QU":
            self.cli_socket.send("BY".encode())
            self.cli_socket.close()
            logging.info(f"Connection ended with IP: {self.cli_address[0]}")
            self.__is_listening = False
            return True
        elif request_type == "RG":
            response = self.tracker.register(request)
            self.cli_socket.send(response.encode())
            logging.info(f"{self.cli_address[0]} < {response}")
            return True
        elif request_type == "CS":
            peers = self.tracker.get_peers()

            self.cli_socket.send("CO::BEGIN".encode())
            for peer in peers:
                self.cli_socket.send(peer.to_string(prefix="CO").encode())
            self.cli_socket.send("CO::END".encode())
            return True

        return False


class PeerConnectionThread(TrackerConnectionThread):
    def __parse_request(self, request: str):
        request_type = request.split("::")[0]

        is_understood = super().__parse_request(request)
        if is_understood:
            return True

        # Benim ekstaradan yapabildiğim kısımlar
        if request_type == "":
            pass
