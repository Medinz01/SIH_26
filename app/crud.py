from sqlalchemy.orm import Session
from . import models

def search_terms(db: Session, query: str):
    """
    Searches for NAMASTE terms containing the query string (case-insensitive).
    """
    return db.query(models.NamasteTerm).filter(models.NamasteTerm.term.ilike(f"%{query}%")).all()

    # Add this function to app/crud.py
def get_term_by_id(db: Session, term_id: int):
    return db.query(models.NamasteTerm).filter(models.NamasteTerm.id == term_id).first()

# Add this function to app/crud.py
def get_mapping_for_namaste_code(db: Session, namaste_code: str):
    return db.query(models.ConceptMap).filter(models.ConceptMap.namaste_code == namaste_code).first()