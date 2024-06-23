from pydantic import BaseModel

class ConnectRequest(BaseModel):
    device: str
    password: str