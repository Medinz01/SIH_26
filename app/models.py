from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NamasteTerm(Base):
    __tablename__ = "namaste_terms"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    term = Column(String)
    # We can add the 'system' column later if needed, keeping it simple for now.

class ConceptMap(Base):
    __tablename__ = "concept_map"

    id = Column(Integer, primary_key=True, index=True)
    namaste_code = Column(String, index=True)
    icd_code = Column(String)
    icd_display = Column(String)
    relationship = Column(String, default='equivalent')