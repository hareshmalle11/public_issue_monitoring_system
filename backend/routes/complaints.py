<<<<<<< HEAD
=======

>>>>>>> 54b4f71bedfb02c75db5ccf0e61f06120a5cca88
from fastapi import APIRouter, HTTPException, UploadFile, File
import os
import shutil
import requests
<<<<<<< HEAD
from datetime import datetime, timezone
from uuid import uuid4

=======
from datetime import datetime, timezone
from uuid import uuid4
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException
>>>>>>> 54b4f71bedfb02c75db5ccf0e61f06120a5cca88
from schemas import (
    ComplaintCreateRequest,
    ComplaintCreateResponse,
    ComplaintPredictRequest,
    ComplaintPrediction,
    ComplaintStatusUpdate,
    ComplaintReopenRequest,
<<<<<<< HEAD
=======
)
from services.ml_predictor import get_predictor
from services.supabase_client import SupabaseRestError, supabase

router = APIRouter()

@router.post("/upload")
def upload_file(file: UploadFile = File(...)) -> dict:
    filename = f"{uuid4().hex}_{file.filename}"
    
    # Attempt Supabase Storage upload
    try:
        url = f"https://nyjyvbijrurvqvrhtnwi.supabase.co/storage/v1/object/complaint-images/{filename}"
        headers = {
            "Authorization": "Bearer sb_publishable_rPDtQCZYLdwwW9ikW9vz8w_Ky4NPAt4",
            "apikey": "sb_publishable_rPDtQCZYLdwwW9ikW9vz8w_Ky4NPAt4",
            "Content-Type": file.content_type
        }
        file.file.seek(0)
        content = file.file.read()
        res = requests.post(url, data=content, headers=headers)
        if res.status_code == 200:
            public_url = f"https://nyjyvbijrurvqvrhtnwi.supabase.co/storage/v1/object/public/complaint-images/{filename}"
            return {"image_url": public_url}
    except Exception as e:
        print(f"Warning: Supabase Storage upload failed: {e}")

    # Fallback to local file storage
    try:
        os.makedirs("static/uploads", exist_ok=True)
        local_path = os.path.join("static", "uploads", filename)
        file.file.seek(0)
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"image_url": f"http://127.0.0.1:8000/static/uploads/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Local fallback upload failed: {e}")

>>>>>>> 54b4f71bedfb02c75db5ccf0e61f06120a5cca88
)
from services.ml_predictor import get_predictor
from services.supabase_client import SupabaseRestError, supabase

router = APIRouter()

@router.post("/upload")
def upload_file(file: UploadFile = File(...)) -> dict:
    filename = f"{uuid4().hex}_{file.filename}"
    
    # Attempt Supabase Storage upload
    try:
        url = f"https://nyjyvbijrurvqvrhtnwi.supabase.co/storage/v1/object/complaint-images/{filename}"
        headers = {
            "Authorization": "Bearer sb_publishable_rPDtQCZYLdwwW9ikW9vz8w_Ky4NPAt4",
            "apikey": "sb_publishable_rPDtQCZYLdwwW9ikW9vz8w_Ky4NPAt4",
            "Content-Type": file.content_type
        }
        file.file.seek(0)
        content = file.file.read()
        res = requests.post(url, data=content, headers=headers)
        if res.status_code == 200:
            public_url = f"https://nyjyvbijrurvqvrhtnwi.supabase.co/storage/v1/object/public/complaint-images/{filename}"
            return {"image_url": public_url}
    except Exception as e:
        print(f"Warning: Supabase Storage upload failed: {e}")

    # Fallback to local file storage
    try:
        os.makedirs("static/uploads", exist_ok=True)
        local_path = os.path.join("static", "uploads", filename)
        file.file.seek(0)
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"image_url": f"http://127.0.0.1:8000/static/uploads/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Local fallback upload failed: {e}")


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
        grievance = supabase.insert(
            "grievances",
            {
                "ticket_number": generate_ticket_number(),
                "user_id": request.user_id,
<<<<<<< HEAD
=======
                "complaint_text": request.complaint_text,
                "category": prediction.category,
                "priority": prediction.priority,
                "status": "Pending",
                "locality": request.locality,
                "address": request.address,
                "landmark": request.landmark,
                "image_url": request.image_url,
                "department_id": department["department_id"],
>>>>>>> 54b4f71bedfb02c75db5ccf0e61f06120a5cca88
                "complaint_text": request.complaint_text,
                "category": prediction.category,
                "priority": prediction.priority,
                "status": "Pending",
                "locality": request.locality,
                "address": request.address,
                "landmark": request.landmark,
                "image_url": request.image_url,
                "submission_date": datetime.now(timezone.utc).isoformat(),
                "resolved_date": None,
            },
        )
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
    locality: str | None = None,
    status: str | None = None,
) -> list[dict]:
    params = {"select": "*", "order": "submission_date.desc"}

    if user_id is not None:
        params["user_id"] = f"eq.{user_id}"
<<<<<<< HEAD
    if locality is not None:
        params["locality"] = f"eq.{locality}"
=======
>>>>>>> 54b4f71bedfb02c75db5ccf0e61f06120a5cca88
    if status:
        params["status"] = f"eq.{status}"

    try:
        return supabase.select("grievances", params=params)
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
<<<<<<< HEAD

=======
>>>>>>> 54b4f71bedfb02c75db5ccf0e61f06120a5cca88
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
    # Fetch old status first for logging
    try:
        old_grievance = get_complaint(grievance_id)
        old_status = old_grievance.get("status", "Pending")
    except HTTPException:
        old_status = "Pending"
<<<<<<< HEAD
=======

    payload = {"status": request.status}
    if request.status.lower() == "resolved":
        payload["resolved_date"] = datetime.now(timezone.utc).isoformat()
    else:
        payload["resolved_date"] = None

    try:
        updated = supabase.update("grievances", "grievance_id", grievance_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Complaint not found")

        # Create log entry in officer_logs if officer_id is provided
        if request.officer_id is not None:
            try:
                supabase.insert(
                    "officer_logs",
                    {
                        "officer_id": request.officer_id,
                        "grievance_id": grievance_id,
                        "old_status": old_status,
                        "new_status": request.status,
                        "remarks": request.remarks or f"Status changed from {old_status} to {request.status}",
                        "action_time": datetime.now(timezone.utc).isoformat()
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to log officer action to database: {e}")

        return updated
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/{grievance_id}/reopen")
def reopen_complaint(grievance_id: int, request: ComplaintReopenRequest) -> dict:
    try:
        old_grievance = get_complaint(grievance_id)
        old_status = old_grievance.get("status", "Resolved")
    except HTTPException:
        old_status = "Resolved"

    payload = {
        "status": "Pending",
        "resolved_date": None
    }

    try:
        updated = supabase.update("grievances", "grievance_id", grievance_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Complaint not found")

        # Log the reopen action in officer_logs (using officer_id = 0 to signify citizen reopen)
        try:
            supabase.insert(
                "officer_logs",
                {
                    "officer_id": 0,  # 0 indicates Citizen Reopen
                    "grievance_id": grievance_id,
                    "old_status": old_status,
                    "new_status": "Pending",
                    "remarks": f"Reopened by Citizen. Reason: {request.reason}",
                    "action_time": datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as e:
            print(f"Warning: Failed to log reopen action to database: {e}")

        return updated
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    payload = {"status": request.status}
>>>>>>> 54b4f71bedfb02c75db5ccf0e61f06120a5cca88

    payload = {"status": request.status}
    if request.status.lower() == "resolved":
        payload["resolved_date"] = datetime.now(timezone.utc).isoformat()
    else:
        payload["resolved_date"] = None

    try:
        updated = supabase.update("grievances", "grievance_id", grievance_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Complaint not found")

        # Create log entry in officer_logs if officer_id is provided
        if request.officer_id is not None:
            try:
                supabase.insert(
                    "officer_logs",
                    {
                        "officer_id": request.officer_id,
                        "grievance_id": grievance_id,
                        "old_status": old_status,
                        "new_status": request.status,
                        "remarks": request.remarks or f"Status changed from {old_status} to {request.status}",
                        "action_time": datetime.now(timezone.utc).isoformat()
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to log officer action to database: {e}")

        return updated
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/{grievance_id}/reopen")
def reopen_complaint(grievance_id: int, request: ComplaintReopenRequest) -> dict:
    try:
        old_grievance = get_complaint(grievance_id)
        old_status = old_grievance.get("status", "Resolved")
    except HTTPException:
        old_status = "Resolved"

<<<<<<< HEAD
    payload = {
        "status": "Pending",
        "resolved_date": None
    }

    try:
        updated = supabase.update("grievances", "grievance_id", grievance_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Complaint not found")

        # Log the reopen action in officer_logs (using officer_id = 0 to signify citizen reopen)
        try:
            supabase.insert(
                "officer_logs",
                {
                    "officer_id": 0,  # 0 indicates Citizen Reopen
                    "grievance_id": grievance_id,
                    "old_status": old_status,
                    "new_status": "Pending",
                    "remarks": f"Reopened by Citizen. Reason: {request.reason}",
                    "action_time": datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as e:
            print(f"Warning: Failed to log reopen action to database: {e}")

        return updated
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
=======
    return updated

>>>>>>> 54b4f71bedfb02c75db5ccf0e61f06120a5cca88
