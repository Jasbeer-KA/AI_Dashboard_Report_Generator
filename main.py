from db import fetch_student_activities, get_student_name
from report_generator import (
    calculate_stats,
    generate_description,
    generate_ai_feedback
)

def generate_student_report(student_id):
    # Fetch student name from DB
    student_name = get_student_name(student_id)

    # EXERCISE mode
    exercise_data = fetch_student_activities(student_id, pool=False)
    exercise_stats = calculate_stats(exercise_data)
    exercise_report = generate_description(exercise_stats, "Exercise")
    exercise_ai = generate_ai_feedback(exercise_stats, student_id, "Exercise")

    # POOL mode
    pool_data = fetch_student_activities(student_id, pool=True)
    pool_stats = calculate_stats(pool_data)
    pool_report = generate_description(pool_stats, "Pool")
    pool_ai = generate_ai_feedback(pool_stats, student_id, "Pool")

    # Display Reports
    print(f"\n============== TYPING REPORT for {student_name} ==============")
    print("📊 Exercise Mode Summary:\n" + exercise_report)
    print("🤖 AI Feedback (Exercise):\n" + exercise_ai)
    print("\n")
    print("📊 Pool Mode Summary:\n" + pool_report)
    print("🤖 AI Feedback (Pool):\n" + pool_ai)

if __name__ == "__main__":
    student_id = int(input("Enter Student ID: "))
    generate_student_report(student_id)

