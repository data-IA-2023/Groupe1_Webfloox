from pydantic import BaseModel
import datetime

class uuercreate(BaseModel):
    username : str
    Email : str
    passzord : str