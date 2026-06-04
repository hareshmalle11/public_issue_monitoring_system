from fastapi import APIRouter, HTTPException
<<<<<<< HEAD
from datetime import datetime, timezone

from schemas import (
=======

from schemas import (
    AdminAuthResponse,
    AdminLoginRequest,
    AdminResponse,
>>>>>>> 80059c2b04c7ac3595f5aa0c1ea637f596fe3064
    AuthResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
<<<<<<< HEAD
    OfficerRegisterRequest,
    OfficerLoginRequest,
    OfficerResponse,
    OfficerUpdateRequest,
    OfficerAuthResponse,
=======
>>>>>>> 80059c2b04c7ac3595f5aa0c1ea637f596fe3064
)
from services.security import hash_password, verify_password
from services.supabase_client import SupabaseRestError, supabase

<<<<<<< HEAD
router = APIRouter()

=======

router = APIRouter()


>>>>>>> 80059c2b04c7ac3595f5aa0c1ea637f596fe3064
def public_user(row: dict) -> UserResponse:
    return UserResponse(
        user_id=row["user_id"],
        name=row["name"],
        email=row["email"],
        phone_number=row.get("phone_number"),
        created_at=row.get("created_at"),
    )

<<<<<<< HEAD
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

# --- CITIZEN AUTH ---
=======
>>>>>>> 80059c2b04c7ac3595f5aa0c1ea637f596fe3064

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

<<<<<<< HEAD
=======

>>>>>>> 80059c2b04c7ac3595f5aa0c1ea637f596fe3064
@router.post("/login", response_model=AuthResponse)
def login_user(request: UserLoginRequest) -> AuthResponse:
    users = supabase.select(
        "users",
        params={"email": f"eq.{request.email}", "select": "*", "limit": "1"},
    )
    if not users or not verify_password(request.password, users[0].get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return AuthResponse(message="Login successful", user=public_user(users[0]))

<<<<<<< HEAD
# --- OFFICER AUTH ---

@router.post("/officer/register", response_model=OfficerAuthResponse)
def register_officer(request: OfficerRegisterRequest) -> OfficerAuthResponse:
    existing = supabase.select(
        "officers",
        params={"username": f"eq.{request.username}", "select": "*", "limit": "1"}
    )
    if existing:
        raise HTTPException(status_code=409, detail="Username already registered")

    try:
        officer = supabase.insert(
            "officers",
            {
                "officer_name": request.officer_name,
                "username": request.username,
                "email": request.email,
                "password_hash": hash_password(request.password),
                "locality": request.locality,
                "is_active": request.is_active if request.is_active is not None else True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        )
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return OfficerAuthResponse(
        message="Officer registered successfully",
        officer=to_officer_response(officer)
    )

@router.post("/officer/login", response_model=OfficerAuthResponse)
def login_officer(request: OfficerLoginRequest) -> OfficerAuthResponse:
    officers = supabase.select(
        "officers",
        params={"username": f"eq.{request.username}", "select": "*", "limit": "1"}
    )
    if not officers or not verify_password(request.password, officers[0].get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return OfficerAuthResponse(
        message="Officer login successful",
        officer=to_officer_response(officers[0])
    )

# CRUD routes moved to routes/officers.py
=======

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
>>>>>>> 80059c2b04c7ac3595f5aa0c1ea637f596fe3064
