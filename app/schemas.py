from pydantic import BaseModel

class NamasteTerm(BaseModel):
    id: int
    code: str
    term: str

    class Config:
        from_attributes = True