from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_soustraction():
    response = client.get("/soustraction?a=5&b=3")
    assert response.status_code == 200
    assert response.json() == {"result a-b=": 2, "developer": "Dev1"}