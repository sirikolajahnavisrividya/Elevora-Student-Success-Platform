from pathlib import Path
import joblib
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE / "models" / "risk_model.joblib"

FEATURES = [
    "attendance", "internal_marks", "assignment_score",
    "quiz_score", "previous_cgpa", "backlogs", "study_hours"
]

_model = None

def load_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Model not found. Run: python training/train_model.py"
            )
        _model = joblib.load(MODEL_PATH)
    return _model

def predict(data: dict):
    model = load_model()
    row = pd.DataFrame([{k: data[k] for k in FEATURES}])
    pred = int(model.predict(row)[0])
    probs = model.predict_proba(row)[0]
    confidence = float(max(probs))

    labels = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
    risk = labels[pred]

    factors = []
    if data["attendance"] < 75:
        factors.append("Attendance is below 75%.")
    if data["internal_marks"] < 50:
        factors.append("Internal examination marks are low.")
    if data["assignment_score"] < 60:
        factors.append("Assignment performance needs improvement.")
    if data["quiz_score"] < 60:
        factors.append("Quiz performance needs improvement.")
    if data["previous_cgpa"] < 6.5:
        factors.append("Previous CGPA indicates academic risk.")
    if data["backlogs"] > 0:
        factors.append(f"{data['backlogs']} backlog(s) are present.")
    if data["study_hours"] < 2:
        factors.append("Daily study time is low.")

    if not factors:
        factors.append("No major risk factor was detected from the supplied inputs.")

    if risk == "HIGH":
        recommendation = "Prioritize weak subjects, improve attendance, clear pending work, and seek faculty support early."
    elif risk == "MEDIUM":
        recommendation = "Improve the weakest academic areas and monitor attendance and assessment performance weekly."
    else:
        recommendation = "Maintain current performance and continue regular attendance, assignments, and revision."

    return {
        "risk_level": risk,
        "risk_probability": round(confidence * 100, 2),
        "recommendation": recommendation,
        "factors": factors,
        "model_version": "v1.0.0"
    }
