import pandas as pd
from sqlalchemy import create_engine
from app.models import NamasteTerm
from app.database import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ayush:hackathon_secret@localhost/ayur_db")

def ingest_namaste_data():
    """
    Reads the unified NAMASTE CSV and ingests it into the namaste_terms table.
    """
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    unified_csv_path = 'data/processed/unified_namaste_codes.csv'
    print(f"Reading unified NAMASTE data from {unified_csv_path}...")
    
    df = pd.read_csv(unified_csv_path)
    df.rename(columns={'namaste_code': 'code', 'namaste_term': 'term'}, inplace=True)
    
    print(f"Found {len(df)} NAMASTE terms.")
    
    with engine.connect() as connection:
        print("Ingesting NAMASTE terms into the database...")
        # Clear the table before inserting new data
        connection.execute(NamasteTerm.__table__.delete())
        df.to_sql(NamasteTerm.__tablename__, connection, if_exists='append', index=False)
        connection.commit()
        print("NAMASTE data ingestion complete.")

if __name__ == "__main__":
    ingest_namaste_data()