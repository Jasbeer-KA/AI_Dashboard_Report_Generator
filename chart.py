# report_generator.py
import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import sys

# DB Connection
import pymysql
from config import DB_CONFIG
from pymysql.cursors import DictCursor

def get_connection():
    return pymysql.connect(
        **DB_CONFIG,
        cursorclass=DictCursor  # set dictionary behavior here
    )

# Fetch student name
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

# Fetch table data as DataFrame
def fetch_drill_data(table_name, conn, student_id):
    if table_name == "student_activity_drills":
        join = "JOIN student_activities sa ON sa.id = d.student_activity_id"
        student_col = "sa.student_id"
    else:
        join = "JOIN student_pool_activities spa ON spa.id = d.student_pool_activity_id"
        student_col = "spa.student_id"

    query = f"""
    SELECT d.drill_type, d.drill_id, d.actual_key, d.wrong_key, d.missed_key, d.correct_key,
           d.drill_time, d.run_time, d.drill_start_date, d.drill_end_date, d.activity_drill_status
    FROM {table_name} d
    {join}
    WHERE d.activity_drill_status = 1 AND {student_col} = %s AND d.deleted_at IS NULL
    """
    try:
        df = pd.read_sql(query, conn, params=(student_id,))
        return df
    except Exception as e:
        print(f"Failed to fetch from {table_name}: {e}")
        return pd.DataFrame()

# Safe JSON to set conversion
def safe_json_to_set(x):
    if not x or x in ['null', 'None', '']:
        return set()
    try:
        parsed = json.loads(x)
        return set(parsed) if isinstance(parsed, list) else set()
    except (json.JSONDecodeError, TypeError):
        return set()

# Convert JSON columns to sets
def parse_key_fields(df):
    for key in ['actual_key', 'wrong_key', 'missed_key', 'correct_key']:
        df[key] = df[key].apply(safe_json_to_set)
    return df

# Compute counts based on sets
def compute_counts(df):
    df['actual_key_count'] = df['actual_key'].apply(len)
    df['wrong_key_count'] = df['wrong_key'].apply(len)
    df['missed_key_count'] = df['missed_key'].apply(len)
    df['correct_key_count'] = df['correct_key'].apply(len)
    return df

# Split into latest and past
def split_latest_past(df):
    df_sorted = df.sort_values('drill_end_date')
    join_cols = [col for col in df.columns if df[col].apply(lambda x: isinstance(x, set)).sum() == 0]
    df_joinable = df_sorted[join_cols]
    latest_rows = df_joinable.groupby(['drill_type', 'drill_id']).tail(1)
    past_rows = df_joinable.merge(latest_rows, how='outer', indicator=True)
    past_rows = past_rows[past_rows['_merge'] == 'left_only'].drop(columns=['_merge'])
    final_latest = df_sorted.loc[latest_rows.index]
    final_past = df_sorted.loc[past_rows.index]
    return final_latest, final_past

# Aggregate keys and counts
def aggregate_section(df):
    summary = defaultdict(float)
    key_union = defaultdict(set)
    for _, row in df.iterrows():
        for k in ['actual_key_count', 'wrong_key_count', 'missed_key_count', 'correct_key_count']:
            summary[k] += row[k]
        for key_set in ['actual_key', 'wrong_key', 'missed_key', 'correct_key']:
            if isinstance(row[key_set], set):
                key_union[key_set].update(row[key_set])
    summary.update({f"{k}_keys": sorted(list(v)) for k, v in key_union.items()})
    summary['total_key_count'] = (
        summary['actual_key_count'] +
        summary['wrong_key_count'] +
        summary['missed_key_count'] +
        summary['correct_key_count']
    )
    return summary

# Display Report
def display_report(title, data):
    print(f"\n===== {title} =====")
    for key in ['actual_key_count', 'wrong_key_count', 'missed_key_count', 'correct_key_count', 'total_key_count']:
        print(f"{key}: {data[key]}")
    for key in ['actual_key_keys', 'wrong_key_keys', 'missed_key_keys', 'correct_key_keys']:
        print(f"{key}: {data[key]}")

# Generate Bar Chart
def plot_key_counts(latest_data, past_data, student_name):
    labels = ['Actual', 'Wrong', 'Missed', 'Correct']
    latest_counts = [latest_data['actual_key_count'], latest_data['wrong_key_count'], latest_data['missed_key_count'], latest_data['correct_key_count']]
    past_counts = [past_data['actual_key_count'], past_data['wrong_key_count'], past_data['missed_key_count'], past_data['correct_key_count']]

    x = range(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots()
    ax.bar([p - width/2 for p in x], latest_counts, width, label='Latest')
    ax.bar([p + width/2 for p in x], past_counts, width, label='Past')

    ax.set_xlabel('Key Type')
    ax.set_ylabel('Count')
    ax.set_title(f'{student_name} - Key Count Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    plt.tight_layout()
    plt.show()

# === Main ===
def main():
    if len(sys.argv) < 2:
        print("Usage: python chart.py <student_id>")
        return
    student_id = sys.argv[1]

    student_name = get_student_name(student_id)
    conn = get_connection()
    df1 = fetch_drill_data('student_activity_drills', conn, student_id)
    df2 = fetch_drill_data('student_pool_activity_drills', conn, student_id)

    if df1.empty and df2.empty:
        print("No activity drill data found for the student.")
        return

    df = pd.concat([df1, df2], ignore_index=True)
    df = parse_key_fields(df)
    df = compute_counts(df)
    latest_df, past_df = split_latest_past(df)
    latest_summary = aggregate_section(latest_df)
    past_summary = aggregate_section(past_df)
    display_report(f"{student_name} - Latest Drills", latest_summary)
    display_report(f"{student_name} - Past Drills", past_summary)
    plot_key_counts(latest_summary, past_summary, student_name)

if __name__ == "__main__":
    main()
