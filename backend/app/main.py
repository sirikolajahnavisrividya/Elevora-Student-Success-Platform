from pathlib import Path
from datetime import datetime
import json
import re
import sqlite3
import urllib.error
import urllib.request
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pypdf import PdfReader

from .schemas import StudentFeatures, PredictionResponse
from .model_service import predict

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "student_support.db"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "llama3.2:3b"

app = FastAPI(title="AI Academic Risk Prediction API", version="1.1.0", description="Academic risk prediction and offline study support.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT NOT NULL,
            weekday TEXT NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL,
            kind TEXT NOT NULL DEFAULT 'Study', notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS textbooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL,
            page_count INTEGER NOT NULL DEFAULT 0, uploaded_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS textbook_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, textbook_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL, content TEXT NOT NULL,
            FOREIGN KEY(textbook_id) REFERENCES textbooks(id) ON DELETE CASCADE)""")

init_db()

class TimetableItem(BaseModel):
    subject: str = Field(..., min_length=1, max_length=100)
    weekday: str
    start_time: str
    end_time: str
    kind: str = "Study"
    notes: str = ""

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=3000)
    textbook_id: Optional[int] = None

class RevisionRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    format: str = "revision sheet"
    textbook_id: Optional[int] = None

@app.get("/")
def root():
    return {"name": "AI Academic Risk Prediction System", "status": "ok", "version": "1.1.0"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "ollama_model": OLLAMA_MODEL}

@app.post("/api/predict", response_model=PredictionResponse)
def predict_risk(student: StudentFeatures):
    try:
        return predict(student.model_dump())
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

@app.get("/api/timetable")
def get_timetable():
    with connect_db() as conn:
        rows = conn.execute("SELECT * FROM timetable ORDER BY CASE weekday WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 ELSE 7 END, start_time").fetchall()
    return [dict(row) for row in rows]

@app.post("/api/timetable")
def add_timetable(item: TimetableItem):
    days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
    if item.weekday not in days:
        raise HTTPException(400, "Choose a valid weekday.")
    for t in (item.start_time, item.end_time):
        try: datetime.strptime(t, "%H:%M")
        except ValueError: raise HTTPException(400, "Times must use 24-hour HH:MM format.")
    if item.start_time >= item.end_time:
        raise HTTPException(400, "End time must be after start time.")
    with connect_db() as conn:
        cur = conn.execute("INSERT INTO timetable(subject,weekday,start_time,end_time,kind,notes,created_at) VALUES(?,?,?,?,?,?,?)", (item.subject.strip(), item.weekday, item.start_time, item.end_time, item.kind, item.notes.strip(), datetime.now().isoformat(timespec="seconds")))
        row = conn.execute("SELECT * FROM timetable WHERE id=?", (cur.lastrowid,)).fetchone()
    return dict(row)

@app.delete("/api/timetable/{item_id}")
def delete_timetable(item_id: int):
    with connect_db() as conn:
        cur = conn.execute("DELETE FROM timetable WHERE id=?", (item_id,))
    if cur.rowcount == 0: raise HTTPException(404, "Timetable item not found.")
    return {"deleted": True, "id": item_id}

@app.get("/api/textbooks")
def list_textbooks():
    with connect_db() as conn:
        rows = conn.execute("SELECT t.id,t.filename,t.page_count,t.uploaded_at,COUNT(c.id) AS chunks FROM textbooks t LEFT JOIN textbook_chunks c ON c.textbook_id=t.id GROUP BY t.id ORDER BY t.id DESC").fetchall()
    return [dict(r) for r in rows]

@app.post("/api/textbooks/upload")
def upload_textbook(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF textbook or notes file.")
    try:
        reader = PdfReader(file.file)
        page_text = [(i + 1, (p.extract_text() or "").strip()) for i, p in enumerate(reader.pages)]
    except Exception as e:
        raise HTTPException(400, f"Could not read this PDF: {e}")
    if not any(text for _, text in page_text):
        raise HTTPException(400, "No selectable text found. Scanned PDFs need OCR before they can be searched.")
    with connect_db() as conn:
        cur = conn.execute("INSERT INTO textbooks(filename,page_count,uploaded_at) VALUES(?,?,?)", (file.filename, len(reader.pages), datetime.now().isoformat(timespec="seconds")))
        textbook_id = cur.lastrowid
        for page_num, text in page_text:
            # Chunk each page into short overlapping passages for local keyword retrieval.
            words = text.split()
            for start in range(0, len(words), 180):
                chunk = " ".join(words[start:start+220]).strip()
                if chunk:
                    conn.execute("INSERT INTO textbook_chunks(textbook_id,page_number,content) VALUES(?,?,?)", (textbook_id, page_num, chunk))
    return {"id": textbook_id, "filename": file.filename, "page_count": len(reader.pages), "message": "PDF text indexed locally."}

STOPWORDS = set("the a an and or is are was were to of in on for with what how why explain describe define give from this that these those about into by as it be can could should would do does did i you we they their your please simple example".split())
def retrieve_chunks(question: str, textbook_id: Optional[int], limit: int = 5):
    words = [w.lower() for w in re.findall(r"[a-zA-Z0-9]{3,}", question) if w.lower() not in STOPWORDS]
    if not words: words = [w.lower() for w in re.findall(r"[a-zA-Z0-9]{3,}", question)]
    with connect_db() as conn:
        if textbook_id:
            rows = conn.execute("SELECT c.*,t.filename FROM textbook_chunks c JOIN textbooks t ON t.id=c.textbook_id WHERE c.textbook_id=?", (textbook_id,)).fetchall()
        else:
            rows = conn.execute("SELECT c.*,t.filename FROM textbook_chunks c JOIN textbooks t ON t.id=c.textbook_id").fetchall()
    scored=[]
    for row in rows:
        text = row["content"]
        low = text.lower()
        score = sum(low.count(w) for w in words)
        if score:
            scored.append((score, row))
    scored.sort(key=lambda x:x[0], reverse=True)
    return [{"filename": r["filename"], "page_number": r["page_number"], "content": r["content"], "score": score} for score,r in scored[:limit]]

def ollama_chat(system_prompt: str, user_prompt: str):
    payload = json.dumps({"model": OLLAMA_MODEL, "stream": False, "messages": [{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}], "options":{"temperature":0.2}}).encode("utf-8")
    req = urllib.request.Request(OLLAMA_URL, data=payload, headers={"Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("message", {}).get("content", "No response was returned.")
    except urllib.error.URLError as e:
        raise HTTPException(503, "Cannot connect to Ollama. Start Ollama and check that llama3.2:3b is installed.") from e
    except TimeoutError as e:
        raise HTTPException(504, "The local model took too long to respond. Try a shorter question.") from e

@app.post("/api/study/chat")
def textbook_chat(request: ChatRequest):
    chunks = retrieve_chunks(request.question, request.textbook_id)
    if not chunks:
        raise HTTPException(400, "Upload a text-based PDF first, or ask a question that matches the uploaded material.")
    context = "\n\n".join(f"Source: {c['filename']}, page {c['page_number']}\n{c['content']}" for c in chunks)
    answer = ollama_chat("You are an offline study tutor. Explain in clear, student-friendly language. Prioritize the provided textbook excerpts. If the excerpts do not contain enough information, say so instead of inventing textbook facts. Do not help with cheating during a live exam.", f"Textbook excerpts:\n{context}\n\nStudent question: {request.question}\n\nAnswer with an explanation and cite source filename and page numbers where possible.")
    sources = [{"filename": c["filename"], "page_number": c["page_number"]} for c in chunks]
    return {"answer": answer, "sources": sources, "model": OLLAMA_MODEL}

@app.post("/api/study/revision")
def make_revision(request: RevisionRequest):
    chunks = retrieve_chunks(request.topic, request.textbook_id, limit=7)
    if not chunks:
        raise HTTPException(400, "Upload a text-based PDF first, and choose a topic that appears in the material.")
    context = "\n\n".join(f"Source: {c['filename']}, page {c['page_number']}\n{c['content']}" for c in chunks)
    fmt = request.format.lower()
    instruction = "Create a concise exam revision sheet with headings, key concepts, definitions, and a short recap." if fmt == "revision sheet" else "Create flashcards as numbered Question / Answer pairs." if fmt == "flashcards" else "Create 8 practice questions based on the excerpts, then provide an answer key with brief explanations."
    answer = ollama_chat("You are an offline exam revision assistant. Use the provided textbook excerpts as the source. Do not invent details that are absent from the excerpts. Format the output clearly in plain text/Markdown.", f"Topic: {request.topic}\nTask: {instruction}\nTextbook excerpts:\n{context}")
    sources = [{"filename": c["filename"], "page_number": c["page_number"]} for c in chunks]
    return {"content": answer, "sources": sources, "model": OLLAMA_MODEL}
