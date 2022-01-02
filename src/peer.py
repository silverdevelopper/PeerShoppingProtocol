from models.demand import Demand
from models.offer import Offer
from models.peer_info import PeerInfo
from tracker import Tracker


class Peer(Tracker):
    def __init__(
        self,
        uuid: str,
        ip: str,
        port: int,
        geoloc: str,
        keywords: str = "",
        demands: list[Demand] = [],
        offers: list[Offer] = [],
    ):
        super().__init__(uuid, ip, port, geoloc, "A", keywords)
        self.demands = demands
        self.offers = offers
        self.subscribers = []

    def to_string(self, prefix=""):
        return self.info.to_string(prefix)

    def add_subscriber(self, peer_uuid):
        self.subscribers.append(peer_uuid)

    def remove_subscriber(self, peer_uuid):
        self.subscribers.remove(peer_uuid)

    def get_offer_by_id(self, offer_id):
        for offer in self.offers:
            if offer.id == offer_id:
                return offer
        return None

    def get_demand_by_id(self, demand_id):
        for demand in self.demands:
            if demand.id == demand_id:
                return demand
        return None
