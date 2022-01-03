import threading
from typing import Union
from models.demand import Demand
from models.offer import Offer
from models.peer_info import PeerInfo
from models.transaction import Transaction
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
        transaction_inbox: list = [],
    ):
        super().__init__(uuid, ip, port, geoloc, "A", keywords)
        self.demands = demands
        self.offers = offers
        self.subscribers: list = []
        self.transaction_inbox = transaction_inbox

    def to_string(self, prefix=""):
        return self.info.to_string(prefix)

    def add_subscriber(self, peer_uuid):
        self.subscribers.append(peer_uuid)

    def remove_subscriber(self, peer_uuid):
        self.subscribers.remove(peer_uuid)

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
        new_offer = Demand(offer_uuid, name, offered_product, exchange_product)
        self.offers.append(new_offer)

        self.__notify_subscribers(
            [
                "UO::BEGIN",
                *[offer.to_string("UO::T") for offer in self.offers],
                "UO::END",
            ],
        )

    def create_demand(self, name, requested_product, exchange_product):
        demand_uuid = uuid4()
        new_demand = Demand(demand_uuid, name, requested_product, exchange_product)
        self.demands.append(new_demand)

        self.__notify_subscribers(
            [
                "UB::BEGIN",
                *[demand.to_string("UB::A") for demand in self.demands],
                "UB::END",
            ],
        )

    def list_transactions(self):
        for ta in self.transaction_inbox:
            # TODO: nasıl dondursun?
            pass

    def accept_transaction(self, transaction_uuid):
        for ta in self.transaction_inbox:
            if ta.uuid == transaction_uuid:
                self.transaction_inbox.remove(ta)
                # TODO this should notify the other peer
                return ta
        return None

    # TODO: Suan ikisi de aynı isi yapiyor :/
    def decline_transaction(self, transaction_uuid):
        for ta in self.transaction_inbox:
            if ta.uuid == transaction_uuid:
                self.transaction_inbox.remove(ta)
                # TODO this should notify the other peer
                return ta
        return None

    def __notify_subscribers(
        self,
        message_or_message_list: Union[str, list],
        expected_response_for_each_message="UO",
        unexpected_response_error_code="UN",
    ):
        threads = [
            threading.Thread(
                target=lambda: self.send_message_to_peer(
                    peer_uuid,
                    message_or_message_list,
                    expected_response_for_each_message=expected_response_for_each_message,
                    unexpected_response_error_code=unexpected_response_error_code,
                )
            )
            for peer_uuid in self.subscribers
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
