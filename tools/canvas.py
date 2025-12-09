#!/usr/bin/env python3
"""
Canvas LMS API utilities for Rowan/Laser school monitoring.

Requires CANVAS_PAT environment variable.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional

BASE_URL = "https://canvas.instructure.com/api/v1"

def get_headers():
    pat = os.environ.get("CANVAS_PAT")
    if not pat:
        raise ValueError("CANVAS_PAT environment variable not set")
    return {"Authorization": f"Bearer {pat}"}

def api_get(endpoint: str, params: dict = None) -> dict | list:
    """Make authenticated GET request to Canvas API."""
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.get(url, headers=get_headers(), params=params or {})
    resp.raise_for_status()
    return resp.json()

def get_observees() -> list[dict]:
    """Get linked students (observees)."""
    return api_get("users/self/observees")

def get_student_courses(student_id: int, include_scores: bool = True) -> list[dict]:
    """Get courses for a student with optional grade info."""
    params = {"enrollment_state": "active"}
    if include_scores:
        params["include[]"] = ["total_scores", "current_grading_period_scores"]
    return api_get(f"users/{student_id}/courses", params)

def get_missing_submissions(student_id: int) -> list[dict]:
    """Get all missing submissions for a student."""
    return api_get(f"users/{student_id}/missing_submissions", {"include[]": "course", "per_page": 100})

def get_course_modules(course_id: int, include_items: bool = True) -> list[dict]:
    """Get modules (curriculum units) for a course."""
    params = {"per_page": 50}
    if include_items:
        params["include[]"] = "items"
    return api_get(f"courses/{course_id}/modules", params)

def get_course_assignments(course_id: int, bucket: str = None) -> list[dict]:
    """
    Get assignments for a course.
    bucket: past, overdue, undated, ungraded, unsubmitted, upcoming, future
    """
    params = {"per_page": 100}
    if bucket:
        params["bucket"] = bucket
    return api_get(f"courses/{course_id}/assignments", params)

def get_student_submissions(course_id: int, student_id: int) -> list[dict]:
    """Get all submissions for a student in a course."""
    return api_get(f"courses/{course_id}/students/submissions", {
        "student_ids[]": student_id,
        "per_page": 100
    })

def format_grade_summary(student_id: int) -> str:
    """Generate a formatted grade summary for a student."""
    courses = get_student_courses(student_id)
    lines = []

    for course in courses:
        name = course.get("name", "Unknown").strip()
        enrollments = course.get("enrollments", [])

        for enrollment in enrollments:
            if enrollment.get("type") == "student":
                current = enrollment.get("computed_current_grade", "-")
                current_pct = enrollment.get("computed_current_score")
                final = enrollment.get("computed_final_grade", "-")
                final_pct = enrollment.get("computed_final_score")

                current_str = f"{current} ({current_pct:.1f}%)" if current_pct else current
                final_str = f"{final} ({final_pct:.1f}%)" if final_pct else final

                # Flag if big gap between current and final (missing work)
                gap = ""
                if current_pct and final_pct and (current_pct - final_pct) > 10:
                    gap = " ⚠️"

                lines.append(f"  {name}: {current_str} → {final_str}{gap}")
                break

    return "\n".join(sorted(lines))

def format_missing_summary(student_id: int) -> str:
    """Generate a formatted missing assignments summary."""
    missing = get_missing_submissions(student_id)
    if not missing:
        return "  No missing assignments!"

    lines = []
    by_course = {}

    for item in missing:
        course_name = item.get("course", {}).get("name", "Unknown").strip()
        if course_name not in by_course:
            by_course[course_name] = []
        by_course[course_name].append({
            "name": item.get("name"),
            "due_at": item.get("due_at"),
            "points": item.get("points_possible", 0)
        })

    for course, assignments in sorted(by_course.items()):
        total_points = sum(a["points"] or 0 for a in assignments)
        lines.append(f"  {course} ({len(assignments)} missing, {total_points:.0f} pts):")
        for a in sorted(assignments, key=lambda x: x["due_at"] or ""):
            due = ""
            if a["due_at"]:
                due_dt = datetime.fromisoformat(a["due_at"].replace("Z", "+00:00"))
                due = f" (due {due_dt.strftime('%b %d')})"
            lines.append(f"    - {a['name']}{due}")

    return "\n".join(lines)

def format_current_week(student_id: int) -> str:
    """Get this week's curriculum modules across all courses."""
    courses = get_student_courses(student_id, include_scores=False)
    lines = []

    today = datetime.now()
    # Look for modules with current week in name
    week_patterns = [
        today.strftime("%B %d"),  # December 01
        today.strftime("%b %d"),   # Dec 01
        f"Week {(today.day - 1) // 7 + 1}",  # Week N
    ]

    for course in courses:
        course_id = course["id"]
        course_name = course.get("name", "Unknown").strip()

        try:
            modules = get_course_modules(course_id)
        except:
            continue

        # Find current/recent module (usually highest position that's not future)
        current_module = None
        for mod in modules:
            name = mod.get("name", "")
            # Check if module name contains current date range
            if any(p.lower() in name.lower() for p in week_patterns):
                current_module = mod
                break
            # Or just take the most recent one with items
            if mod.get("items"):
                current_module = mod

        if current_module:
            items = current_module.get("items", [])
            assignments = [i for i in items if i.get("type") == "Assignment"]
            if assignments:
                lines.append(f"  {course_name}:")
                lines.append(f"    Module: {current_module['name']}")
                for a in assignments[:5]:  # Limit to 5
                    lines.append(f"    - {a['title']}")

    return "\n".join(lines) if lines else "  No current week modules found"

def full_report(student_name: str = "Rowan") -> str:
    """Generate full Canvas report for a student."""
    observees = get_observees()
    student = next((o for o in observees if student_name.lower() in o["name"].lower()), None)

    if not student:
        return f"Student '{student_name}' not found. Available: {[o['name'] for o in observees]}"

    student_id = student["id"]

    report = []
    report.append(f"# Canvas Report: {student['name']}")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")

    report.append("## Current Grades")
    report.append("(Current = graded work only | Final = includes zeros for missing)")
    report.append(format_grade_summary(student_id))
    report.append("")

    report.append("## Missing Assignments")
    report.append(format_missing_summary(student_id))
    report.append("")

    report.append("## This Week's Curriculum")
    report.append(format_current_week(student_id))

    return "\n".join(report)


if __name__ == "__main__":
    import sys
    student = sys.argv[1] if len(sys.argv) > 1 else "Rowan"
    print(full_report(student))
