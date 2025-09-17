import requests
import sys

# --------------------------------------------------------------------------
# IMPORTANT: Replace these placeholders with your actual Client ID and Secret
# You can get these from https://icd.who.int/icdapi after registering.
# --------------------------------------------------------------------------
CLIENT_ID = "9753f1bd-4738-42c8-9081-963e1e8f8551_aa2b763e-6c0a-4d54-85e8-135fe144fcd0"
CLIENT_SECRET = "KmWdoiVii9wZhFPG7hF0AQyoh1Pnwco3MGzwmGf8hV0="

# --- Configuration ---
TOKEN_URL = 'https://icdaccessmanagement.who.int/connect/token'
API_BASE_URL = 'https://id.who.int/icd'
SEARCH_TERM = 'Cholera'

def get_access_token():
    """Authenticates with the server and retrieves an access token."""
    if not CLIENT_ID or 'YOUR_CLIENT_ID' in CLIENT_ID:
        print("Error: Please replace 'YOUR_CLIENT_ID' and 'YOUR_CLIENT_SECRET' with your credentials.")
        sys.exit(1)
        
    print("🔄 Requesting access token...")
    
    # Prepare the token request
    token_payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'icdapi_access'
    }
    
    try:
        # Make the POST request to the token endpoint
        response = requests.post(TOKEN_URL, data=token_payload, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # Extract and return the token
        access_token = response.json().get('access_token')
        print("✅ Access token received successfully.")
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting access token: {e}")
        if 'response' in locals() and response.text:
            print(f"   Server response: {response.text}")
        return None

def fetch_icd_code(token, search_text):
    """Fetches the ICD-11 code for a given search term."""
    if not token:
        return
        
    print(f"🔎 Searching for ICD-11 code for '{search_text}'...")
    
    # --- Endpoint Details ---
    # We use the 'mms' (Mortality and Morbidity Statistics) linearization,
    # which is the standard for statistical coding.
    # We use a recent release ID, e.g., '2025-01'.
    endpoint_url = f"{API_BASE_URL}/release/11/2025-01/mms/autocode"
    
    # --- Required Headers ---
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Accept-Language': 'en',  # Language for the response
        'API-Version': 'v2'       # Using Version 2 of the API
    }
    
    # --- Query Parameters ---
    params = {
        'searchText': search_text
    }
    
    try:
        # Make the GET request to the autocode endpoint
        response = requests.get(endpoint_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        # Process the result
        code = result.get('theCode')
        match_text = result.get('matchingText')
        
        if code:
            print("\n--- Result ---")
            print(f"✅ Found a match!")
            print(f"   Search Term:    '{search_text}'")
            print(f"   Matched Term:   '{match_text}'")
            print(f"   ICD-11 Code:      {code}")
            print("--------------\n")
        else:
            print(f"⚠️ No direct code match found for '{search_text}'.")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching ICD code: {e}")
        if 'response' in locals() and response.text:
            print(f"   Server response: {response.text}")

if __name__ == "__main__":
    access_token = get_access_token()
    fetch_icd_code(access_token, SEARCH_TERM)