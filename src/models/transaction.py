from typing import Union
from models.base_model import BaseModel
from models.demand import Demand
from models.offer import Offer
from models.product import Product


class TransactionRequest(BaseModel):
    def __init__(
        self,
        ta_uuid: str,
        mode: str,
        peer_uuid: str,
        offer_demand_uuid: str,
        exc_product: Product,
    ):
        self.ta_uuid = ta_uuid
        self.mode = mode
        self.peer_uuid = peer_uuid
        self.offer_demand_uuid = offer_demand_uuid
        self.exc_product = exc_product

    def to_string(self, prefix: str):
        return f"{prefix}::{self.type}::{self.offer_or_demand.uuid}::{self.exc_product.to_string()}"

    def has_keywords(self, keywords: list):
        return self.offer_or_demand.has_keywords(keywords) or self.exc_product.has_keywords(keywords)
