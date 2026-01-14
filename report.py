# report_generator.py
from collections import defaultdict
from langchain_ollama import OllamaLLM
from db import get_student_name
from db import get_drill_type_name  

llm = OllamaLLM(model="llama3:latest")

def get_latest_drill(records):
    return records[-1] if records else None

def calculate_overall_stats(records):
    if not records:
        return None

    summary = {
        "latest": records[-1],
        "highest_wpm": max(records, key=lambda x: x["word_per_min"] or 0),
        "lowest_wpm": min(records, key=lambda x: x["word_per_min"] or 999),
        "avg_wpm": sum(r["word_per_min"] or 0 for r in records) / len(records),
        "avg_accuracy": sum(r["accuracy"] or 0 for r in records) / len(records),
        "total_drills": len(records),
        "total_keys": sum(r.get("actual_key_count") or 0 for r in records),
        "correct_keys": sum(r.get("correct_key_count") or 0 for r in records),
        "wrong_keys": sum(r.get("wrong_key_count") or 0 for r in records),
        "missed_keys": sum(r.get("missed_key_count") or 0 for r in records),
    }

    key_counts = defaultdict(int)
    for r in records:
        for key_group in ["wrong_key", "missed_key"]:
            keys = (r.get(key_group) or "").replace('[', '').replace(']', '').replace('"', '').split()
            for k in keys:
                if k.strip():
                    key_counts[k.strip()] += 1

    summary["weakest_key"] = " ".join(sorted(key_counts, key=key_counts.get, reverse=True)[:4]) if key_counts else None
    return summary

def get_skill_level(wpm, accuracy):
    if wpm >= 40 and accuracy >= 95:
        return "Advanced"
    elif wpm >= 30 and accuracy >= 85:
        return "Intermediate"
    else:
        return "Beginner"

def generate_latest_report(latest):
    if not latest:
        return "No recent drill found."

    print("DEBUG - latest record:", latest)

    skill_level = get_skill_level(latest['word_per_min'], latest['accuracy'])

    try:
        drill_type_id = latest.get("drill_type")
        drill_name = get_drill_type_name(drill_type_id) if drill_type_id else "Unknown Drill"
    except Exception as e:
        print("ERROR in get_drill_type_name:", e)
        drill_name = f"Drill ID: {drill_type_id}"

    return f"""
👩‍🏫 Latest Drill Report:
- Drill: {drill_name}
- WPM: {latest['word_per_min']:.1f} | Accuracy: {latest['accuracy']:.1f}%
- Total Keys Typed: {int(latest['actual_key_count'] or 0)}
  - Correct: {int(latest['correct_key_count'] or 0)} | Wrong: {int(latest['wrong_key_count'] or 0)} | Missed: {int(latest['missed_key_count'] or 0)}
- Weakest Keys (this drill): '{((latest.get('wrong_key') or '') + ' ' + (latest.get('missed_key') or '')).strip()}'
- Skill Level: {skill_level}
""".strip()




def generate_overall_summary(stats):
    if not stats:
        return "No overall stats available."

    return f"""
📊 Overall Performance Summary:
- Total Drills Played: {stats['total_drills']}
- Average WPM: {stats['avg_wpm']:.1f} | Average Accuracy: {stats['avg_accuracy']:.1f}%
- Highest WPM: {stats['highest_wpm']['word_per_min']:.1f} | Lowest WPM: {stats['lowest_wpm']['word_per_min']:.1f}
- Total Keys Typed: {stats['total_keys']}, Correct: {stats['correct_keys']}, Wrong: {stats['wrong_keys']}, Missed: {stats['missed_keys']}
- Most Missed/Mistyped Keys: '{stats['weakest_key']}'
- Skill Progression: {get_skill_level(stats['avg_wpm'], stats['avg_accuracy'])}
""".strip()

def generate_ai_feedback(stats, student_id, mode_name="Exercise"):
    if not stats:
        return f"No {mode_name} data available."

    student_name = get_student_name(student_id)
    prompt = f"""
You are a friendly typing coach for students aged 8–16.
Write a motivational performance feedback for {student_name}.

Drill Summary:
- Mode: {mode_name}
- Latest WPM: {stats['latest']['word_per_min']:.1f}, Accuracy: {stats['latest']['accuracy']:.1f}%
- Average WPM: {stats['avg_wpm']:.1f}, Avg Accuracy: {stats['avg_accuracy']:.1f}%
- Highest WPM: {stats['highest_wpm']['word_per_min']:.1f}, Lowest WPM: {stats['lowest_wpm']['word_per_min']:.1f}
- Weakest Key: {stats.get('weakest_key', 'None')}
- Skill Level: {get_skill_level(stats['avg_wpm'], stats['avg_accuracy'])}

Tone: Supportive, warm, friendly, under 80 words.
"""
    return llm.invoke(prompt)
