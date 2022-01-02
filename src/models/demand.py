from models.base_model import BaseModel
from models.product import Product


class Demand(BaseModel):
    def __init__(
        self,
        uuid: str,
        requested_product: Product,
        exchange_product: Product,
    ):
        self.uuid = uuid
        self.requested_product = requested_product
        self.exchange_product = exchange_product

    def to_string(self, prefix: str):
        return f"{prefix}::{self.uuid}::{self.requested_product.to_string()}::{self.exchange_product.to_string()}"

    def has_keywords(self, keywords: list[str]):
        return self.requested_product.has_keywords(
            keywords
        ) or self.exchange_product.has_keywords(keywords)
