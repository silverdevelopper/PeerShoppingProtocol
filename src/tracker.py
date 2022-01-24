import logging
import socket
from models.peer_info import PeerInfo
from typing import Tuple, Union


GLOBAL_TRACKER_IP, GLOBAL_TRACKER_PORT = "ec2-3-15-222-217.us-east-2.compute.amazonaws.com", 23456


class Tracker:
    def __init__(
        self,
        uuid: str,
        ip: str,
        port: int,
        geoloc: str,
        type="T",
        keywords: str = "",
    ):
        uuid = "43"
        self.socket = socket
        self.peers: dict[str, PeerInfo] = dict()
        self.info = PeerInfo(uuid, ip, port, geoloc, type, keywords)
        self.uuid = uuid
        self.on_change_callbacks = []

        #self.register(self.info)
        self.fetch_peers_from_tracker(GLOBAL_TRACKER_IP, GLOBAL_TRACKER_PORT)

    def register(self, request_or_peer: Union[str, PeerInfo]):
        if isinstance(request_or_peer, PeerInfo):
            peer = request_or_peer
        else:
            tokens = request_or_peer.split("::")

            if len(tokens) != 7:
                logging.info(f"Registration request rejected.")
                return None

            _, uuid, ip, port, geoloc, node_type, keywords = tokens
            peer = PeerInfo(uuid, ip, port, geoloc, node_type, keywords)

        self.peers[peer.uuid] = peer

        logging.info(f"Registered {peer.to_string('Peer')}")
        self.run_on_change_callbacks()
        return peer

    def get_peers(self):
        return self.peers.values()

    def get_peer_by_address(self, address: Tuple[str, int]):
        for peer in self.peers.values():
            if peer.ip == address[0] and peer.port == address[1]:
                return peer

        return None

    def to_string(self, prefix: str):
        return self.info.to_string(prefix)

    def fetch_peers_from_tracker(self, tracker_ip: str, tracker_port: int):
        tracker_socket = socket.socket()
        try:
            tracker_socket.connect((tracker_ip, tracker_port))
        except Exception as e:
            logging.error(f"Could not connect to global tracker.")
            print(e)
            tracker_socket.close()
            # raise Exception("Could not connect to global tracker.")
            return

        # Ignore first hello message
        tracker_socket.recv(1024)
        tracker_socket.send(self.to_string("RG").encode())

        response = tracker_socket.recv(1024).decode().strip()

        if response != "RO":
            logging.error(
                f"Received unexpected response from tracker while registering: {response}"
            )
            return

        logging.info(f"Registered to global tracker")

        tracker_socket.send("CS".encode())

        is_ended = False
        while not is_ended:
            responses = tracker_socket.recv(1024).decode().strip().split("\n")
            for response in responses:
                if response == "CO::BEGIN":
                    continue
                elif response == "CO::END":
                    is_ended = True
                else:
                    self.register(response)

        tracker_socket.close()
        logging.info(f"Fetched peers from global tracker")

    def get_peer_by_uuid(self, uuid: str):
        return self.peers[uuid]

    def connect_to_peer(self, peer_uuid: str):
        peer_info = self.get_peer_by_uuid(peer_uuid)
        peer_socket = socket.socket()
        try:
            peer_socket.connect((peer_info.ip, peer_info.port))
        except Exception as e:
            logging.error(f"Could not connect to {peer_info.to_string('Peer')}")
            peer_socket.close()
            return None

        # Ignore first hello message
        peer_socket.recv(1024)
        # Register to peer
        peer_socket.send(self.to_string("RG").encode())

        response = peer_socket.recv(1024).decode().strip()

        if response != "RO":
            logging.error(
                f"Received unexpected response from peer while registering to {peer_info.to_string('Peer')} -> {response}"
            )
            peer_socket.close()
            return None

        return peer_socket

    def run_on_change_callbacks(self):
        for callback in self.on_change_callbacks:
            callback()