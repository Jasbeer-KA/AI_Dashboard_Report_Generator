from collections import defaultdict
from langchain_ollama import OllamaLLM
from db import get_student_name  # Update this import path if needed

# Initialize the LLM (Ollama)
llm = OllamaLLM(model="llama3:latest")

def calculate_stats(records):
    if not records:
        return None

    summary = {
        "latest": records[-1],
        "highest_wpm": max(records, key=lambda x: x["word_per_min"] or 0),
        "lowest_wpm": min(records, key=lambda x: x["word_per_min"] or 999),
        "avg_wpm": sum(r["word_per_min"] or 0 for r in records) / len(records),
        "avg_accuracy": sum(r["accuracy"] or 0 for r in records) / len(records),
    }

    key_counts = defaultdict(int)
    for r in records:
        for k in (r["wrong_key"] or "").split(","):
            if k.strip():
                key_counts[k.strip()] += 1
        for k in (r["missed_key"] or "").split(","):
            if k.strip():
                key_counts[k.strip()] += 1

    summary["weakest_key"] = max(key_counts, key=key_counts.get) if key_counts else None
    return summary

def generate_description(stats, mode_name="Exercise"):
    if not stats:
        return f"No {mode_name} data available."

    latest = stats["latest"]
    desc = (
        f"{mode_name} Report:\n"
        f"- Played drill: {latest['drill_type']}.\n"
        f"- WPM (Latest): {latest['word_per_min']:.1f}, Accuracy: {latest['accuracy']:.1f}%\n"
        f"- Average WPM: {stats['avg_wpm']:.1f}, Accuracy: {stats['avg_accuracy']:.1f}%\n"
        f"- Highest WPM: {stats['highest_wpm']['word_per_min']:.1f}, "
        f"Lowest WPM: {stats['lowest_wpm']['word_per_min']:.1f}\n"
    )

    if stats["weakest_key"]:
        desc += f"- Weakest key: '{stats['weakest_key']}' — frequently missed or mistyped.\n"

    return desc.strip()

def generate_ai_feedback(stats, student_id, mode_name="Exercise"):
    if not stats:
        return f"No {mode_name} data available."

    # Fetch the student's full name
    student_name = get_student_name(student_id)

    prompt = (
        f"You are a friendly typing coach for students aged 8–16.\n"
        f"Write a short, motivational performance report for {student_name} based on this data:\n"
        f"- Drill: {stats['latest']['drill_type']}\n"
        f"- WPM (Latest): {stats['latest']['word_per_min']:.1f}, Accuracy: {stats['latest']['accuracy']:.1f}%\n"
        f"- Average WPM: {stats['avg_wpm']:.1f}, Avg Accuracy: {stats['avg_accuracy']:.1f}%\n"
        f"- Highest WPM: {stats['highest_wpm']['word_per_min']:.1f}, "
        f"Lowest WPM: {stats['lowest_wpm']['word_per_min']:.1f}\n"
        f"- Weakest Key: {stats.get('weakest_key', 'None')}\n\n"
        f"Tone: Friendly and supportive. Length: under 80 words."
    )

    return llm.invoke(prompt)
