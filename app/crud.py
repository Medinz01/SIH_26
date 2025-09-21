from sqlalchemy.orm import Session, joinedload
from . import models

def search_namaste_terms(db: Session, query: str):
    """
    Searches for NAMASTE terms containing the query string (case-insensitive).
    """
    return db.query(models.NamasteTerm).filter(models.NamasteTerm.term.ilike(f"%{query}%")).all()

def search_icd_terms(db: Session, query: str):
    """
    Searches for ICD-11 terms containing the query string (case-insensitive).
    """
    return db.query(models.IcdTerm).filter(models.IcdTerm.term.ilike(f"%{query}%")).all()

def search_loinc_terms(db: Session, query: str):
    """
    Searches for LOINC terms containing the query string (case-insensitive).
    """
    return db.query(models.LoincTerm).filter(models.LoincTerm.term.ilike(f"%{query}%")).all()


def get_mapping_for_namaste_code(db: Session, namaste_code: str):
    """
    Searches for a concept map for a given NAMASTE code and eagerly
    loads the related LOINC and SNOMED terms to avoid extra DB queries.
    """
    return (
        db.query(models.ConceptMap)
        .options(
            joinedload(models.ConceptMap.loinc_term),
            joinedload(models.ConceptMap.icd_term) # Added for future use
        )
        .filter(models.ConceptMap.namaste_code == namaste_code)
        .first()
    )

def get_term_by_id(db: Session, term_id: int):
    return db.query(models.NamasteTerm).filter(models.NamasteTerm.id == term_id).first()