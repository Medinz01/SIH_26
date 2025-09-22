import sys
import os
from fastapi.testclient import TestClient

# Add the project root directory to the Python path
# This allows the test script to find the 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

# This creates a special client that can call your API endpoints from within the code
client = TestClient(app)

def test_health_check():
    """
    Tests the most basic endpoint to ensure the server is running.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_icd11_search():
    """
    Tests the ICD-11 search endpoint to ensure it connects to the DB
    and returns a valid response.
    """
    response = client.get("/search/icd11?term=Cholera")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check if we got at least one result and it contains the term
    assert len(data) > 0
    assert "Cholera" in data[0]["term"]
    assert "1A00" in data[0]["code"]

def test_namaste_search():
    """
    Tests the NAMASTE search endpoint.
    """
    response = client.get("/search/namaste?term=vikāraḥ")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["term"] == "vikāraḥ"

def test_map_endpoint_not_found():
    """
    Tests that the mapping endpoint correctly returns a 404 error
    for a code that has no map.
    """
    response = client.get("/map?namaste_code=NON_EXISTENT&namaste_system=ayurveda")
    assert response.status_code == 404

# You can add a test for a successful map once you have a known mapping
# in your 'build_live_map.py' or a manual mapping file.
# def test_map_endpoint_success():
#     # This test depends on your `build_live_map` script finding this specific map.
#     # You might need to adjust the code and system based on your data.
#     response = client.get("/map?namaste_code=A-2&namaste_system=unani")
#     if response.status_code == 200:
#         data = response.json()
#         assert data["source_term"]["code"] == "A-2"
#         assert data["target_term"]["code"] is not None
#     else:
#         # This allows the test to pass even if the map isn't created yet
#         assert response.status_code == 404

