import socket
from models.peer import PeerModel


class Tracker:
    __peers: dict[PeerModel] = dict()

    def __init__(self, uuid: str):
        self.socket = socket
        self.uuid = uuid

    def register(self, request: str):
        tokens = request.split("::")

        if len(tokens) < 7:
            return "RN"

        _, uuid, ip, port, geoloc, node_type, keywords = tokens
        peer = PeerModel(uuid, ip, port, geoloc, node_type, keywords)
        self.__peers[uuid] = peer

        return "RO"

    def get_peers(self):
        return self.__peers.values()
