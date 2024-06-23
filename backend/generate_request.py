from pydantic import BaseModel

class GenerateRequest(BaseModel):
    input: str