import pandas as pd
from sqlalchemy import create_engine
from app.models import LoincTerm  # Adjust import path if needed
from app.database import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ayush:hackathon_secret@localhost/ayur_db")

def ingest_loinc_data():
    """
    Reads the Loinc.csv file and ingests it into the loinc_terms table.
    """
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    loinc_csv_path = 'data/raw/Loinc.csv'
    print(f"Reading LOINC data from {loinc_csv_path}...")
    
    df = pd.read_csv(
        loinc_csv_path, 
        usecols=['LOINC_NUM', 'LONG_COMMON_NAME'],
        low_memory=False
    )
    df.rename(columns={'LOINC_NUM': 'code', 'LONG_COMMON_NAME': 'term'}, inplace=True)
    
    print(f"Found {len(df)} LOINC terms.")
    
    with engine.connect() as connection:
        print("Ingesting LOINC terms into the database...")
        # --- FIX ---
        connection.execute(LoincTerm.__table__.delete())
        df.to_sql(LoincTerm.__tablename__, connection, if_exists='append', index=False)
        connection.commit()
        # -----------
        print("LOINC data ingestion complete.")

if __name__ == "__main__":
    ingest_loinc_data()