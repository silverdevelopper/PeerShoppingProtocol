import threading
from typing import Union
from models.demand import Demand
from models.offer import Offer
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
    ):
        super().__init__(uuid, ip, port, geoloc, "A", keywords)
        self.demands = demands
        self.offers = offers
        self.subscribers: list = []

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
        self.__notify_offer_change()

    def create_demand(self, name, requested_product, exchange_product):
        demand_uuid = uuid4()
        new_demand = Demand(demand_uuid, name, requested_product, exchange_product)
        self.demands.append(new_demand)
        self.__notify_demand_change()

    def handle_transaction_request(self, request: TransactionRequest):
        if request.mode == "D":
            # check if peer have the exchange product in any offer
            for offer in self.offers:
                if offer.offered_product.can_be_exchanged_with(request.exc_product):
                    # remove offer or reduce its amount
                    if offer.offered_product.amount == request.exc_product.amount:
                        self.__remove_offer_by_id(offer.uuid)
                    else:
                        offer.offered_product.amount -= request.exc_product.amount

            # remove demand
            self.__remove_demand_by_id(request.offer_or_demand.uuid)
            return "TD"

        if request.mode == "O":
            # check if peer want the exchange product in any demand
            for demand in self.demands:
                if demand.requested_product.can_be_exchanged_with(request.exc_product):
                    # remove demand or reduce its amount
                    if demand.requested_product.amount == request.exc_product.amount:
                        self.__remove_demand_by_id(demand.uuid)
                    else:
                        demand.requested_product.amount -= request.exc_product.amount
            # remove offer
            self.__remove_offer_by_id(request.offer_or_demand.uuid)
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
