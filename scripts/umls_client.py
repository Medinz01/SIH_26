import requests
import os

# It's best practice to get your API key from an environment variable
# rather than hardcoding it.
UMLS_API_KEY = os.environ.get("UMLS_API_KEY")
BASE_URI = "https://uts-ws.nlm.nih.gov/rest"

if not UMLS_API_KEY:
    print("ERROR: UMLS_API_KEY environment variable not set.")
    print("Please get your key from https://uts.nlm.nih.gov/uts/profile")
    exit()

def get_cui_for_term(term: str) -> str | None:
    """Searches the UMLS for a term and returns the top CUI if found."""
    print(f"Searching for CUI for term: '{term}'...")
    endpoint = f"/search/current"
    url = BASE_URI + endpoint
    params = {
        "string": term,
        "apiKey": UMLS_API_KEY,
        "sabs": "SNOMEDCT_US,LNC,ICD10CM", # Prioritize these sources
        "searchType": "exact"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an exception for bad status codes
        data = response.json()
        
        if data["result"]["results"]:
            top_result_cui = data["result"]["results"][0]["ui"]
            print(f"Found CUI: {top_result_cui}")
            return top_result_cui
        else:
            print("No CUI found.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# --- You can run this file directly to test it ---
if __name__ == "__main__":
    # Example usage:
    test_term = "Diabetes mellitus" 
    cui = get_cui_for_term(test_term)
    
    if cui:
        # In the next step, we'll build the function to get mappings for this CUI.
        print(f"Next step will be to find mappings for CUI: {cui}")