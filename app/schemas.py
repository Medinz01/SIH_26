from pydantic import BaseModel, ConfigDict

# Base schemas for the terminology terms
class IcdTerm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    code: str
    term: str

class NamasteTerm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    code: str
    term: str
    system: str

class LoincTerm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    code: str
    term: str

# The rich response model for the mapping endpoint
class ConceptMapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    map_relationship: str
    source_term: NamasteTerm
    target_term: IcdTerm | None = None