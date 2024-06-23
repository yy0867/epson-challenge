from pydantic import BaseModel

class RegisterInformationRequest(BaseModel):
    header_left: str
    header_center: str
    contact: str
    footer: str
    teacher: str