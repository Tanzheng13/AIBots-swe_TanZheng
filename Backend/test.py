from fastapi.testclient import TestClient
from main import app  # Replace 'your_main_module' with the actual name of your FastAPI application

client = TestClient(app)

def test_test_endpoint():
    # Send a GET request to the /test endpoint
    response = client.get("/test")

    # Assert that the status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response body matches the expected result
    assert response.text == "Endpoint Reached"