import logging
import socket
from models.peer_info import PeerInfo
from typing import Tuple


class Tracker:
    __peers: dict[PeerInfo] = dict()

    def __init__(self, uuid: str):
        self.socket = socket
        self.uuid = uuid

    def register(self, request: str):
        tokens = request.split("::")

        if len(tokens) != 7:
            logging.info(f"Registration request rejected.")
            return "RN"

        _, uuid, ip, port, geoloc, node_type, keywords = tokens
        peer = PeerInfo(uuid, ip, port, geoloc, node_type, keywords)
        self.__peers[uuid] = peer

        logging.info(f"Registered {uuid}:{ip}:{port}")

        return "RO"

    def get_peers(self):
        return self.__peers.values()

    def get_peer_by_address(self, address: Tuple[str, int]) -> PeerInfo:
        for peer in self.__peers.values():
            if peer.ip == address[0] and peer.port == address[1]:
                return peer

        return None
