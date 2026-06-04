from fastapi import APIRouter, HTTPException
<<<<<<< HEAD
from services.supabase_client import SupabaseRestError, supabase

router = APIRouter()

@router.get("/summary")
def dashboard_summary(locality: str | None = None) -> dict:
    try:
        if locality:
            # Query grievances for specific locality
            grievances = supabase.select("grievances", params={"locality": f"eq.{locality}"})
        else:
            # Query all grievances globally
            grievances = supabase.select("grievances")
            
        total = len(grievances)
        pending = len([g for g in grievances if g.get("status") == "Pending"])
        in_progress = len([g for g in grievances if g.get("status") == "In Progress"])
        resolved = len([g for g in grievances if g.get("status") == "Resolved"])
        rejected = len([g for g in grievances if g.get("status") == "Rejected"])
        high_priority = len([g for g in grievances if g.get("priority") == "High"])

        # Calculate average rating for resolved grievances in this locality
        avg_rating = 0.0
        resolved_ids = [g["grievance_id"] for g in grievances if g.get("status") == "Resolved"]
        if resolved_ids:
            try:
                feedbacks = supabase.select("feedback")
                locality_feedbacks = [f for f in feedbacks if f["grievance_id"] in resolved_ids]
                if locality_feedbacks:
                    avg_rating = round(sum(f["rating"] for f in locality_feedbacks) / len(locality_feedbacks), 2)
            except Exception as e:
                print(f"Warning: Failed to fetch ratings for summary calculation: {e}")

        # Calculate reopened complaints (grievances having Resolved -> Pending status transition log)
        reopened_count = 0
        try:
            reopen_logs = supabase.select("officer_logs", params={"old_status": "eq.Resolved", "new_status": "eq.Pending"})
            g_ids = {g["grievance_id"] for g in grievances}
            reopened_count = len({log["grievance_id"] for log in reopen_logs if log["grievance_id"] in g_ids})
        except Exception as e:
            print(f"Warning: Failed to fetch reopen logs for summary calculation: {e}")

=======

from schemas import DepartmentCreateRequest, DepartmentResponse
from services.supabase_client import SupabaseRestError, supabase


router = APIRouter()


@router.get("/summary")
def dashboard_summary() -> dict:
    try:
        grievances = supabase.select("grievances", params={"select": "*"})
        departments = supabase.select("departments", params={"select": "*"})
>>>>>>> 80059c2b04c7ac3595f5aa0c1ea637f596fe3064
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
<<<<<<< HEAD
        "total_complaints": total,
        "pending_complaints": pending,
        "in_progress_complaints": in_progress,
        "resolved_complaints": resolved,
        "rejected_complaints": rejected,
        "high_priority_complaints": high_priority,
        "average_rating": avg_rating,
        "reopened_complaints": reopened_count
    }

@router.get("/departments")
def list_departments() -> list[dict]:
    # Keeping this for backend routing compatibility, but selecting all categories
    return [
        {"department_id": 3, "department_name": "Water"},
        {"department_id": 4, "department_name": "Roads"},
        {"department_id": 1, "department_name": "Electricity"},
        {"department_id": 5, "department_name": "Sanitation"},
        {"department_id": 6, "department_name": "Drainage"},
        {"department_id": 2, "department_name": "Traffic"},
        {"department_id": 7, "department_name": "Public Property"},
        {"department_id": 8, "department_name": "Environment"}
    ]
=======
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
>>>>>>> 80059c2b04c7ac3595f5aa0c1ea637f596fe3064
