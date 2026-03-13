# StudyFlow AI

StudyFlow AI is an AI-powered study planner that automatically generates a **personalized study schedule** from a student's **syllabus and exam datesheet**.

Instead of manually planning study sessions, users simply upload their syllabus and exam schedule. The system extracts topics, matches them with exam dates, and generates a **day-by-day study plan optimized around the user’s available study hours and progress.**

---

# Features

### AI Syllabus Understanding

Uploads supported:

* PDF syllabus
* DOCX syllabus
* Image or PDF exam datesheets

The system extracts text from these files and uses an LLM to structure the data.

### Automatic Study Plan Generation

StudyFlow AI generates a **date-wise study schedule** based on:

* Exam dates
* Topics to study
* User's available study hours

### Progress Tracking

Users can update their progress for each topic:

* Done
* Partially Done
* Incomplete
* Custom progress notes

The schedule can be **re-adjusted based on updated progress.**

### User Accounts

Each user has their own account:

* Secure login
* Password hashing with salt
* Personal study schedules stored in the database

### Persistent Data

All study plans and progress are saved so users can **resume planning later.**

---

# Tech Stack

### Backend

* Python
* Flask
* SQLAlchemy
* SQLite

### AI Models

Using OpenRouter LLM APIs:

* `qwen/qwen2.5-72b-instruct`
* `qwen/qwen3-vl-235b-a22b-thinking`

Used for:

* syllabus understanding
* topic extraction
* exam date matching
* schedule planning

### Frontend

* HTML
* CSS
* JavaScript

### Document Processing

* PyPDF
* python-docx
* Pillow

---

# Project Structure

```
StudyFlow-AI
│
├── app.py                 # Main Flask server
├── models.py              # Database models
├── text_extractor.py      # File text extraction + AI structuring
├── schedule_planner.py    # Study schedule generation
│
├── templates
│   ├── login.html
│   ├── Upload-page.html
│   ├── Status.html
│   └── Schedule.html
│
├── static
│   ├── upload.js
│   ├── Status.js
│   ├── schedule.js
│   ├── Upload-page.css
│   └── Status.css
│
├── uploads                # Uploaded files
├── instance               # Database storage
│
└── README.md
```

---

# How It Works

### 1 Upload Syllabus + Datesheet

The user uploads:

* syllabus document
* exam schedule

### 2 Text Extraction

Files are processed and converted to text using:

* PDF parser
* DOCX parser
* Image processing

### 3 AI Structuring

The extracted text is sent to the LLM which produces structured JSON:

```
{
  "subjects":[
    {
      "subject":"Design Thinking with AI",
      "exam_date":"2026-01-15",
      "topics":[
        "Introduction to Design Thinking",
        "Empathy and Problem Identification",
        "AI Ethics"
      ]
    }
  ]
}
```

### 4 User Progress Input

The user marks their preparation status for each topic.

### 5 Schedule Generation

The system generates a daily schedule based on:

* exam dates
* study hours per day
* progress level

### 6 Study Plan Display

The final study plan is displayed date-wise.

Example:

```
2026-01-02
    Design Thinking
        - Empathy and Problem Identification (2h)

2026-01-03
    Design Thinking
        - AI Ethics (2h)
```

---

# Installation

Clone the repository:

```
git clone https://github.com/YOUR_USERNAME/StudyFlow-AI.git
cd StudyFlow-AI
```

Create virtual environment:

```
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```
pip install flask flask_sqlalchemy python-docx pypdf openai pillow
```

---

# Environment Setup

Create a file:

```
apikey.py
```

Inside it add:

```
key = "YOUR_OPENROUTER_API_KEY"
```

---

# Run the Server

```
python app.py
```

Server will start at:

```
http://127.0.0.1:5000
```

---

# Future Improvements

* Smart schedule optimization
* Deadline prioritization
* Pomodoro-based scheduling
* Mobile UI support
* Google Calendar integration
* Offline scheduling mode

---

# Demo Use Case

Example workflow:

1. Upload syllabus PDF
2. Upload exam datesheet image
3. AI extracts topics and exam dates
4. User selects preparation level
5. AI generates a full study schedule

---

# License

MIT License

---

# Author

Built for AI Hackathon by:

**Ayush** and **Manish**

Passionate about AI, software engineering, and building intelligent systems.
