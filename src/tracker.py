import logging
import socket
import time
from models.peer_info import PeerInfo
from typing import Tuple, Union


GLOBAL_TRACKER_IP, GLOBAL_TRACKER_PORT = "13.59.56.189", 23456


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
        self.register(self.info)
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
        except:
            logging.error(f"Could not connect to global tracker.")
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
            response = tracker_socket.recv(1024).decode().strip()
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

    def send_message_to_peer(
        self,
        peer_uuid: str,
        message_or_message_list: Union[str, list],
        expected_response_for_each_message: str = None,
        error_code_for_unexpected_response: str = None,
        get_response: bool = False,
    ):
        message_list = (
            [message_or_message_list]
            if isinstance(message_or_message_list, str)
            else message_or_message_list
        )

        peer_info = self.get_peer_by_uuid(peer_uuid)

        peer_socket = socket.socket()
        peer_socket.connect((peer_info.ip, peer_info.port))

        for message in message_list:
            peer_socket.send(message.encode())

            if expected_response_for_each_message is not None:
                response = peer_socket.recv(1024).decode().strip()
                if response != expected_response_for_each_message:
                    peer_socket.send(error_code_for_unexpected_response.encode())
                    peer_socket.close()
                    return None
            else:
                time.sleep(0.01)

        if not get_response:
            peer_socket.close()
            return

        response = peer_socket.recv(1024).decode()
        peer_socket.close()

        return response
