from models.demand import Demand
from models.peer_info import PeerInfo
from tracker import Tracker


class Peer(Tracker):
    __info: PeerInfo
    demands: list[Demand]

    def __init__(
        self,
        uuid: str,
        ip: str,
        port: int,
        geoloc: str,
        keywords: str = "",
        demands: list[Demand] = [],
    ):
        super().__init__(uuid)
        self.__info = PeerInfo(uuid, ip, port, geoloc, "A", keywords)
        self.demands = demands

    def to_string(self, prefix=""):
        return self.__info.to_string(prefix)
