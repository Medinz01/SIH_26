from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from .database import Base

class IcdTerm(Base):
    __tablename__ = "icd_terms"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    term = Column(String)

# FINAL CORRECTED VERSION of NamasteTerm
class NamasteTerm(Base):
    __tablename__ = "namaste_terms"

    # Revert to a simple integer primary key, which is always unique.
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, index=True) # Index for fast lookups
    term = Column(String)
    system = Column(String, index=True) # Index for fast lookups


class SnomedTerm(Base):
    __tablename__ = "snomed_terms"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    term = Column(String)

class LoincTerm(Base):
    __tablename__ = "loinc_terms"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    term = Column(String)


# FINAL CORRECTED VERSION of ConceptMap
class ConceptMap(Base):
    __tablename__ = "concept_map"

    id = Column(Integer, primary_key=True, index=True)
    
    # The ForeignKey now points to the simple 'id' of the NamasteTerm
    namaste_id = Column(Integer, ForeignKey("namaste_terms.id"), index=True)
    
    # Mappings to other code systems
    icd_code = Column(String, ForeignKey("icd_terms.code"), nullable=True)
    snomed_code = Column(String, ForeignKey("snomed_terms.code"), nullable=True)
    loinc_code = Column(String, ForeignKey("loinc_terms.code"), nullable=True)
    
    map_relationship = Column(String, default='equivalent')

    # Relationships for easier data access
    namaste_term = relationship("NamasteTerm")
    icd_term = relationship("IcdTerm")
    snomed_term = relationship("SnomedTerm")
    loinc_term = relationship("LoincTerm")