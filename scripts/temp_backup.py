import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import os

# --- Configuration ---
LOCAL_DATABASE_URL = "postgresql://ayush:hackathon_secret@localhost/ayur_db"
OUTPUT_DIR = 'data/mappings'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'namaste_to_icd11_backup.csv')

# --- TEMPORARY DATABASE MODELS ---
# We define the models here to exactly match the OLD database schema,
# without the 'status' column. This avoids the error.
Base = declarative_base()

class NamasteTerm(Base):
    __tablename__ = "namaste_terms"
    id = Column(Integer, primary_key=True)
    code = Column(String)
    term = Column(String)
    system = Column(String)

class ConceptMap(Base):
    __tablename__ = "concept_map"
    id = Column(Integer, primary_key=True)
    namaste_id = Column(Integer, ForeignKey("namaste_terms.id"))
    icd_code = Column(String)
    map_relationship = Column(String)
    namaste_term = relationship("NamasteTerm")

def backup_map_data():
    """
    Extracts map data using a model that matches the current database state.
    """
    engine = create_engine(LOCAL_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    print("Querying database with temporary model for backup...")
    all_maps = db_session.query(ConceptMap).all()
    
    if not all_maps:
        print("No concept maps found. Nothing to back up.")
        db_session.close()
        return

    print(f"Found {len(all_maps)} maps. Preparing data for backup...")
    backup_data = []
    for mapping in all_maps:
        if mapping.namaste_term:
            backup_data.append({
                'namaste_code': mapping.namaste_term.code,
                'namaste_system': mapping.namaste_term.system,
                'icd_code': mapping.icd_code,
                'relationship': mapping.map_relationship,
            })

    df = pd.DataFrame(backup_data)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    
    print(f"✅ Successfully backed up {len(df)} records.")
    print(f"Backup file saved to: {OUTPUT_FILE}")
    db_session.close()

if __name__ == "__main__":
    backup_map_data()