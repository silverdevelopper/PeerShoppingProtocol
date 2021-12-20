import socket


class Peer:
    def __init__(
        self,
        uuid: str,
        ip: str,
        port: int,
        geoloc: str,
        node_type: str,
        keywords: str,
    ):
        self.uuid = uuid
        self.ip = ip
        self.port = port
        self.geoloc = geoloc
        self.node_type = node_type
        self.keywords = keywords

    def to_string(self, prefix=""):
        return f"{prefix}::{self.uuid}::{self.ip}::{self.port}::{self.geoloc}::{self.node_type}::{self.keywords}"


class Tracker:
    __peers: dict[Peer] = dict()

    def __init__(self, uuid: str):
        self.socket = socket
        self.uuid = uuid

    def register(self, request: str):
        tokens = request.split("::")

        if len(tokens) < 7:
            return "RN"

        _, uuid, ip, port, geoloc, node_type, keywords = tokens
        peer = Peer(uuid, ip, port, geoloc, node_type, keywords)
        self.__peers[uuid] = peer

        return "RO"

    def get_peers(self):
        return self.__peers.values()
