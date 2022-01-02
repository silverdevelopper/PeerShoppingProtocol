from models.demand import Demand
from models.offer import Offer
from models.peer_info import PeerInfo
from models.transaction import Transaction
from tracker import Tracker
from uuid import uuid4

class Peer(Tracker):
    __info: PeerInfo

    def __init__(
        self,
        uuid: str,
        ip: str,
        port: int,
        geoloc: str,
        keywords: str = "",
        demands: list[Demand] = [],
        offers: list[Offer] = [],
        transaction_inbox: list[Transaction] = [],
    ):
        super().__init__(uuid)
        self.__info = PeerInfo(uuid, ip, port, geoloc, "A", keywords)
        self.demands = demands
        self.offers = offers
        self.subscribers = []
        self.transaction_inbox = transaction_inbox

    def to_string(self, prefix=""):
        return self.__info.to_string(prefix)

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

        for sub in self.subscribers:
            #TODO: Send message to sub
            pass

    def create_demand(self, name, requested_product, exchange_product):
        demand_uuid = uuid4()
        new_demand = Demand(demand_uuid, name, requested_product, exchange_product)
        self.demands.append(new_demand)

        for sub in self.subscribers:
            #TODO: Send message to sub
            pass

    def list_transactions(self):
        for ta in self.transaction_inbox:
            #TODO: nasıl dondursun?
            pass

    def accept_transaction(self, transaction_uuid):
        for ta in self.transaction_inbox:
            if ta.uuid == transaction_uuid:
                self.transaction_inbox.remove(ta)
                return ta
        return None

    #TODO: Suan ikisi de aynı isi yapiyor :/
    def decline_transaction(self, transaction_uuid):
        for ta in self.transaction_inbox:
            if ta.uuid == transaction_uuid:
                self.transaction_inbox.remove(ta)
                return ta
        return None
