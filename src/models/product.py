from models.base_model import BaseModel


class Product(BaseModel):
    def __init__(
        self,
        name: str = "",
        unit_key: str = "",
        amount: float = 0,
        keywords = [],
    ):
        super().__init__(name, name)
        self.unit_key = unit_key
        self.amount = amount

        if isinstance(keywords,str):
            keywords = [keywords]
        self.keywords = keywords

    def to_string(self):
        return f"{self.name}::{self.unit_key}::{self.amount}::{','.join(self.keywords)}"

    def has_keywords(self, keywords: list):
        for keyword in keywords:
            if keyword.lower() in self.keywords:
                return True
        return False

    def can_be_exchanged_with(self, product):
        return (
            self.name == product.name
            and self.unit_key == product.unit_key
            and self.amount >= product.amount
        )
