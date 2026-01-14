# Typing Report Generator API

A FastAPI-based backend service that generates detailed typing performance reports for students. The API aggregates student activity data, calculates statistics, generates summaries, and provides AI-based feedback for both **Exercise** and **Pool** typing modes.

---

## 🚀 Features

* FastAPI backend with REST endpoints
* Student-wise typing performance reports
* Separate analysis for **Exercise** and **Pool** modes
* Overall statistics and latest drill report
* AI-generated feedback per mode
* Static frontend support
* CORS enabled for local development

---

## 🛠️ Tech Stack

* **Python**
* **OllamaLLM**
* **langchain**
* **FastAPI**
* **Uvicorn** (recommended ASGI server)
* **pymysql**
* **CORS Middleware**
* Static file serving via FastAPI

---



## ⚙️ Setup & Installation

1. **Clone the repository**

   ```bash
   git clone <https://github.com/Jasbeer-KA/AI_Dashboard_Report_Generator.git>
   cd AI_Dashboard_Report_Generator
   ```

2. **Create virtual environment (optional but recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**

   ```bash
   pip install fastapi uvicorn
   ```

   > Add any additional dependencies used in `db.py` or `report.py`

4. **Run the server**

   ```bash
   uvicorn app:app --reload
   ```

5. **Open in browser**

   * API Base: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   * Frontend: [http://127.0.0.1:8000/frontend](http://127.0.0.1:8000/frontend)

---

## 🌐 API Endpoints

### Root

```
GET /
```

Serves the frontend `index.html` file.

---

### Generate Student Report

```
GET /report/{student_id}
```

#### Path Parameters

| Name       | Type | Description               |
| ---------- | ---- | ------------------------- |
| student_id | int  | Unique student identifier |

#### Response Structure

```json
{
  "student_name": "John Doe",
  "exercise": {
    "summary": "Overall exercise summary",
    "latest": "Latest exercise report",
    "ai_feedback": "AI feedback for exercise"
  },
  "pool": {
    "summary": "Overall pool summary",
    "latest": "Latest pool report",
    "ai_feedback": "AI feedback for pool"
  }
}
```

---

## 🧠 Internal Modules

### `db.py`

* `fetch_student_activities(student_id, pool=False)`
* `get_student_name(student_id)`

Handles database operations and student activity retrieval.

---

### `report.py`

* `calculate_overall_stats()`
* `get_latest_drill()`
* `generate_overall_summary()`
* `generate_latest_report()`
* `generate_ai_feedback()`

Responsible for data analysis, summarization, and AI feedback generation.

---

## 🔐 CORS Configuration

CORS is enabled for:

* `http://localhost`
* `http://127.0.0.1:8000`

This allows frontend-backend communication during development.

---

## 🖼️ Static Files

* Static assets are served under `/frontend`
* Favicon is available at `/favicon.ico`

---

## ❗ Error Handling

* Returns **500 Internal Server Error** for unexpected failures
* Error details are returned in the response body

---

## 📌 Future Enhancements (Optional)

* Authentication & authorization
* Pagination for activity history
* Export reports as PDF
* Admin dashboard
* Deployment using Docker

---

## 👤 Author

**Abdul Rahiman Jasbeer**

---