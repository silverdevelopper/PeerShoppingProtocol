from models.base_model import BaseModel
from models.product import Product

class Transaction(BaseModel):
    def __init__(
        self,
        offer_or_demand,
        uuid: str,
        offer_uuid: str,
        exc_product: Product
    ):
        self.offer_or_demand = offer_or_demand
        self.uuid = uuid
        self.offer_uuid = offer_uuid
        self.exc_product = exc_product

    def to_string(self, prefix=""):
        return f"{prefix}::{self.offer_or_demand}::{self.offer_uuid}::{self.exc_product}"

    def has_keywords(self, keywords: list[str]):
        pass
