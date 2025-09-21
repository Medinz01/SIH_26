from fastapi.testclient import TestClient
from app.main import app

# Create a test client that can make requests to your FastAPI app
client = TestClient(app)

def test_health_check():
    """
    Tests if the /health endpoint is working correctly.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_search_for_term():
    """
    Tests the core /search functionality.
    """
    response = client.get("/search?term=fever") # Assuming 'fever' is in your test data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # This assertion might need to be adjusted based on your actual data
    if data:
        assert "fever" in data[0]["term"].lower()

def test_mapping_endpoint_success():
    """
    Tests a successful mapping from a NAMASTE code to an ICD code.
    """
    # IMPORTANT: Replace 'AYU0001' with a real code from your dataset
    test_code = "AYU0001" 
    response = client.get(f"/map/namaste/{test_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["namaste_code"] == test_code
    assert "icd_code" in data

def test_mapping_endpoint_not_found():
    """
    Tests the API's response for a code that does not exist.
    """
    response = client.get("/map/namaste/INVALID_CODE")
    assert response.status_code == 404
    assert response.json() == {"detail": "No mapping found for NAMASTE code: INVALID_CODE"}