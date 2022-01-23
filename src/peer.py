import threading
from typing import Tuple
from models.peer_info import PeerInfo
from models.demand import Demand
from models.offer import Offer
from models.product import Product
from models.transaction import TransactionRequest
from tracker import Tracker
from uuid import uuid4


class Peer(Tracker):
    def __init__(
        self,
        uuid: str,
        ip: str,
        port: int,
        geoloc: str,
        keywords: str = "",
        demands: list = [],
        offers: list = [],
        trade_history: dict = {},
    ):
        super().__init__(uuid, ip, port, geoloc, "A", keywords)
        self.demands = demands
        self.offers = offers
        self.trade_history = trade_history
        self.subscribers: set = set()
        self.block_list: set = set()
        self.blocked_from: set = set()

    def to_string(self, prefix=""):
        return self.info.to_string(prefix)

    def add_subscriber(self, peer_uuid):
        self.subscribers.add(peer_uuid)

    def remove_subscriber(self, peer_uuid):
        self.subscribers.remove(peer_uuid)

    def is_subscribed(self, peer_uuid: str):
        return peer_uuid in self.subscribers

    def add_peer_to_block_list(self, peer_uuid: str):
        if peer_uuid not in self.block_list:
            self.block_list.add(peer_uuid)
        if self.is_subscribed(peer_uuid):
            self.remove_subscriber(peer_uuid)

    def remove_peer_from_block_list(self, peer_uuid: str):
        self.block_list.remove(peer_uuid)

    def add_peer_to_blocked_from(self, peer_uuid: str):
        if peer_uuid not in self.blocked_from:
            self.blocked_from.add(peer_uuid)
        if self.is_subscribed(peer_uuid):
            self.remove_subscriber(peer_uuid)
    
    #Adi garip biliyorum ama tutarli olsun diye yaptim
    def remove_peer_from_blocked_from(self, peer_uuid: str):
        self.blocked_from.remove(peer_uuid)

    def is_blocked(self,peer_uuid: str):
        return peer_uuid in self.block_list

    def get_peers(self):
        return [peer for peer in super().get_peers() if peer.uuid not in self.block_list]

    def get_peer_by_address(self, address: Tuple[str, int]):
        peer = super().get_peer_by_address(address)
        if peer is None or self.is_blocked(peer.uuid):
            return None
        return peer

    def get_offer_by_id(self, offer_id):
        for offer in self.offers:
            if offer.uuid == offer_id:
                return offer
        return None

    def get_demand_by_id(self, demand_id):
        for demand in self.demands:
            if demand.uuid == demand_id:
                return demand
        return None

    def create_offer(self, name, offered_product, exchange_product):
        offer_uuid = uuid4()
        new_offer = Offer(offer_uuid, name, offered_product, exchange_product)
        self.offers.append(new_offer)
        self.__notify_offer_change()

    def create_demand(self, name, requested_product, exchange_product):
        demand_uuid = uuid4()
        new_demand = Demand(demand_uuid, name, requested_product, exchange_product)
        self.demands.append(new_demand)
        self.__notify_demand_change()

    def receive_message(self, message: str, sender: PeerInfo):
        print("received the following message from", sender.to_string())
        print(message)

    def send_message(self, message: str, peer_uuid: str):
        peer_socket = self.connect_to_peer(peer_uuid)

        if peer_socket is None:
            return False

        peer_socket.send(f"MS::{message}".encode())
        response = peer_socket.recv(1024).decode().strip()
        peer_socket.close()

        # return if the message was sent successfully
        return response == "MO"

    def send_transaction_request(self, offer_or_demand, target_uuid: str, 
                                 offer_demand_uuid: str, exchange_product: Product):
        ta_request = TransactionRequest(uuid4(), offer_or_demand, target_uuid, offer_demand_uuid, exchange_product)
        
        #TODO: obje mi eklensin yoksa to_str mi?
        self.trade_history[ta_request.ta_uuid] = ta_request

        peer_socket = self.connect_to_peer(target_uuid)
        if peer_socket is None:
            return False

        peer_socket.send(ta_request.to_string().encode())
        response = peer_socket.recv(1024).decode().strip()
        peer_socket.close()

        # return if the message was sent successfully
        return response == "TO"

    def handle_transaction_request(self, request: TransactionRequest):
        if request.mode == "D":
            # check if peer have the exchange product in any offer
            to_offer = self.get_offer_by_id(request.offer_demand_uuid)
            if to_offer.offered_product.can_be_exchanged_with(request.exc_product):
                # remove offer or reduce its amount
                if to_offer.offered_product.amount <= request.exc_product.amount:
                    self.__remove_offer_by_id(to_offer.uuid)
                else:
                    to_offer.offered_product.amount -= request.exc_product.amount

            #Kaldirdim cunku demand bizim degil, karsinin
            # remove demand
            #self.__remove_demand_by_id(request.offer_demand_uuid)
            self.trade_history[request.ta_uuid] = request
            return "TD"

        if request.mode == "O":
            # check if peer want the exchange product in any demand
            to_demand = self.get_demand_by_id(request.offer_demand_uuid)
            if to_demand.requested_product.can_be_exchanged_with(request.exc_product):
                # remove demand or reduce its amount
                if to_demand.requested_product.amount <= request.exc_product.amount:
                    self.__remove_demand_by_id(to_demand.uuid)
                else:
                    to_demand.requested_product.amount -= request.exc_product.amount
            
            #Kaldirdim cunku offer bizim degil, karsinin
            # remove offer
            #self.__remove_offer_by_id(request.offer_demand_uuid)
            self.trade_history[request.ta_uuid] = request
            return "TD"

        return "TN"

    def __remove_demand_by_id(self, demand_id: str):
        for demand in self.demands:
            if demand.uuid == demand_id:
                self.demands.remove(demand)
                self.__notify_demand_change()
                return

    def __remove_offer_by_id(self, offer_id: str):
        for offer in self.offers:
            if offer.uuid == offer_id:
                self.offers.remove(offer)
                self.__notify_offer_change()
                return

    def __notify_demand_change(self):
        self.__notify_subscribers(
            [
                "UB::BEGIN",
                *[demand.to_string("UB::A") for demand in self.demands],
                "UB::END",
            ],
        )

    def __notify_offer_change(self):
        self.__notify_subscribers(
            [
                "UO::BEGIN",
                *[offer.to_string("UO::T") for offer in self.offers],
                "UO::END",
            ],
        )

    def __notify_subscribers(self, message_list: list):
        def callback(peer_uuid: str):
            peer_socket = self.connect_to_peer(peer_uuid)
            if peer_socket is None:
                return

            for message in message_list:
                peer_socket.send(message.encode())
                response = peer_socket.recv(1024).decode().strip()
                if response != "UO":
                    peer_socket.send("UN".encode())
                    break

            peer_socket.close()

        threads = [
            threading.Thread(target=lambda: callback(peer_uuid))
            for peer_uuid in self.subscribers
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
