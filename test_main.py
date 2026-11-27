"""Unit tests for the FastAPI application in main.py."""
import socket

from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


def test_root():
    """GET / returns the health message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "it works !"}


def test_addition():
    """GET /addition returns a + b."""
    response = client.get("/addition?a=2&b=3")
    assert response.status_code == 200
    assert response.json() == {"result a+b=": 5, "developer": "Dev1"}


def test_soustraction():
    """GET /soustraction returns a - b."""
    response = client.get("/soustraction?a=5&b=3")
    assert response.status_code == 200
    assert response.json() == {"result a-b=": 2, "developer": "Dev1"}


def test_soustraction_negative_result():
    """GET /soustraction works when b > a."""
    response = client.get("/soustraction?a=3&b=5")
    assert response.json()["result a-b="] == -2


def test_soustraction_invalid_input():
    """GET /soustraction rejects a non-integer parameter with HTTP 422."""
    response = client.get("/soustraction?a=x&b=5")
    assert response.status_code == 422


def test_greeting():
    """GET /greeting returns the name, host name and IP."""
    response = client.get("/greeting?name=Mahran")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Hello, Mahran"
    assert body["developer"] == "Dev2"
    assert body["hostname"] == socket.gethostname()
    assert "IP" in body


class _OfflineSocket:  # pylint: disable=too-few-public-methods
    """Fake socket whose connect() fails, as if there were no network."""

    def __init__(self, *args):
        self.args = args

    def connect(self, address):
        """Always fail, like a machine with no network."""
        raise OSError(f"no network to {address}")

    def close(self):
        """Nothing to close."""


def test_current_ip_without_network(monkeypatch):
    """current_ip() falls back to 127.0.0.1 when the network is down."""
    monkeypatch.setattr(main.socket, "socket", _OfflineSocket)
    assert main.current_ip() == "127.0.0.1"


def test_multiply():
    """POST /multiply returns a * b."""
    response = client.post("/multiply", json={"a": 4, "b": 2.5})
    assert response.status_code == 200
    assert response.json() == {"result a*b=": 10.0, "developer": "Dev1"}


def test_divide():
    """POST /divide returns a / b."""
    response = client.post("/divide", json={"a": 10, "b": 4})
    assert response.status_code == 200
    assert response.json() == {"result a/b=": 2.5, "developer": "Dev2"}


def test_divide_by_zero():
    """POST /divide returns HTTP 400 when b is 0."""
    response = client.post("/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    assert response.json() == {"detail": "Division by zero"}


def test_list_items():
    """GET /items lists the items."""
    response = client.get("/items")
    assert response.status_code == 200
    assert {"id": 1, "name": "item1", "description": "first item"} in response.json()


def test_remove_item():
    """DELETE /remove/{id} deletes an existing item."""
    response = client.delete("/remove/3")
    assert response.status_code == 200
    assert response.json() == {"deleted": 3, "developer": "Dev1"}
    assert 3 not in main.items


def test_remove_missing_item():
    """DELETE /remove/{id} returns HTTP 404 for an unknown id."""
    response = client.delete("/remove/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
