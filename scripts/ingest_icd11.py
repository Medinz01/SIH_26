import pandas as pd
from sqlalchemy import create_engine
from app.models import IcdTerm
from app.database import Base
import os
import re

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ayush:hackathon_secret@localhost/ayur_db")

def clean_title(title):
    """
    Removes leading hyphens and spaces from the ICD-11 titles.
    """
    if isinstance(title, str):
        # This regex removes any number of hyphens and spaces at the start of the string
        return re.sub(r'^[-\s]+', '', title)
    return title

def ingest_icd11_data():
    """
    Reads the ICD-11 linearization CSV and ingests it into the icd_terms table.
    """
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    icd_csv_path = 'data/raw/icd11_data.csv'
    print(f"Reading ICD-11 data from {icd_csv_path}...")
    
    df = pd.read_csv(icd_csv_path, usecols=['Code', 'Title'])
    df.dropna(subset=['Code'], inplace=True)
    df['Title'] = df['Title'].apply(clean_title)
    df.rename(columns={'Code': 'code', 'Title': 'term'}, inplace=True)
    
    print(f"Found {len(df)} ICD-11 terms with codes.")
    
    with engine.connect() as connection:
        print("Ingesting ICD-11 terms into the database...")
        # --- FIX ---
        # Clear the table before inserting new data, but don't drop it
        connection.execute(IcdTerm.__table__.delete())
        df.to_sql(IcdTerm.__tablename__, connection, if_exists='append', index=False)
        connection.commit() # Add commit to save the changes
        # -----------
        print("ICD-11 data ingestion complete.")
if __name__ == "__main__":
    ingest_icd11_data()