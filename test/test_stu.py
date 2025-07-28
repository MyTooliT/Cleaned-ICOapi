from fastapi.testclient import TestClient

from icoapi.api import app

client = TestClient(app)
stu_prefix = "/api/v1/stu"

def test_root():
    """Test endpoint ``/``"""
    
    response = client.get(stu_prefix)
    assert response.status_code == 200
