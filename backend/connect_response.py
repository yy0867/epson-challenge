from pydantic import BaseModel

class ConnectResponse(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    subject_id: str
    subject_type: str = ''
    token_type: str
