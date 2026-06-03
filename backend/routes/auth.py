from fastapi import APIRouter, HTTPException

from schemas import (
    AdminAuthResponse,
    AdminLoginRequest,
    AdminResponse,
    AuthResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from services.security import hash_password, verify_password
from services.supabase_client import SupabaseRestError, supabase


router = APIRouter()


def public_user(row: dict) -> UserResponse:
    return UserResponse(
        user_id=row["user_id"],
        name=row["name"],
        email=row["email"],
        phone_number=row.get("phone_number"),
        created_at=row.get("created_at"),
    )


@router.post("/register", response_model=AuthResponse)
def register_user(request: UserRegisterRequest) -> AuthResponse:
    existing_users = supabase.select(
        "users",
        params={"email": f"eq.{request.email}", "select": "*", "limit": "1"},
    )
    if existing_users:
        raise HTTPException(status_code=409, detail="Email already registered")

    try:
        user = supabase.insert(
            "users",
            {
                "name": request.name,
                "email": request.email,
                "phone_number": request.phone_number,
                "password_hash": hash_password(request.password),
            },
        )
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AuthResponse(message="User registered successfully", user=public_user(user))


@router.post("/login", response_model=AuthResponse)
def login_user(request: UserLoginRequest) -> AuthResponse:
    users = supabase.select(
        "users",
        params={"email": f"eq.{request.email}", "select": "*", "limit": "1"},
    )
    if not users or not verify_password(request.password, users[0].get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return AuthResponse(message="Login successful", user=public_user(users[0]))


@router.post("/admin/login", response_model=AdminAuthResponse)
def login_admin(request: AdminLoginRequest) -> AdminAuthResponse:
    admins = supabase.select(
        "admins",
        params={"username": f"eq.{request.username}", "select": "*", "limit": "1"},
    )
    if not admins or not verify_password(request.password, admins[0].get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    admin = admins[0]
    return AdminAuthResponse(
        message="Admin login successful",
        admin=AdminResponse(
            admin_id=admin["admin_id"],
            username=admin["username"],
            email=admin.get("email"),
            role=admin.get("role"),
            department_id=admin.get("department_id"),
        ),
    )


@router.get("/health")
def auth_health() -> dict[str, str]:
    return {"status": "auth routes ready"}
