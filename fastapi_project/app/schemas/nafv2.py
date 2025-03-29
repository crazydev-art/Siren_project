from pydantic import BaseModel

class NafV2Schema(BaseModel):
    codenaf: str
    nafvfinale: str | None = None  

    class Config:
        orm_mode = True
