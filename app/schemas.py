from pydantic import BaseModel

# Base schemas for the terminology terms
class IcdTerm(BaseModel):
    code: str
    term: str
    class Config: from_attributes = True

class NamasteTerm(BaseModel):
    id: int
    code: str
    term: str
    system: str
    class Config: from_attributes = True

class LoincTerm(BaseModel):
    code: str
    term: str
    class Config: from_attributes = True

# The rich response model for the mapping endpoint
class ConceptMapResponse(BaseModel):
    map_relationship: str
    source_term: NamasteTerm
    target_term: IcdTerm | None = None # Can be expanded later

    class Config:
        from_attributes = True