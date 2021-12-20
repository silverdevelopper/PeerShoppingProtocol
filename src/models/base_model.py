import json
class BaseModel:
    def __init__(self,name:str = "",desc:str = "") -> None:
        self.name = name
        self.desc = desc
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
        sort_keys=True, indent=4)