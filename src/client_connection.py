import threading
import socket
from tracker import Tracker


class ConnectionThread(threading.Thread):
    def __init__(self, tracker: Tracker, cli_socket: socket.socket):
        threading.Thread.__init__(self)
        self.cli_socket = cli_socket
        self.tracker = tracker

    def run(self):
        self.cli_socket.send(f"HE::{self.tracker.uuid}".encode())

        while True:
            request = self.cli_socket.recv(1024).decode().strip()
            request_type = request.split("::")[0]

            if request_type == "IG":
                self.cli_socket.send(f"OG::{self.tracker.uuid}".encode())
            elif request_type == "QU":
                self.cli_socket.send("BY".encode())
                self.cli_socket.close()
                break
            elif request_type == "RG":
                response = self.tracker.register(request)
                self.cli_socket.send(response.encode())
            elif request_type == "CS":
                peers = self.tracker.get_peers()

                self.cli_socket.send("CO::BEGIN".encode())
                for peer in peers:
                    self.cli_socket.send(peer.to_string(prefix="CO").encode())
                self.cli_socket.send("CO::END".encode())
