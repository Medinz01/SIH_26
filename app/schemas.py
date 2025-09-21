from pydantic import BaseModel

class IcdTerm(BaseModel):
    id: int
    code: str
    term: str

    class Config:
        from_attributes = True

class NamasteTerm(BaseModel):
    id: int
    code: str
    term: str

    class Config:
        from_attributes = True

class LoincTerm(BaseModel):
    code: str
    term: str

    class Config:
        from_attributes = True

class ConceptMap(BaseModel):
    namaste_code: str
    icd_code: str | None = None
    icd_display: str | None = None
    snomed_code: str | None = None
    # Change loinc_code to be the full term object
    loinc_term: LoincTerm | None = None 
    map_relationship: str # Use the corrected column name

    class Config:
        from_attributes = True
