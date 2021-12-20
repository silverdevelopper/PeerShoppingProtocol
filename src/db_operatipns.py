import json
import os
class DataBase:
    """
    This class represent main datanase for per pears. Data stored as json object.
    Main data for our exists in the /db/data/mydb.json
    """
    def __init__(self) -> None:
        self.mydb:str = None
        self.db_path = "./src/db/data/mydb.json"
        if os.path.isfile(self.db_path):
            self.read_db()
        else:
            with open(self.db_path,"w") as fp:
                fp.write("")
        
    def update_db(self):
        with open(self.db_path,"w") as fp:
            fp.write(json.dumps(self.mydb))
        self.read_db()
        
    def read_db(self):
        if os.path.isfile(self.db_path):
            with open(self.db_path,"r") as fp:
                self.mydb =  json.load(fp)
        print(self.mydb)