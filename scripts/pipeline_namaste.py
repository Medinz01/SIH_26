import pandas as pd
import re
import os
from sqlalchemy import create_engine
from app.models import NamasteTerm
from app.database import Base

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ayush:hackathon_secret@localhost/ayur_db")
RAW_DATA_PATH = 'data/raw'

# --- 1. EXTRACTION & TRANSFORM (Logic from prepare_namaste_data.py) ---

def process_ayurveda(df):
    """
    Processes the raw Ayurveda CSV data.
    """
    df = df[['NAMC_CODE', 'NAMC_term_diacritical']].copy()
    df.rename(columns={'NAMC_CODE': 'namaste_code', 'NAMC_term_diacritical': 'namaste_term'}, inplace=True)
    
    new_rows = []
    for _, row in df.iterrows():
        code = row['namaste_code']
        term_string = str(row['namaste_term'])
        cleaned_terms = re.sub(r'\([a-z]\)\s*', '', term_string).strip()
        individual_terms = re.split(r'\s{2,}', cleaned_terms)
        
        for term in individual_terms:
            if term:
                new_rows.append({'namaste_code': code, 'namaste_term': term, 'system': 'ayurveda'})
        
        if len(individual_terms) > 1:
            combined_term = ' '.join(individual_terms)
            new_rows.append({'namaste_code': code, 'namaste_term': combined_term, 'system': 'ayurveda'})

    return pd.DataFrame(new_rows)

def process_siddha(df):
    """
    Processes the raw Siddha CSV data.
    """
    df = df[['NAMC_CODE', 'NAMC_TERM']].copy()
    df.rename(columns={'NAMC_CODE': 'namaste_code', 'NAMC_TERM': 'namaste_term'}, inplace=True)
    df['system'] = 'siddha'
    return df

def process_unani(df):
    """
    Processes the raw Unani CSV data.
    """
    df = df[['NUMC_CODE', 'NUMC_TERM']].copy()
    df.rename(columns={'NUMC_CODE': 'namaste_code', 'NUMC_TERM': 'namaste_term'}, inplace=True)
    df['system'] = 'unani'
    return df

# --- 2. LOAD (Logic from ingest_namaste.py) ---

def run_pipeline():
    """
    Runs the full ETL pipeline for all NAMASTE codes.
    """
    # --- PREPARE DATA ---
    print("Starting NAMASTE data preparation...")
    ayur_df = pd.read_csv(os.path.join(RAW_DATA_PATH, 'ayurveda.csv'))
    siddha_df = pd.read_csv(os.path.join(RAW_DATA_PATH, 'siddha.csv'))
    unani_df = pd.read_csv(os.path.join(RAW_DATA_PATH, 'unani.csv'))

    ayur_processed = process_ayurveda(ayur_df)
    siddha_processed = process_siddha(siddha_df)
    unani_processed = process_unani(unani_df)

    combined_df = pd.concat([ayur_processed, siddha_processed, unani_processed], ignore_index=True)
    combined_df.dropna(subset=['namaste_code', 'namaste_term'], inplace=True)
    combined_df = combined_df[combined_df['namaste_term'].str.strip() != '']
    
    # --- ADD THIS LINE ---
    # Remove any duplicate rows that the cleaning process might have created
    combined_df.drop_duplicates(inplace=True)
    # ---------------------
    
    print(f"Preparation complete. Found {len(combined_df)} unique NAMASTE terms.")

    # --- INGEST DATA ---
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    df_to_ingest = combined_df.rename(columns={'namaste_code': 'code', 'namaste_term': 'term'})
    
    with engine.connect() as connection:
        print("Ingesting NAMASTE terms into the database...")
        connection.execute(NamasteTerm.__table__.delete())
        df_to_ingest.to_sql(NamasteTerm.__tablename__, connection, if_exists='append', index=False)
        connection.commit()
        print("NAMASTE data ingestion complete.")

if __name__ == "__main__":
    run_pipeline()