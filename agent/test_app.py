import json
from unittest.mock import patch
import pytest
from agent.app import app

@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c: yield c

def test_missing_both_returns_400(client):
    resp = client.post("/invoke", json={})
    assert resp.status_code == 400

def test_missing_session_id_returns_400(client):
    resp = client.post("/invoke", json={"message": "hello"})
    assert resp.status_code == 400

def test_missing_message_returns_400(client):
    resp = client.post("/invoke", json={"session_id": "abc"})
    assert resp.status_code == 400

def test_successful_invoke(client):
    with patch("agent.app.run_turn", return_value="How can I help?") as mock:
        resp = client.post("/invoke", json={"session_id": "s1", "message": "help"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["session_id"] == "s1"
    assert body["reply"] == "How can I help?"

def test_exception_returns_500(client):
    with patch("agent.app.run_turn", side_effect=RuntimeError("boom")):
        resp = client.post("/invoke", json={"session_id": "s2", "message": "test"})
    assert resp.status_code == 500

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
