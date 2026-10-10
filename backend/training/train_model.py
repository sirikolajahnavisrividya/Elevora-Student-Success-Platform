from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
MODEL_DIR = BASE / "models"
DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
n = 1800

attendance = np.clip(rng.normal(78, 14, n), 35, 100)
internal = np.clip(rng.normal(65, 16, n), 15, 100)
assignment = np.clip(rng.normal(70, 15, n), 10, 100)
quiz = np.clip(rng.normal(68, 17, n), 10, 100)
cgpa = np.clip(rng.normal(7.1, 1.1, n), 3, 10)
backlogs = np.clip(rng.poisson(0.8, n), 0, 6)
study = np.clip(rng.normal(2.8, 1.5, n), 0.2, 10)

risk_score = (
    (75 - attendance) * 0.30 +
    (55 - internal) * 0.25 +
    (60 - assignment) * 0.10 +
    (60 - quiz) * 0.10 +
    (6.5 - cgpa) * 10 * 0.12 +
    backlogs * 3.0 +
    (2 - study) * 2.0 +
    rng.normal(0, 5, n)
)

# 0=LOW, 1=MEDIUM, 2=HIGH
y = np.select([risk_score > 18, risk_score > -5], [2, 1], default=0)

df = pd.DataFrame({
    "attendance": attendance.round(2),
    "internal_marks": internal.round(2),
    "assignment_score": assignment.round(2),
    "quiz_score": quiz.round(2),
    "previous_cgpa": cgpa.round(2),
    "backlogs": backlogs,
    "study_hours": study.round(2),
    "risk": y
})
df.to_csv(DATA_DIR / "academic_risk_dataset.csv", index=False)

features = ["attendance","internal_marks","assignment_score","quiz_score","previous_cgpa","backlogs","study_hours"]
X_train, X_test, y_train, y_test = train_test_split(
    df[features], df["risk"], test_size=0.2, random_state=42, stratify=df["risk"]
)

model = RandomForestClassifier(
    n_estimators=250,
    max_depth=10,
    min_samples_leaf=3,
    random_state=42,
    class_weight="balanced"
)
model.fit(X_train, y_train)

pred = model.predict(X_test)
print("Accuracy:", round(accuracy_score(y_test, pred), 4))
print(classification_report(y_test, pred, target_names=["LOW","MEDIUM","HIGH"]))
print("Confusion matrix:\n", confusion_matrix(y_test, pred))

joblib.dump(model, MODEL_DIR / "risk_model.joblib")
print(f"\nSaved model to: {MODEL_DIR / 'risk_model.joblib'}")
print(f"Saved dataset to: {DATA_DIR / 'academic_risk_dataset.csv'}")
