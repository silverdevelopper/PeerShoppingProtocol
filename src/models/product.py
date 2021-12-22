from models.base_model import BaseModel


class Product(BaseModel):
    def __init__(
        self,
        name: str = "",
        unit_key: str = "",
        amount: float = 0,
        keywords: list[str] = [],
    ):
        super().__init__(name, name)
        self.unit_key = unit_key
        self.amount = amount
        self.keywords = keywords

    def to_string(self):
        return f"{self.name}::{self.unit_key}::{self.amount}"

    def has_keywords(self, keywords: list[str]):
        for keyword in keywords:
            if keyword.lower() in self.keywords:
                return True
        return False
