from fastapi import APIRouter, HTTPException

from schemas import UserResponse
from services.supabase_client import SupabaseRestError, supabase


router = APIRouter()


def to_user_response(row: dict) -> UserResponse:
    return UserResponse(
        user_id=row["user_id"],
        name=row["name"],
        email=row["email"],
        phone_number=row.get("phone_number"),
        created_at=row.get("created_at"),
    )


@router.get("/", response_model=list[UserResponse])
def list_users() -> list[UserResponse]:
    try:
        rows = supabase.select("users", params={"select": "*", "order": "user_id.desc"})
        return [to_user_response(row) for row in rows]
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/health")
def users_health() -> dict[str, str]:
    return {"status": "users routes ready"}


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int) -> UserResponse:
    rows = supabase.select(
        "users",
        params={"user_id": f"eq.{user_id}", "select": "*", "limit": "1"},
    )
    if not rows:
        raise HTTPException(status_code=404, detail="User not found")

    return to_user_response(rows[0])
