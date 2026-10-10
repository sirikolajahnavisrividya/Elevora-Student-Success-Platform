@echo off
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  python -m venv .venv
  call .venv\Scripts\activate
  pip install -r requirements.txt
) else (
  call .venv\Scripts\activate
)
if not exist "models\risk_model.joblib" (
  echo Training the initial model...
  python training\train_model.py
)
echo Starting FastAPI...
uvicorn app.main:app --reload
pause
