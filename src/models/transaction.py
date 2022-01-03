from typing import Union
from models.base_model import BaseModel
from models.demand import Demand
from models.offer import Offer
from models.product import Product


class TransactionRequest(BaseModel):
    def __init__(
        self,
        type: str,
        peer_uuid: str,
        offer_or_demand: Union[Offer, Demand],
        exc_product: Product,
    ):
        self.type = type
        self.peer_uuid = peer_uuid
        self.exc_product = exc_product
        self.offer_or_demand = offer_or_demand

    def to_string(self, prefix=""):
        return f"{prefix}::{self.offer_or_demand}::{self.offer_or_demand.uuid}::{self.exc_product}"

    def has_keywords(self, keywords: list[str]):
        return self.offer_or_demand.has_keywords(keywords)
