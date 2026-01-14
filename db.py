import pymysql
from sqlalchemy import text
from config import DB_CONFIG
from pymysql.cursors import DictCursor

def get_connection():
    return pymysql.connect(
        **DB_CONFIG,
        cursorclass=DictCursor  # set dictionary behavior here
    )


def get_student_name(student_id):
    query = """
        SELECT u.first_name, u.last_name
        FROM students s
        JOIN users u ON s.userId = u.id
        WHERE s.id = %s
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, (student_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return f"{row['first_name']} {row['last_name']}"
    return "Student"


def fetch_student_activities(student_id, pool=False):
    table = "student_pool_activity_drills" if pool else "student_activity_drills"
    parent = "student_pool_activities" if pool else "student_activities"
    foreign_key = "student_pool_activity_id" if pool else "student_activity_id"

    query = f"""
        SELECT d.*, dt.drill_type
        FROM {table} d
        JOIN {parent} a ON d.{foreign_key} = a.id
        LEFT JOIN drill_types dt ON dt.id = d.drill_type
        WHERE a.student_id = %s AND d.activity_drill_status = 1 AND d.deleted_at IS NULL
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, (student_id,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results



def get_drill_type_name(drill_type_id: int) -> str:
    conn = get_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)  # ✅ Using DictCursor
    try:
        cur.execute("SELECT drill_type FROM drill_types WHERE id = %s", (drill_type_id,))
        result = cur.fetchone()
        return result["drill_type"] if result else f"Drill Type {drill_type_id}"
    finally:
        cur.close()
        conn.close()