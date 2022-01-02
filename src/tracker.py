import logging
import socket
import time
from models.peer_info import PeerInfo
from typing import Tuple, Union


class Tracker:
    __peers: dict[str, PeerInfo] = dict()

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

    def get_peer_by_address(self, address: Tuple[str, int]):
        for peer in self.__peers.values():
            if peer.ip == address[0] and peer.port == address[1]:
                return peer

        return None

    def get_peer_by_uuid(self, uuid: str):
        return self.__peers[uuid]

    def send_message_to_peer(
        self,
        peer_uuid: str,
        message_or_message_list: Union[str, list[str]],
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
