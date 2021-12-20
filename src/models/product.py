from models.base_model import BaseModel


from base_model import BaseModel

class Product(BaseModel):
    def __init__(self,name:str = "",desc:str = "", unit_key = "") -> None:
        super().__init__(name,desc)
        self.unit_key = unit_key