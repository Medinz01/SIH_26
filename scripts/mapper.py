import requests
import sys
import time
import csv
import os

# --------------------------------------------------------------------------
# IMPORTANT: Replace these placeholders with your actual Client ID and Secret
# --------------------------------------------------------------------------
CLIENT_ID = "9753f1bd-4738-42c8-9081-963e1e8f8551_aa2b763e-6c0a-4d54-85e8-135fe144fcd0"
CLIENT_SECRET = "KmWdoiVii9wZhFPG7hF0AQyoh1Pnwco3MGzwmGf8hV0="

# --- Configuration ---
TOKEN_URL = 'https://icdaccessmanagement.who.int/connect/token'
API_BASE_URL = 'https://id.who.int/icd'
INPUT_FILE = 'combined_namaste_codes.csv'
OUTPUT_FILE = 'enriched_namaste_codes_with_icd11.csv'

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
        # Increased timeout for the token request as well
        response = requests.post(TOKEN_URL, data=token_payload, timeout=30)
        response.raise_for_status()
        print("✅ Access token received.")
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting access token: {e}")
        return None

# --- MODIFIED FUNCTION WITH RETRY LOGIC ---
def search_icd_term(token, term, headers):
    """
    Searches for a term within Chapter 26 with automatic retries.
    Returns a dictionary with 'icd11_term' and 'icd11_code'.
    """
    if not term:
        return {'icd11_term': '', 'icd11_code': ''}

    endpoint_url = f"{API_BASE_URL}/release/11/2025-01/mms/search"
    params = {'q': term, 'chapterFilter': '26'}
    
    # Retry parameters
    max_retries = 5
    base_delay = 5 # seconds

    for attempt in range(max_retries):
        try:
            # Increased timeouts: (connect_timeout, read_timeout)
            response = requests.get(endpoint_url, headers=headers, params=params, timeout=(15, 30))
            
            # Check for non-200 status codes which indicate an API error, not a network error
            if response.status_code != 200:
                print(f"  - API returned status {response.status_code} for '{term}'. Skipping.")
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
            # This catches network errors like timeouts and connection issues
            print(f"  - Network error for '{term}': {type(e).__name__}. Attempt {attempt + 1} of {max_retries}.")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) # Exponential backoff
                print(f"    Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"  - Max retries reached for '{term}'. Skipping.")
                return {'icd11_term': '', 'icd11_code': ''}
    
    return {'icd11_term': '', 'icd11_code': ''} # Fallback in case loop finishes unexpectedly

def main():
    """Main function to process the CSV file."""
    token = get_access_token()
    if not token:
        sys.exit(1)

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Accept-Language': 'en',
        'API-Version': 'v2'
    }

    processed_codes = set()
    if os.path.exists(OUTPUT_FILE):
        print(f"✅ Output file '{OUTPUT_FILE}' found. Resuming from last point.")
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f_out:
            reader = csv.DictReader(f_out)
            for row in reader:
                if 'namaste_code' in row:
                    processed_codes.add(row['namaste_code'])
        print(f"   - Found {len(processed_codes)} previously processed codes.")
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f_in, \
             open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f_out:

            reader = csv.DictReader(f_in)
            output_headers = reader.fieldnames + ['icd11_term', 'icd11_code']
            writer = csv.DictWriter(f_out, fieldnames=output_headers)

            if not processed_codes:
                writer.writeheader()

            for i, row in enumerate(reader):
                namaste_code = row.get('namaste_code')
                if namaste_code in processed_codes:
                    continue

                search_name = row.get('name')
                print(f"Processing row {i+1}: '{search_name}' ({namaste_code})")
                
                icd_data = search_icd_term(token, search_name, headers)
                row.update(icd_data)
                writer.writerow(row)

    except FileNotFoundError:
        print(f"❌ ERROR: Input file '{INPUT_FILE}' not found.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Ctrl+C detected. Saving progress and exiting gracefully.")
        sys.exit(0)
    
    print("\n🎉 Processing complete.")

if __name__ == "__main__":
    main()