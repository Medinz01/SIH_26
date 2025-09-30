import pandas as pd
from sqlalchemy import create_engine
from app.models import IcdTerm
from app.database import Base
import os
import re

# --- THE FIX: Environment-aware database connection ---
DB_HOST = "db" if os.getenv("APP_ENV") == "docker" else "localhost"
DATABASE_URL = f"postgresql://ayush:hackathon_secret@{DB_HOST}/ayur_db"
# --- END FIX ---

def clean_title(title):
    if isinstance(title, str):
        return re.sub(r'^[-\s]+', '', title)
    return title

def ingest_icd11_data():
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
        with connection.begin():
            print("Ingesting ICD-11 terms into the database...")
            connection.execute(IcdTerm.__table__.delete())
            df.to_sql(IcdTerm.__tablename__, connection, if_exists='append', index=False)
        print("✅ ICD-11 data ingestion complete.")

if __name__ == "__main__":
    ingest_icd11_data()
