# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from db import fetch_student_activities, get_student_name
from report import (
    calculate_overall_stats, 
    get_latest_drill,
    generate_overall_summary,
    generate_latest_report,
    generate_ai_feedback
)

app = FastAPI(title="Typing Report Generator API")

# Mount the static folder
app.mount("/frontend", StaticFiles(directory="static", html=True), name="static")

# Favicon route
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")

@app.get("/report/{student_id}")
async def generate_student_report(student_id: int):
    try:
        student_name = get_student_name(student_id)

        # --- Exercise mode ---
        exercise_data = fetch_student_activities(student_id, pool=False)
        latest_exercise = get_latest_drill(exercise_data)
        exercise_stats = calculate_overall_stats(exercise_data)
        exercise_summary = generate_overall_summary(exercise_stats)
        exercise_latest = generate_latest_report(latest_exercise)
        exercise_ai = generate_ai_feedback(exercise_stats, student_id, "Exercise")

        # --- Pool mode ---
        pool_data = fetch_student_activities(student_id, pool=True)
        latest_pool = get_latest_drill(pool_data)
        pool_stats = calculate_overall_stats(pool_data)
        pool_summary = generate_overall_summary(pool_stats)
        pool_latest = generate_latest_report(latest_pool)
        pool_ai = generate_ai_feedback(pool_stats, student_id, "Pool")

        return {
            "student_name": student_name,
            "exercise": {
                "summary": exercise_summary,
                "latest": exercise_latest,
                "ai_feedback": exercise_ai
            },
            "pool": {
                "summary": pool_summary,
                "latest": pool_latest,
                "ai_feedback": pool_ai
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
