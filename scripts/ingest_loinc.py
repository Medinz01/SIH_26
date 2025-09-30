import pandas as pd
from sqlalchemy import create_engine
from app.models import LoincTerm
from app.database import Base
import os

# --- THE FIX: Environment-aware database connection ---
DB_HOST = "db" if os.getenv("APP_ENV") == "docker" else "localhost"
DATABASE_URL = f"postgresql://ayush:hackathon_secret@{DB_HOST}/ayur_db"
# --- END FIX ---

def ingest_loinc_data():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    loinc_csv_path = 'data/raw/Loinc.csv'
    
    try:
        print(f"Reading LOINC data from {loinc_csv_path}...")
        df = pd.read_csv(
            loinc_csv_path, 
            usecols=['LOINC_NUM', 'LONG_COMMON_NAME'],
            low_memory=False,
            dtype={'LOINC_NUM': str}
        )
        df.rename(columns={'LOINC_NUM': 'code', 'LONG_COMMON_NAME': 'term'}, inplace=True)
        df['term'] = df['term'].astype(str).fillna('')
        df.dropna(subset=['code'], inplace=True)
        
        print(f"Found {len(df)} LOINC terms to process.")
        
        with engine.connect() as connection:
            with connection.begin():
                print("Ingesting LOINC terms into the database...")
                connection.execute(LoincTerm.__table__.delete())
                df.to_sql(LoincTerm.__tablename__, connection, if_exists='append', index=False)
            print("✅ LOINC data ingestion complete.")

    except FileNotFoundError:
        print(f"❌ ERROR: LOINC data file not found at '{loinc_csv_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    ingest_loinc_data()

