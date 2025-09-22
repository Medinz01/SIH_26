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

class ConceptMapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int # Add ID to identify the map
    status: str # Add status
    map_relationship: str
    source_term: NamasteTerm
    target_term: IcdTerm | None = None

# Add this new schema to app/schemas.py
class MapUpdate(BaseModel):
    map_relationship: str
    status: str