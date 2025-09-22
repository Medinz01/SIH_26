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

def get_reverse_map_for_icd_code(db: Session, icd_code: str):
    """
    Finds all NAMASTE terms that are mapped to a given ICD-11 code.
    """
    # Find all map entries for the given icd_code
    mappings = db.query(models.ConceptMap).filter(models.ConceptMap.icd_code == icd_code).all()
    
    # Extract the namaste_id from each mapping
    namaste_ids = [mapping.namaste_id for mapping in mappings]
    
    if not namaste_ids:
        return []
        
    # Return all NamasteTerm objects whose IDs were in the map
    return db.query(models.NamasteTerm).filter(models.NamasteTerm.id.in_(namaste_ids)).all()

# Add these new functions to app/crud.py

def get_unreviewed_maps(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of all concept maps that have not yet been reviewed.
    """
    return (
        db.query(models.ConceptMap)
        .options(
            joinedload(models.ConceptMap.namaste_term),
            joinedload(models.ConceptMap.icd_term)
        )
        .filter(models.ConceptMap.status == 'auto_generated')
        .offset(skip)
        .limit(limit)
        .all()
    )

# In app/crud.py
def update_map(db: Session, map_id: int, relationship: str, status: str):
    """
    Updates the relationship and status of a specific concept map.
    """
    db_map = (
        db.query(models.ConceptMap)
        .options(
            joinedload(models.ConceptMap.namaste_term),
            joinedload(models.ConceptMap.icd_term)
        )
        .filter(models.ConceptMap.id == map_id)
        .first()
    )
    if db_map:
        db_map.map_relationship = relationship
        db_map.status = status
        db.commit()
        db.refresh(db_map)
    return db_map

def delete_map(db: Session, map_id: int):
    """
    Deletes a concept map from the database.
    """
    db_map = db.query(models.ConceptMap).filter(models.ConceptMap.id == map_id).first()
    if db_map:
        db.delete(db_map)
        db.commit()
    return db_map

# Add this new function to app/crud.py
def get_maps_by_status(db: Session, status: str, skip: int = 0, limit: int = 20):
    """
    Retrieves a list of concept maps filtered by their review status.
    """
    return (
        db.query(models.ConceptMap)
        .options(
            joinedload(models.ConceptMap.namaste_term),
            joinedload(models.ConceptMap.icd_term)
        )
        .filter(models.ConceptMap.status == status)
        .order_by(models.ConceptMap.id) # Add consistent ordering
        .offset(skip)
        .limit(limit)
        .all()
    )