from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from schemas import FeedbackCreateRequest, FeedbackResponse
from services.supabase_client import SupabaseRestError, supabase

router = APIRouter()

def to_feedback_response(row: dict) -> FeedbackResponse:
    return FeedbackResponse(
        feedback_id=row.get("feedback_id"),
        grievance_id=row["grievance_id"],
        user_id=row["user_id"],
        rating=row["rating"],
        feedback_text=row.get("feedback_text"),
        image_url=row.get("image_url"),
        submitted_at=row.get("submitted_at")
    )

@router.post("", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackCreateRequest) -> FeedbackResponse:
    # Check if feedback already exists for this grievance
    existing = supabase.select(
        "feedback",
        params={"grievance_id": f"eq.{request.grievance_id}", "limit": "1"}
    )
    if existing:
        raise HTTPException(status_code=409, detail="Feedback already submitted for this grievance")

    try:
        row = supabase.insert(
            "feedback",
            {
                "grievance_id": request.grievance_id,
                "user_id": request.user_id,
                "rating": request.rating,
                "feedback_text": request.feedback_text,
                "image_url": request.image_url,
                "submitted_at": datetime.now(timezone.utc).isoformat()
            }
        )
        return to_feedback_response(row)
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/{grievance_id}", response_model=FeedbackResponse)
def get_feedback(grievance_id: int) -> FeedbackResponse:
    rows = supabase.select(
        "feedback",
        params={"grievance_id": f"eq.{grievance_id}", "limit": "1"}
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Feedback not found for this grievance")
    return to_feedback_response(rows[0])
