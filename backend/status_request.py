from pydantic import BaseModel


class StatusRequest(BaseModel):
    access_token: str
    subject_id: str
    job_id: str
