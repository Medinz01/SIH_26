import requests
import sys

# --------------------------------------------------------------------------
# IMPORTANT: Replace these placeholders with your actual Client ID and Secret
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
CLIENT_ID = "9753f1bd-4738-42c8-9081-963e1e8f8551_aa2b763e-6c0a-4d54-85e8-135fe144fcd0"
CLIENT_SECRET = "KmWdoiVii9wZhFPG7hF0AQyoh1Pnwco3MGzwmGf8hV0="

# --- Configuration ---
TOKEN_URL = 'https://icdaccessmanagement.who.int/connect/token'
API_BASE_URL = 'https://id.who.int/icd'
SEARCH_TERM = 'vātasañcayaḥ'

def get_access_token():
    """Authenticates with the server and retrieves an access token."""
    if not CLIENT_ID or 'YOUR_CLIENT_ID' in CLIENT_ID:
        print("Error: Please replace 'YOUR_CLIENT_ID' and 'YOUR_CLIENT_SECRET'.")
        sys.exit(1)
        
    print("🔄 Requesting access token...")
    token_payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'icdapi_access'
    }
    try:
        response = requests.post(TOKEN_URL, data=token_payload, timeout=10)
        response.raise_for_status()
        print("✅ Access token received.")
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting access token: {e}")
        return None

def search_icd_term(token, term):
    """Searches for a term within a specific ICD-11 chapter."""
    if not token:
        return

    print(f"\n🔎 Searching for '{term}' in ICD-11 Chapter 26...")

    # --- Endpoint Details ---
    release_id = '2025-01'
    linearization = 'mms'
    endpoint_url = f"{API_BASE_URL}/release/11/{release_id}/{linearization}/search"

    # --- Required Headers ---
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Accept-Language': 'en',
        'API-Version': 'v2'
    }

    # --- Query Parameters ---
    params = {
        'q': term,
        'chapterFilter': '26' # Crucial for focusing the search on Traditional Medicine
    }

    try:
        response = requests.get(endpoint_url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        
        results = response.json()
        destination_entities = results.get('destinationEntities', [])

        if destination_entities:
            print("\n--- Result(s) Found ---")
            for entity in destination_entities:
                code = entity.get('theCode')
                title = entity.get('title')
                # The title is returned with highlighting tags, which we can remove
                clean_title = title.replace('<em class="found">', '').replace('</em>', '')
                print(f"   ✅ Term: '{clean_title}'")
                print(f"      ICD-11 Code: {code}")
            print("-----------------------\n")
        else:
            print(f"\n❌ No ICD-11 equivalent found for the term '{term}' in Chapter 26.")

    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred during the search: {e}")

if __name__ == "__main__":
    access_token = get_access_token()
    search_icd_term(access_token, SEARCH_TERM)