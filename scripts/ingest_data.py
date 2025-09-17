import csv
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Base, NamasteTerm, ConceptMap

# The location of your final, enriched data file
DATA_FILE = 'data/enriched_namaste_codes_with_icd11.csv'

def reset_database():
    """Drops and recreates all tables. Use with caution!"""
    print("Resetting database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def ingest_unified_data():
    """
    Parses the enriched CSV and populates both the namaste_terms
    and concept_map tables.
    """
    db: Session = SessionLocal()
    try:
        if db.query(NamasteTerm).count() > 0:
            print("Data has already been ingested. Skipping.")
            return

        print(f"Ingesting unified data from {DATA_FILE}...")
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 1. Create and add the NAMASTE term
                # --- FIX IS HERE ---
                db_term = NamasteTerm(
                    code=row['namaste_code'],
                    term=row['name']  # Changed 'namaste_display' to 'name'
                )
                db.add(db_term)
                
                # 2. If a mapping exists in the row, create and add it
                if row.get('icd11_code'):
                    # --- FIX IS HERE ---
                    db_map = ConceptMap(
                        namaste_code=row['namaste_code'],
                        icd_code=row['icd11_code'],
                        icd_display=row['icd11_term'] # Changed 'icd11_display' to 'icd11_term'
                    )
                    db.add(db_map)
        
        db.commit()
        print("Unified data ingestion complete.")

    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
    ingest_unified_data()