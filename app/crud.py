from sqlalchemy.orm import Session, joinedload
from . import models

# --- Terminology Search Functions (Unchanged) ---

def search_namaste_terms(db: Session, query: str):
    return db.query(models.NamasteTerm).filter(models.NamasteTerm.term.ilike(f"%{query}%")).all()

def search_icd_terms(db: Session, query: str):
    return db.query(models.IcdTerm).filter(models.IcdTerm.term.ilike(f"%{query}%")).all()

def search_loinc_terms(db: Session, query: str):
    return db.query(models.LoincTerm).filter(models.LoincTerm.term.ilike(f"%{query}%")).all()

def search_snomed_terms(db: Session, query: str):
    return db.query(models.SnomedTerm).filter(models.SnomedTerm.term.ilike(f"%{query}%")).all()

# --- Mapping Functions (Unchanged) ---

def get_mapping_for_namaste_code(db: Session, namaste_code: str, namaste_system: str):
    namaste_term = db.query(models.NamasteTerm).filter(
        models.NamasteTerm.code == namaste_code,
        models.NamasteTerm.system == namaste_system
    ).first()
    if not namaste_term: return None
    return db.query(models.ConceptMap).options(
        joinedload(models.ConceptMap.namaste_term),
        joinedload(models.ConceptMap.icd_term)
    ).filter(models.ConceptMap.namaste_id == namaste_term.id).first()

def get_reverse_map_for_icd_code(db: Session, icd_code: str):
    mappings = db.query(models.ConceptMap).filter(models.ConceptMap.icd_code == icd_code).all()
    namaste_ids = [mapping.namaste_id for mapping in mappings]
    if not namaste_ids: return []
    return db.query(models.NamasteTerm).filter(models.NamasteTerm.id.in_(namaste_ids)).all()

def get_term_by_id(db: Session, term_id: int):
    return db.query(models.NamasteTerm).filter(models.NamasteTerm.id == term_id).first()

# --- UPGRADED Curation Functions ---

def get_maps_by_status(db: Session, status: str, search: str | None = None, skip: int = 0, limit: int = 10):
    """
    Retrieves a paginated list of concept maps, filtered by status and an optional search query.
    """
    query = (
        db.query(models.ConceptMap)
        .options(
            joinedload(models.ConceptMap.namaste_term),
            joinedload(models.ConceptMap.icd_term)
        )
        .filter(models.ConceptMap.status == status)
    )

    if search:
        query = query.join(models.NamasteTerm).filter(
            models.NamasteTerm.term.ilike(f"%{search}%")
        )
    
    return query.order_by(models.ConceptMap.id).offset(skip).limit(limit).all()

def get_maps_count_by_status(db: Session, status: str, search: str | None = None):
    """
    Gets the total count of concept maps for a given status and optional search query.
    """
    query = db.query(models.ConceptMap).filter(models.ConceptMap.status == status)
    
    if search:
        query = query.join(models.NamasteTerm).filter(
            models.NamasteTerm.term.ilike(f"%{search}%")
        )
        
    return query.count()


def update_map(db: Session, map_id: int, relationship: str, status: str):
    db_map = db.query(models.ConceptMap).filter(models.ConceptMap.id == map_id).first()
    if db_map:
        db_map.map_relationship = relationship
        db_map.status = status
        db.commit()
        db.refresh(db_map)
    return db_map

def delete_map(db: Session, map_id: int):
    db_map = db.query(models.ConceptMap).filter(models.ConceptMap.id == map_id).first()
    if db_map:
        db.delete(db_map)
        db.commit()
    return db_map

def get_term_by_system_and_code(db: Session, system: str, code: str):
    """
    Finds a single term in the database by its system and code.
    """
    if system.startswith("namaste"):
        system_name = system.split('_')[-1]
        return db.query(models.NamasteTerm).filter_by(system=system_name, code=code).first()
    elif system == "icd11":
        return db.query(models.IcdTerm).filter_by(code=code).first()
    elif system == "loinc":
        return db.query(models.LoincTerm).filter_by(code=code).first()
    return None