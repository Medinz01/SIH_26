import csv
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Base, NamasteTerm, ConceptMap
from unidecode import unidecode

# The location of your final, enriched data file
DATA_FILE = 'data/enriched_namaste_codes_with_icd11.csv'

def format_term_for_search(term):
    """
    Converts a term to a simplified, searchable format.
    Example: 'vātasañcayaḥ' -> 'vatasancayah'
    """
    if not term:
        return ""
    return unidecode(term)

def reset_database():
    """Drops and recreates all tables. Use with caution!"""
    print("Resetting database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def ingest_unified_data():
    """
    Parses the enriched CSV and populates both the namaste_terms
    and concept_map tables, skipping duplicate codes.
    """
    db: Session = SessionLocal()
    processed_codes = set()  # Keep track of codes we've already added
    try:
        if db.query(NamasteTerm).count() > 0:
            print("Data has already been ingested. Skipping.")
            return

        print(f"Ingesting unified data from {DATA_FILE}...")
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                namaste_code = row.get('namaste_code')

                # --- FIX IS HERE ---
                # Skip this row if we've already processed this code
                if not namaste_code or namaste_code in processed_codes:
                    continue

                formatted_term = format_term_for_search(row['name'])

                # 1. Create and add the NAMASTE term
                db_term = NamasteTerm(
                    code=namaste_code,
                    term=formatted_term
                )
                db.add(db_term)
                processed_codes.add(namaste_code)  # Mark this code as processed
                
                # 2. If a mapping exists in the row, create and add it
                if row.get('icd11_code'):
                    db_map = ConceptMap(
                        namaste_code=namaste_code,
                        icd_code=row['icd11_code'],
                        icd_display=row['icd11_term']
                    )
                    db.add(db_map)
        
        db.commit()
        print("Unified data ingestion complete.")

    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
    ingest_unified_data()