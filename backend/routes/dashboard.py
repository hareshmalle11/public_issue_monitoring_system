from fastapi import APIRouter, HTTPException

from schemas import DepartmentCreateRequest, DepartmentResponse
from services.supabase_client import SupabaseRestError, supabase


router = APIRouter()


@router.get("/summary")
def dashboard_summary() -> dict:
    try:
        grievances = supabase.select("grievances", params={"select": "*"})
        departments = supabase.select("departments", params={"select": "*"})
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "total_complaints": len(grievances),
        "open_complaints": len([row for row in grievances if row.get("status") != "Resolved"]),
        "resolved_complaints": len([row for row in grievances if row.get("status") == "Resolved"]),
        "departments": departments,
    }


@router.get("/departments", response_model=list[DepartmentResponse])
def list_departments() -> list[DepartmentResponse]:
    rows = supabase.select("departments", params={"select": "*", "order": "department_id.asc"})
    return [DepartmentResponse(**row) for row in rows]


@router.post("/departments", response_model=DepartmentResponse)
def create_department(request: DepartmentCreateRequest) -> DepartmentResponse:
    row = supabase.insert(
        "departments",
        {"department_name": request.department_name, "number_of_complaints": 0},
    )
    return DepartmentResponse(**row)
