# api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import fetch_student_activities, get_student_name
from report_generator import (
    calculate_stats,
    generate_description,
    generate_ai_feedback
)

app = FastAPI(title="Typing Report Generator API")


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount the static folder
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Optional: Explicit route for favicon
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")


# Optional: Enable CORS if you're calling this API from a frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost","http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/report/{student_id}")
async def generate_student_report(student_id: int):
    try:
        student_name = get_student_name(student_id)

        exercise_data = fetch_student_activities(student_id, pool=False)
        exercise_stats = calculate_stats(exercise_data)
        exercise_report = generate_description(exercise_stats, "Exercise")
        exercise_ai = generate_ai_feedback(exercise_stats, student_id, "Exercise")

        pool_data = fetch_student_activities(student_id, pool=True)
        pool_stats = calculate_stats(pool_data)
        pool_report = generate_description(pool_stats, "Pool")
        pool_ai = generate_ai_feedback(pool_stats, student_id, "Pool")

        return {
            "student_name": student_name,
            "exercise": {
                "summary": exercise_report,
                "ai_feedback": exercise_ai
            },
            "pool": {
                "summary": pool_report,
                "ai_feedback": pool_ai
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")
