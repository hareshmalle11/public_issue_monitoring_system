from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from schemas import (
    OfficerRegisterRequest,
    OfficerResponse,
    OfficerUpdateRequest,
)
from services.security import hash_password
from services.supabase_client import SupabaseRestError, supabase

router = APIRouter()

def to_officer_response(row: dict) -> OfficerResponse:
    return OfficerResponse(
        officer_id=row["officer_id"],
        officer_name=row["officer_name"],
        username=row["username"],
        email=row["email"],
        locality=row["locality"],
        is_active=row.get("is_active", True),
        created_at=row.get("created_at"),
    )

@router.get("", response_model=list[OfficerResponse])
def list_officers() -> list[OfficerResponse]:
    try:
        rows = supabase.select("officers", params={"order": "officer_id.desc"})
        return [to_officer_response(r) for r in rows]
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("", response_model=OfficerResponse)
def create_officer(request: OfficerRegisterRequest) -> OfficerResponse:
    existing = supabase.select(
        "officers",
        params={"username": f"eq.{request.username}", "select": "*", "limit": "1"}
    )
    if existing:
        raise HTTPException(status_code=409, detail="Username already registered")
        
    try:
        row = supabase.insert(
            "officers",
            {
                "officer_name": request.officer_name,
                "username": request.username,
                "email": request.email,
                "password_hash": hash_password(request.password),
                "locality": request.locality,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        )
        return to_officer_response(row)
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.patch("/{officer_id}", response_model=OfficerResponse)
def update_officer(officer_id: int, request: OfficerUpdateRequest) -> OfficerResponse:
    payload = {}
    if request.username is not None:
        payload["username"] = request.username
    if request.password is not None:
        payload["password_hash"] = hash_password(request.password)
    if request.locality is not None:
        payload["locality"] = request.locality

    if not payload:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    try:
        updated = supabase.update("officers", "officer_id", officer_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Officer not found")
        return to_officer_response(updated)
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.delete("/{officer_id}")
def delete_officer(officer_id: int) -> dict:
    try:
        deleted = supabase.delete("officers", "officer_id", officer_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Officer not found")
        return {"message": "Officer deleted successfully", "deleted_count": len(deleted)}
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
