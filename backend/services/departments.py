from __future__ import annotations

from services.supabase_client import supabase


def get_department_by_name(department_name: str) -> dict | None:
    rows = supabase.select(
        "departments",
        params={
            "department_name": f"eq.{department_name}",
            "select": "*",
            "limit": "1",
        },
    )
    return rows[0] if rows else None


def get_or_create_department(department_name: str) -> dict:
    department = get_department_by_name(department_name)
    if department:
        return department

    return supabase.insert(
        "departments",
        {
            "department_name": department_name,
            "number_of_complaints": 0,
        },
    )


def increment_department_complaints(department: dict) -> None:
    department_id = department.get("department_id")
    current_count = int(department.get("number_of_complaints") or 0)

    if department_id is None:
        return

    supabase.update(
        "departments",
        "department_id",
        department_id,
        {"number_of_complaints": current_count + 1},
    )
