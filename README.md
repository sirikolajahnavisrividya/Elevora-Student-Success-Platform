\# Elevora — Student Success Platform



\*\*Your Journey. Your Progress. Your Success.\*\*



Elevora is a student-focused platform designed to help learners monitor academic performance, organize study schedules, and prepare for examinations through personalized study support.



The platform combines academic risk assessment, timetable management, textbook-based question answering, and revision material generation in one interface.



\## Overview



Students often struggle to manage their academic workload, identify areas that need improvement, and prepare effectively for examinations.



Elevora brings these activities together in a single platform, helping students make informed study decisions and organize their learning more effectively.



\## Features



\### 1. Academic Risk Assessment



\* Accepts academic indicators such as attendance, internal marks, assignment scores, quiz scores, CGPA, backlogs, and daily study hours.

\* Generates a predicted academic risk category.

\* Displays contributing factors and suggested next steps.

\* Uses a Random Forest model for prediction.



\### 2. Study Timetable



\* Create and manage study sessions.

\* Specify subjects, days, timings, activities, and notes.

\* Store timetable entries in a local SQLite database.

\* Display study reminders while the dashboard is open.



\### 3. Textbook Question Answering



\* Upload text-based PDF textbooks.

\* Extract and index textbook content locally.

\* Ask questions about uploaded study materials.

\* Generate answers using relevant passages retrieved from the documents.

\* Display source information to help verify answers.



\### 4. Revision Material Generation



\* Generate revision sheets.

\* Create flashcards.

\* Generate practice questions and answers.

\* Use uploaded textbook content to support exam preparation.



\### 5. Local Processing



\* Uses a locally running Ollama model for study assistance.

\* Keeps textbook processing and timetable storage on the local machine.

\* Supports offline study assistance after the required software and model have been installed.



\## Technology Stack



| Component              | Technologies                         |

| ---------------------- | ------------------------------------ |

| Frontend               | React, Vite, JavaScript, CSS         |

| Backend                | Python, FastAPI                      |

| Machine Learning       | Scikit-learn, Random Forest          |

| Database               | SQLite                               |

| Language Model Runtime | Ollama                               |

| Local Language Model   | Llama 3.2 3B                         |

| PDF Processing         | pypdf                                |

| Development Tools      | Visual Studio Code, CMD, Git, GitHub |



\## Project Structure



```text

Elevora-Student-Success-Platform/

│

├── backend/

│   ├── app/

│   ├── data/

│   ├── models/

│   ├── tests/

│   ├── training/

│   └── requirements.txt

│

├── frontend/

│   ├── src/

│   ├── package.json

│   └── index.html

│

├── .gitignore

├── PROJECT\_ROADMAP.md

├── PROJECT\_STATUS.txt

├── README.md

├── run\_backend.bat

└── run\_frontend.bat

```



\## Installation and Setup



\### Prerequisites



Install the following software:



\* Python 3.11

\* Node.js and npm

\* Ollama

\* Git



The project uses the `llama3.2:3b` model for local study assistance.



\### Step 1: Download the Project



Clone the repository or download its ZIP archive and extract it.



Open CMD and navigate to the extracted project directory.



\### Step 2: Set Up the Backend



Open a CMD window and navigate to the backend folder:



```cmd

cd /d C:\\AIProject\\backend

```



Create a Python virtual environment if one does not already exist:



```cmd

py -3.11 -m venv .venv311

```



Activate it:



```cmd

.venv311\\Scripts\\activate.bat

```



Install the required packages:



```cmd

python -m pip install -r requirements.txt

```



Start the backend:



```cmd

python -m uvicorn app.main:app --reload

```



The backend runs on the local development address configured by the application.



\### Step 3: Set Up the Frontend



Open a second CMD window:



```cmd

cd /d C:\\AIProject\\frontend

```



Install the dependencies:



```cmd

npm install

```



Start the development server:



```cmd

npm run dev

```



Open the local address displayed in the terminal to access Elevora.



\### Step 4: Configure the Local Language Model



Ensure Ollama is installed and running.



Download the required model:



```cmd

ollama pull llama3.2:3b

```



Verify that the model is available:



```cmd

ollama list

```



Keep the backend, frontend, and Ollama running while using the application.



\*\*Note:\*\* Replace `C:\\AIProject` in these instructions with the actual project directory on your computer.



\## How It Works



1\. The student enters academic indicators into the assessment form.

2\. The backend processes the submitted information and returns a predicted risk category.

3\. The student organizes study activities using the timetable.

4\. Textbook PDFs can be uploaded for local text extraction and indexing.

5\. The study assistant retrieves relevant passages and sends them to the local language model to generate an answer.

6\. Students can generate revision materials based on their selected topics and available textbook content.



\## Current Limitations



\* The academic risk model was trained on sample or synthetic data and has not been validated on a representative real-world student dataset.

\* Predictions should be treated as preliminary guidance, not definitive judgments about a student's academic future.

\* Textbook retrieval uses keyword-based matching rather than vector-based semantic search.

\* Scanned PDFs without selectable text are not supported unless OCR is added.

\* Browser reminders operate while the dashboard remains open.

\* Generated answers and revision materials should be verified against the original textbooks.

\* A local language model and its dependencies must be installed before using the study assistant.



\## Future Enhancements



\* Improve prediction reliability using appropriately collected and consented academic datasets.

\* Add semantic search using embeddings and vector storage.

\* Support OCR for scanned textbooks.

\* Improve reminder scheduling and notification handling.

\* Add academic progress visualizations.

\* Expand testing, accessibility, and error handling.

\* Provide downloadable revision materials.



\## Project Purpose



Elevora aims to make academic planning, performance monitoring, and exam preparation more organized and accessible through a unified student support platform.



\## Disclaimer



Elevora is an educational prototype. Its academic risk predictions are not validated for consequential decisions. Students and educators should consider additional evidence and professional judgment when evaluating academic performance.



