from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from schemas import (
    ComplaintCreateRequest,
    ComplaintCreateResponse,
    ComplaintPredictRequest,
    ComplaintPrediction,
    ComplaintStatusUpdate,
)
from services.departments import get_or_create_department, increment_department_complaints
from services.ml_predictor import get_predictor
from services.supabase_client import SupabaseRestError, supabase


router = APIRouter()


def generate_ticket_number() -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = uuid4().hex[:6].upper()
    return f"PI-{today}-{suffix}"


@router.post("/predict", response_model=ComplaintPrediction)
def predict_complaint(request: ComplaintPredictRequest) -> ComplaintPrediction:
    try:
        prediction = get_predictor().predict(request.complaint_text)
        return ComplaintPrediction(**prediction)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        ) from exc


@router.post("/", response_model=ComplaintCreateResponse)
def create_complaint(request: ComplaintCreateRequest) -> ComplaintCreateResponse:
    prediction = predict_complaint(
        ComplaintPredictRequest(complaint_text=request.complaint_text)
    )

    try:
        department = get_or_create_department(prediction.category)
        grievance = supabase.insert(
            "grievances",
            {
                "ticket_number": generate_ticket_number(),
                "user_id": request.user_id,
                "department_id": department["department_id"],
                "complaint_text": request.complaint_text,
                "location": request.location,
                "priority": prediction.priority,
                "status": "Pending",
                "submission_date": datetime.now(timezone.utc).isoformat(),
                "resolved_date": None,
            },
        )
        increment_department_complaints(department)
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ComplaintCreateResponse(
        message="Complaint saved and predicted successfully",
        grievance=grievance,
        prediction=prediction,
    )


@router.get("/health")
def complaints_health() -> dict[str, str]:
    return {"status": "complaints routes ready"}


@router.get("/")
def list_complaints(
    user_id: int | None = None,
    department_id: int | None = None,
    status: str | None = None,
) -> list[dict]:
    params = {"select": "*", "order": "submission_date.desc"}

    if user_id is not None:
        params["user_id"] = f"eq.{user_id}"
    if department_id is not None:
        params["department_id"] = f"eq.{department_id}"
    if status:
        params["status"] = f"eq.{status}"

    try:
        return supabase.select("grievances", params=params)
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{grievance_id}")
def get_complaint(grievance_id: int) -> dict:
    rows = supabase.select(
        "grievances",
        params={"grievance_id": f"eq.{grievance_id}", "select": "*", "limit": "1"},
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return rows[0]


@router.patch("/{grievance_id}/status")
def update_complaint_status(
    grievance_id: int,
    request: ComplaintStatusUpdate,
) -> dict:
    payload = {"status": request.status}

    if request.status.lower() == "resolved":
        payload["resolved_date"] = datetime.now(timezone.utc).isoformat()

    try:
        updated = supabase.update("grievances", "grievance_id", grievance_id, payload)
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not updated:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return updated
