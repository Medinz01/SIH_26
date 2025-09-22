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


def get_mapping_for_namaste_code(db: Session, namaste_code: str, namaste_system: str):
    """
    Finds a NAMASTE term by its code and system, then retrieves its
    concept map, including the full related ICD-11 term.
    """
    # First, find the specific NAMASTE term
    namaste_term = db.query(models.NamasteTerm).filter(
        models.NamasteTerm.code == namaste_code,
        models.NamasteTerm.system == namaste_system
    ).first()

    if not namaste_term:
        return None

    # Now, find the map associated with that term's ID
    return (
        db.query(models.ConceptMap)
        .options(
            joinedload(models.ConceptMap.namaste_term),
            joinedload(models.ConceptMap.icd_term)
        )
        .filter(models.ConceptMap.namaste_id == namaste_term.id)
        .first()
    )

def get_term_by_id(db: Session, term_id: int):
    return db.query(models.NamasteTerm).filter(models.NamasteTerm.id == term_id).first()