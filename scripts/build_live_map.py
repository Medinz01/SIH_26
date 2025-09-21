import requests
import sys
import time
import pandas as pd
# Removed unused import: unicodedata

from sqlalchemy.orm import sessionmaker
from app.database import engine 
# Assuming your models are defined in app.models
from app.models import NamasteTerm, IcdTerm, ConceptMap

# --------------------------------------------------------------------------
# IMPORTANT: These are your actual credentials.
# --------------------------------------------------------------------------
CLIENT_ID = "9753f1bd-4738-42c8-9081-963e1e8f8551_aa2b763e-6c0a-4d54-85e8-135fe144fcd0"
CLIENT_SECRET = "KmWdoiVii9wZhFPG7hF0AQyoh1Pnwco3MGzwmGf8hV0="

# --- Configuration ---
TOKEN_URL = 'https://icdaccessmanagement.who.int/connect/token'
API_BASE_URL = 'https://id.who.int/icd'

# --- REMOVED: The normalize_term function is no longer needed ---

def get_access_token():
    """Authenticates with the server and retrieves an access token."""
    print("🔄 Requesting access token...")
    payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'icdapi_access'
    }
    try:
        response = requests.post(TOKEN_URL, data=payload, timeout=30)
        response.raise_for_status()
        print("✅ Access token received.")
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting access token: {e}")
        return None

# --- REPLACED: Using the more robust search function from your first script ---
def search_icd_term_with_retry(term, headers):
    """
    Searches for a term within Chapter 26 with automatic retries.
    Returns a dictionary with 'icd11_term' and 'icd11_code'.
    """
    if not term or pd.isna(term):
        return {'icd11_term': '', 'icd11_code': ''}

    endpoint_url = f"{API_BASE_URL}/release/11/2025-01/mms/search"
    # --- CRITICAL FIX: Added the chapterFilter parameter ---
    params = {'q': term, 'chapterFilter': '26'}
    
    max_retries = 5
    base_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            # Increased timeouts for robustness
            response = requests.get(endpoint_url, headers=headers, params=params, timeout=(15, 30))
            
            if response.status_code != 200:
                print(f"   - API returned status {response.status_code} for '{term}'. Skipping.")
                return {'icd11_term': '', 'icd11_code': ''}

            results = response.json()
            entities = results.get('destinationEntities', [])
            if entities:
                top_result = entities[0]
                code = top_result.get('theCode', '')
                title = top_result.get('title', '')
                clean_title = title.replace('<em class="found">', '').replace('</em>', '')
                return {'icd11_term': clean_title, 'icd11_code': code}
            else:
                # Success, but no match found
                return {'icd11_term': '', 'icd11_code': ''}

        except requests.exceptions.RequestException as e:
            print(f"   - Network error for '{term}': {type(e).__name__}. Attempt {attempt + 1} of {max_retries}.")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"     Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"   - Max retries reached for '{term}'. Skipping.")
                return {'icd11_term': '', 'icd11_code': ''}
    
    return {'icd11_term': '', 'icd11_code': ''} # Fallback

def main():
    """Main function to fetch NAMASTE terms and build the concept map."""
    token = get_access_token()
    if not token:
        sys.exit(1)

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Accept-Language': 'en',
        'API-Version': 'v2'
    }

    Session = sessionmaker(bind=engine)
    db_session = Session()

    try:
        processed_namaste_ids = {result[0] for result in db_session.query(ConceptMap.namaste_id).all()}
        print(f"✅ Found {len(processed_namaste_ids)} previously processed maps. Resuming...")

        terms_to_process = db_session.query(NamasteTerm).filter(
            NamasteTerm.id.notin_(processed_namaste_ids)
        ).all()
        
        total_terms = len(terms_to_process)
        print(f"Found {total_terms} new NAMASTE terms to process.")

        for i, namaste_term in enumerate(terms_to_process):
            original_term = namaste_term.term
            print(f"Processing ({i+1}/{total_terms}): '{original_term}' ({namaste_term.code}, {namaste_term.system})")
            
            # --- MODIFIED: Simplified search logic ---
            # Only search with the original term.
            icd_data = search_icd_term_with_retry(original_term, headers)
            icd_code = icd_data.get('icd11_code')
            
            if icd_code:
                # IMPORTANT: This check is still here. Ensure your 'icd_terms' table is populated.
                icd_term_exists = db_session.query(IcdTerm).filter_by(code=icd_code).first()
                if icd_term_exists:
                    new_map = ConceptMap(
                        namaste_id=namaste_term.id,
                        icd_code=icd_code,
                        map_relationship='equivalent' # Or another appropriate relationship
                    )
                    db_session.add(new_map)
                    print(f"   -> ✅ Found map: {namaste_term.code} -> {icd_code}")
                else:
                    print(f"   - ⚠️ WARN: API found ICD code '{icd_code}', but it's not in your local DB. Skipping map creation.")
            else:
                print("   - ❌ No ICD-11 equivalent found via API.")

            # Commit in batches to save progress
            if (i + 1) % 50 == 0:
                print("...committing batch to database...")
                db_session.commit()
            
            time.sleep(0.2) # A slightly longer sleep to be kinder to the API

        db_session.commit() # Commit any remaining changes

    except KeyboardInterrupt:
        print("\n\n🛑 Ctrl+C detected. Committing progress and exiting gracefully.")
        db_session.commit()
        sys.exit(0)
    finally:
        db_session.close()
    
    print("\n🎉 Mapping process complete.")

if __name__ == "__main__":
    # Make sure you have your database and models set up correctly
    # For example:
    # from app.database import init_db
    # init_db()
    main()

