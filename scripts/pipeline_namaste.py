import pandas as pd
import re
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import NamasteTerm
from app.database import Base

# --- Configuration ---
LOCAL_DATABASE_URL = "postgresql://ayush:hackathon_secret@localhost/ayur_db"
RAW_DATA_PATH = 'data/raw'

# --- 1. EXTRACTION & TRANSFORM ---

def clean_namaste_code(code):
    """
    Cleans the NAMASTE code by intelligently extracting the primary identifier.
    The logic prefers the part (inside or outside parentheses) that contains a hyphen.
    """
    if not isinstance(code, str):
        return code

    if '(' in code and ')' in code:
        outside_part = code.split('(')[0].strip()
        match = re.search(r'\((.*?)\)', code)
        inside_part = match.group(1).strip() if match else ''

        # ** Your Intelligent Heuristic **
        if '-' in inside_part:
            return inside_part
        else:
            return outside_part
    else:
        return code.strip()

def process_ayurveda(df):
    """
    Processes the raw Ayurveda CSV data using the intelligent cleaning function.
    """
    df = df[['NAMC_CODE', 'NAMC_term_diacritical']].copy()
    df.rename(columns={'NAMC_CODE': 'code', 'NAMC_term_diacritical': 'term'}, inplace=True)
    df['system'] = 'ayurveda'
    
    df['code'] = df['code'].apply(clean_namaste_code)
    
    new_rows = []
    for _, row in df.iterrows():
        code = row['code']
        term_string = str(row['term'])
        cleaned_terms = re.sub(r'\([a-z]\)\s*', '', term_string).strip()
        individual_terms = re.split(r'\s{2,}', cleaned_terms)
        
        for term in individual_terms:
            if term and term.lower() != 'nan':
                new_rows.append({'code': code, 'term': term, 'system': 'ayurveda'})
        
        if len(individual_terms) > 1:
            combined_term = ' '.join(individual_terms)
            new_rows.append({'code': code, 'term': combined_term, 'system': 'ayurveda'})

    return pd.DataFrame(new_rows)

def process_siddha(df):
    """Processes the raw Siddha CSV data."""
    df = df[['NAMC_CODE', 'NAMC_TERM']].copy()
    df.rename(columns={'NAMC_CODE': 'code', 'NAMC_TERM': 'term'}, inplace=True)
    df['system'] = 'siddha'
    df['code'] = df['code'].apply(clean_namaste_code)
    return df

def process_unani(df):
    """Processes the raw Unani CSV data."""
    df = df[['NUMC_CODE', 'NUMC_TERM']].copy()
    df.rename(columns={'NUMC_CODE': 'code', 'NUMC_TERM': 'term'}, inplace=True)
    df['system'] = 'unani'
    df['code'] = df['code'].apply(clean_namaste_code)
    return df

# --- 2. LOAD ---

def run_pipeline():
    """Runs the full ETL pipeline for all NAMASTE codes."""
    engine = create_engine(LOCAL_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    try:
        print("Starting NAMASTE data preparation with intelligent parsing...")
        ayur_df = pd.read_csv(os.path.join(RAW_DATA_PATH, 'ayurveda.csv'))
        siddha_df = pd.read_csv(os.path.join(RAW_DATA_PATH, 'siddha.csv'))
        unani_df = pd.read_csv(os.path.join(RAW_DATA_PATH, 'unani.csv'))

        ayur_processed = process_ayurveda(ayur_df)
        siddha_processed = process_siddha(siddha_df)
        unani_processed = process_unani(unani_df)

        combined_df = pd.concat([ayur_processed, siddha_processed, unani_processed], ignore_index=True)
        combined_df.dropna(subset=['code', 'term'], inplace=True)
        combined_df = combined_df[combined_df['term'].str.strip() != '']
        combined_df.drop_duplicates(inplace=True)
        
        print(f"Preparation complete. Found {len(combined_df)} unique NAMASTE terms.")

        with engine.connect() as connection:
            with connection.begin(): # Start a transaction
                print("Ingesting NAMASTE terms into the database...")
                connection.execute(NamasteTerm.__table__.delete())
                combined_df.to_sql(NamasteTerm.__tablename__, connection, if_exists='append', index=False)
            print("✅ NAMASTE terms ingestion complete.")
            
    except Exception as e:
        print(f"An error occurred during the pipeline: {e}")
    
    print("\n🎉 NAMASTE Pipeline finished.")

if __name__ == "__main__":
    run_pipeline()