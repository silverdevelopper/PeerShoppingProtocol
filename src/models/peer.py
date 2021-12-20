from base_model import BaseModel
class PeerModel(BaseModel):
    # CO:<uuid>::<ip>:<port>::<geoloc>::<type>::<keywords>
    def __init__(self,name:str,geoloc,uuid,ip,port:int,node_type,keywords:str = ""):
        super().__init__(name,keywords)
        self.geoloc = geoloc
        self.node_type = node_type
        self.uuid = uuid