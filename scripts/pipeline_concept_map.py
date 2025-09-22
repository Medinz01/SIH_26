import requests
import sys
import time
import csv
import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine # Import create_engine
from app.database import engine # Keep this for the main app
from app.models import NamasteTerm, IcdTerm, ConceptMap

# --------------------------------------------------------------------------
# Client ID and Secret
# --------------------------------------------------------------------------
CLIENT_ID = "9753f1bd-4738-42c8-9081-963e1e8f8551_aa2b763e-6c0a-4d54-85e8-135fe144fcd0"
CLIENT_SECRET = "KmWdoiVii9wZhFPG7hF0AQyoh1Pnwco3MGzwmGf8hV0="

# --- Configuration ---
TOKEN_URL = 'https://icdaccessmanagement.who.int/connect/token'
API_BASE_URL = 'https://id.who.int/icd'
OUTPUT_CSV_FILE = 'data/mappings/namaste_to_icd11.csv'
# --- FIX: Add a local database URL ---
LOCAL_DATABASE_URL = "postgresql://ayush:hackathon_secret@localhost/ayur_db"


def get_access_token():
    """Authenticates with the server and retrieves an access token."""
    print("🔄 Requesting access token...")
    payload = {'grant_type': 'client_credentials', 'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'scope': 'icdapi_access'}
    try:
        response = requests.post(TOKEN_URL, data=payload, timeout=30)
        response.raise_for_status()
        print("✅ Access token received.")
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting access token: {e}")
        return None

def search_icd_code(term, headers):
    """Searches for a term in the ICD-11 MMS and returns the top result's code."""
    if not term or pd.isna(term): return None
    endpoint_url = f"{API_BASE_URL}/release/11/2025-01/mms/search"
    params = {'q': term}
    try:
        response = requests.get(endpoint_url, headers=headers, params=params, timeout=20)
        if response.status_code == 200:
            entities = response.json().get('destinationEntities', [])
            if entities:
                return entities[0].get('theCode', None)
    except requests.exceptions.RequestException as e:
        print(f"  - Network error for '{term}': {e}")
    return None

def build_map_csv(token, db_session):
    """
    Reads NAMASTE terms from the DB, calls the WHO API, and builds a CSV map file.
    """
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json', 'Accept-Language': 'en', 'API-Version': 'v2'}
    
    os.makedirs(os.path.dirname(OUTPUT_CSV_FILE), exist_ok=True)

    processed_keys = set()
    if os.path.exists(OUTPUT_CSV_FILE):
        print(f"✅ Output file '{OUTPUT_CSV_FILE}' found. Resuming from last point.")
        df_existing = pd.read_csv(OUTPUT_CSV_FILE)
        for _, row in df_existing.iterrows():
            processed_keys.add((row['namaste_code'], row['namaste_system']))
        print(f"   - Found {len(processed_keys)} previously processed maps.")
    
    try:
        with open(OUTPUT_CSV_FILE, 'a', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=['namaste_code', 'namaste_system', 'icd_code', 'relationship'])
            if not processed_keys:
                writer.writeheader()

            all_namaste_terms = db_session.query(NamasteTerm).all()
            terms_to_process = [t for t in all_namaste_terms if (t.code, t.system) not in processed_keys]
            
            total_terms = len(terms_to_process)
            print(f"Found {total_terms} new NAMASTE terms to process.")

            for i, term in enumerate(terms_to_process):
                print(f"Processing ({i+1}/{total_terms}): '{term.term}'")
                icd_code = search_icd_code(term.term, headers)
                if icd_code:
                    writer.writerow({
                        'namaste_code': term.code,
                        'namaste_system': term.system,
                        'icd_code': icd_code,
                        'relationship': 'equivalent'
                    })
                    print(f"  -> ✅ Found map: {term.code} -> {icd_code}")
                else:
                    print("  - ❌ No ICD-11 equivalent found via API.")
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n🛑 Ctrl+C detected. Progress saved to CSV. Exiting.")
        sys.exit(0)

def ingest_map_from_csv(db_session):
    """
    Reads the mapping CSV and populates the concept_map table.
    """
    if not os.path.exists(OUTPUT_CSV_FILE):
        print(f"❌ ERROR: Mapping file '{OUTPUT_CSV_FILE}' not found. Please run the script without flags first.")
        return

    print(f"Reading map data from {OUTPUT_CSV_FILE}...")
    map_df = pd.read_csv(OUTPUT_CSV_FILE)

    print("Clearing old concept map data...")
    db_session.query(ConceptMap).delete()

    new_maps = []
    print("Processing and preparing maps for ingestion...")
    for _, row in map_df.iterrows():
        namaste_term = db_session.query(NamasteTerm).filter_by(code=row['namaste_code'], system=row['namaste_system']).first()
        icd_term = db_session.query(IcdTerm).filter_by(code=row['icd_code']).first()

        if namaste_term and icd_term:
            new_maps.append({
                "namaste_id": namaste_term.id,
                "icd_code": icd_term.code,
                "map_relationship": row['relationship']
            })
    
    if new_maps:
        print(f"Ingesting {len(new_maps)} concept maps into the database...")
        db_session.bulk_insert_mappings(ConceptMap, new_maps)
        db_session.commit()
        print("✅ Concept map ingestion complete.")
    else:
        print("No valid maps found to ingest.")

def main():
    """Main pipeline controller."""
    # --- FIX: Use a local engine when running the script directly ---
    local_engine = create_engine(LOCAL_DATABASE_URL)
    Session = sessionmaker(bind=local_engine)
    db_session = Session()

    try:
        if '--ingest-only' in sys.argv:
            ingest_map_from_csv(db_session)
        elif '--build-only' in sys.argv:
            token = get_access_token()
            if token:
                build_map_csv(token, db_session)
        else:
            token = get_access_token()
            if token:
                build_map_csv(token, db_session)
                ingest_map_from_csv(db_session)
    finally:
        db_session.close()
    
    print("\n🎉 Pipeline finished.")

if __name__ == "__main__":
    main()
