from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_prediction():
    payload = {
        "attendance": 72,
        "internal_marks": 58,
        "assignment_score": 65,
        "quiz_score": 60,
        "previous_cgpa": 7.0,
        "backlogs": 1,
        "study_hours": 2.5
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert 0 <= body["risk_probability"] <= 100
