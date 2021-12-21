from models.base_model import BaseModel


class PeerModel(BaseModel):
    def __init__(
        self,
        uuid: str,
        ip: str,
        port: int,
        geoloc: str,
        node_type: str,
        keywords: str,
    ):
        super().__init__(uuid, keywords)
        self.uuid = uuid
        self.ip = ip
        self.port = port
        self.geoloc = geoloc
        self.node_type = node_type
        self.keywords = keywords

    def to_string(self, prefix=""):
        return f"{prefix}::{self.uuid}::{self.ip}::{self.port}::{self.geoloc}::{self.node_type}::{self.keywords}"
