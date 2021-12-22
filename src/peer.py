from models.demand import Demand
from models.offer import Offer
from models.peer_info import PeerInfo
from tracker import Tracker


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
    ):
        super().__init__(uuid)
        self.__info = PeerInfo(uuid, ip, port, geoloc, "A", keywords)
        self.demands = demands
        self.offers = offers

    def to_string(self, prefix=""):
        return self.__info.to_string(prefix)
