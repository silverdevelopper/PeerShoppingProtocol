from models.base_model import BaseModel
from models.product import Product


class Offer(BaseModel):
    def __init__(
        self, uuid: str, name: str, offered_product: Product, exchange_product: Product
    ):
        self.uuid = uuid
        self.name = name
        self.offered_product = offered_product
        self.exchange_product = exchange_product

    def to_string(self, prefix: str):
        return f"{prefix}::{self.uuid}::{self.name}::{self.offered_product.to_string()}::{self.exchange_product.to_string()}"

    def has_keywords(self, keywords: list):
        return self.offered_product.has_keywords(
            keywords
        ) or self.exchange_product.has_keywords(keywords)

    '''
    It returns Demand Uuid, Demand Name, Requested Product Name, Requested Product Amount,  Exchange Product Name, Exchange Product Name
    '''
    def to_list(self):
        return [self.uuid,self.name,self.offered_product.name,self.offered_product.amount,self.exchange_product.name,self.exchange_product.amount]
