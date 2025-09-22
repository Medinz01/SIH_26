from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from . import crud, models, schemas, fhir_converter
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AyurFHIR Bridge")

# --- Security Setup ---
API_KEY_NAME = "X-API-Key"
MOCK_ABHA_TOKEN = "abhatoken_for_sih_demo_25026"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(key: str = Security(api_key_header)):
    if key == MOCK_ABHA_TOKEN:
        return key
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate credentials"
        )

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Routes ---

@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- Terminology Search Endpoints ---

@app.get("/search/namaste", response_model=List[schemas.NamasteTerm])
def search_for_namaste_terms(term: str, db: Session = Depends(get_db)):
    """Search for NAMASTE terms across Ayurveda, Siddha, and Unani systems."""
    return crud.search_namaste_terms(db=db, query=term)

@app.get("/search/icd11", response_model=List[schemas.IcdTerm])
def search_for_icd_terms(term: str, db: Session = Depends(get_db)):
    """Search for ICD-11 terms."""
    return crud.search_icd_terms(db=db, query=term)

@app.get("/search/loinc", response_model=List[schemas.LoincTerm])
def search_for_loinc_terms(term: str, db: Session = Depends(get_db)):
    """Search for LOINC terms."""
    return crud.search_loinc_terms(db=db, query=term)


# --- Mapping Endpoint ---

@app.get("/map", response_model=schemas.ConceptMapResponse)
def get_mapping(namaste_code: str, namaste_system: str, db: Session = Depends(get_db)):
    """
    Retrieves the ICD-11 mapping for a specific NAMASTE code and system.
    """
    mapping = crud.get_mapping_for_namaste_code(
        db=db, 
        namaste_code=namaste_code, 
        namaste_system=namaste_system
    )
    
    if mapping is None:
        raise HTTPException(
            status_code=404, 
            detail=f"No mapping found for NAMASTE code '{namaste_code}' in system '{namaste_system}'"
        )
    
    # We need to rename the DB model fields to match the Pydantic schema
    response_data = {
        "map_relationship": mapping.map_relationship,
        "source_term": mapping.namaste_term,
        "target_term": mapping.icd_term
    }
    return response_data

@app.get("/map/reverse", response_model=List[schemas.NamasteTerm])
def get_reverse_mapping(icd_code: str, db: Session = Depends(get_db)):
    """
    Performs a reverse lookup, finding all NAMASTE terms mapped 
    to a given ICD-11 code.
    """
    namaste_terms = crud.get_reverse_map_for_icd_code(db=db, icd_code=icd_code)
    
    if not namaste_terms:
        raise HTTPException(
            status_code=404, 
            detail=f"No NAMASTE terms found mapped to ICD-11 code: {icd_code}"
        )
        
    return namaste_terms

# --- Curation Endpoints ---

# In app/main.py

@app.get("/maps/unreviewed", response_model=List[schemas.ConceptMapResponse])
def get_unreviewed_maps_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of all automatically generated maps that need human review.
    """
    maps_from_db = crud.get_unreviewed_maps(db, skip=skip, limit=limit)
    
    # --- THE FIX ---
    # Manually transform each database object into the Pydantic response shape
    response = []
    for mapping in maps_from_db:
        response.append({
            "id": mapping.id,
            "status": mapping.status,
            "map_relationship": mapping.map_relationship,
            "source_term": mapping.namaste_term,
            "target_term": mapping.icd_term
        })
    # --- END FIX ---
        
    return response

# In app/main.py
@app.put("/maps/{map_id}", response_model=schemas.ConceptMapResponse)
def update_map_endpoint(map_id: int, map_update: schemas.MapUpdate, db: Session = Depends(get_db)):
    """
    Approve or update a concept map.
    """
    updated_map = crud.update_map(
        db, 
        map_id=map_id, 
        relationship=map_update.map_relationship, 
        status=map_update.status
    )
    if updated_map is None:
        raise HTTPException(status_code=404, detail="Map not found")
    
    # --- THE FIX ---
    # Manually transform the DB object to match the Pydantic response schema
    response_data = {
        "id": updated_map.id,
        "status": updated_map.status,
        "map_relationship": updated_map.map_relationship,
        "source_term": updated_map.namaste_term,
        "target_term": updated_map.icd_term
    }
    return response_data
    # --- END FIX ---

@app.delete("/maps/{map_id}")
def delete_map_endpoint(map_id: int, db: Session = Depends(get_db)):
    """
    Reject (delete) an incorrect concept map.
    """
    deleted_map = crud.delete_map(db, map_id=map_id)
    if deleted_map is None:
        raise HTTPException(status_code=404, detail="Map not found")
    return {"status": "success", "message": "Map deleted"}

# Add this to the Curation Endpoints section in app/main.py
@app.get("/maps/by_status", response_model=List[schemas.ConceptMapResponse])
def get_maps_by_status_endpoint(status: str = 'reviewed', skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Get a list of maps filtered by status (e.g., 'reviewed', 'auto_generated').
    """
    maps_from_db = crud.get_maps_by_status(db, status=status, skip=skip, limit=limit)
    
    response = []
    for mapping in maps_from_db:
        response.append({
            "id": mapping.id,
            "status": mapping.status,
            "map_relationship": mapping.map_relationship,
            "source_term": mapping.namaste_term,
            "target_term": mapping.icd_term
        })
    return response
# --- FHIR and Secure Endpoints ---

@app.get("/fhir/condition/{term_id}")
def generate_fhir_condition(term_id: int, db: Session = Depends(get_db)):
    db_term = crud.get_term_by_id(db=db, term_id=term_id)
    if db_term is None:
        raise HTTPException(status_code=404, detail="Term not found")

    term_data = schemas.NamasteTerm.model_validate(db_term)
    fhir_resource = fhir_converter.create_fhir_condition(db=db, db_term=term_data)
    return fhir_resource.dict()

@app.post("/bundle")
def upload_encounter_bundle(
    bundle: Dict[str, Any], 
    api_key: str = Depends(get_api_key)
):
    print(f"--- AUDIT LOG ---")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Authenticated Principal: User with token ending in ...{api_key[-4:]}")
    print(f"Action: Ingested FHIR Bundle of type '{bundle.get('type')}' with {len(bundle.get('entry', []))} entries.")
    print("-----------------")
    return {"status": "success", "message": "Bundle received and logged."}

# --- Static Files Mount ---
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")