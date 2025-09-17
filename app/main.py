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

# --- Security Setup (Simulating ABHA Token Check) ---
API_KEY_NAME = "X-API-Key"
# This is our mock ABHA token/API key. In a real system, this would be a JWT.
MOCK_ABHA_TOKEN = "abhatoken_for_sih_demo_25026"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(key: str = Security(api_key_header)):
    if key == MOCK_ABHA_TOKEN:
        return key
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate credentials"
        )

# --- API Routes ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/search", response_model=List[schemas.NamasteTerm])
def search_for_terms(term: str, db: Session = Depends(get_db)):
    return crud.search_terms(db=db, query=term)

@app.get("/fhir/condition/{term_id}")
def generate_fhir_condition(term_id: int, db: Session = Depends(get_db)):
    db_term = crud.get_term_by_id(db=db, term_id=term_id)
    if db_term is None:
        raise HTTPException(status_code=404, detail="Term not found")

    term_data = schemas.NamasteTerm.model_validate(db_term)
    fhir_resource = fhir_converter.create_fhir_condition(db=db, db_term=term_data) # Pass db here
    return fhir_resource.dict()

# --- NEW SECURE ENDPOINT ---
@app.post("/bundle")
def upload_encounter_bundle(
    bundle: Dict[str, Any], 
    api_key: str = Depends(get_api_key)
):
    """
    Ingests a FHIR Bundle. This endpoint is secured.
    """
    # This simulates our audit trail requirement.
    print("--- AUDIT LOG ---")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Authenticated Principal: User with token ending in ...{api_key[-4:]}")
    print(f"Action: Ingested FHIR Bundle of type '{bundle.get('type')}' with {len(bundle.get('entry', []))} entries.")
    print("-----------------")

    # In a real app, you'd save this bundle to a FHIR server or database.
    # For the hackathon, just acknowledging receipt is enough.
    return {"status": "success", "message": "Bundle received and logged."}


# --- Static Files Mount ---
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")