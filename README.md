# AI Academic Risk Prediction & Offline Study Assistant

## Features
- Random Forest academic risk prediction (existing model).
- Timetable stored in SQLite, with in-app reminders while the dashboard is open.
- Offline Ollama textbook question answering over text extracted from uploaded PDFs.
- Offline revision sheet, flashcard, and practice-question generation from retrieved passages.

## Requirements
- Python 3.11 recommended.
- Node.js and npm.
- Ollama installed and running with `llama3.2:3b` pulled.

## Backend (CMD)
```cmd
cd /d "PATH_TO_PROJECT\backend"
.venv311\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
If `.venv311` is missing, create it with `py -3.11 -m venv .venv311` first.

## Frontend (second CMD window)
```cmd
cd /d "PATH_TO_PROJECT\frontend"
npm install
npm run dev
```
Open the Vite URL, normally http://localhost:5173.

## Local AI notes
Ollama model is configured as `llama3.2:3b` in `backend/app/main.py`. The textbook feature uses local PDF text extraction and keyword-based passage retrieval before asking Ollama to answer. Scanned PDFs without selectable text are not supported unless OCR is added. Uploaded PDFs and timetable entries are stored in `backend/data/student_support.db`. Browser reminders only run while the dashboard is open; notifications require browser permission.

## Limitations
- Keyword retrieval is a lightweight offline baseline, not vector-semantic retrieval.
- The included risk model was trained on sample/synthetic data; it is a prototype, not a validated clinical/educational decision system.
- Use predictions as a support signal, not as the sole basis for consequential decisions.
