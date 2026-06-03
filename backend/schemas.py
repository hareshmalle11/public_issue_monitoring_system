from pydantic import BaseModel, Field


class ComplaintPredictRequest(BaseModel):
    complaint_text: str = Field(..., min_length=3)


class ComplaintPrediction(BaseModel):
    category: str
    priority: str
    category_confidence: float
    priority_confidence: float


class ComplaintCreateRequest(BaseModel):
    complaint_text: str = Field(..., min_length=3)
    location: str | None = None
    user_id: int


class ComplaintCreateResponse(BaseModel):
    message: str
    grievance: dict
    prediction: ComplaintPrediction


class ComplaintStatusUpdate(BaseModel):
    status: str = Field(..., min_length=2)


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: str = Field(..., min_length=5)
    phone_number: str | None = None
    password: str = Field(..., min_length=6)


class UserLoginRequest(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    phone_number: str | None = None
    created_at: str | None = None


class AuthResponse(BaseModel):
    message: str
    user: UserResponse


class AdminLoginRequest(BaseModel):
    username: str
    password: str = Field(..., min_length=6)


class AdminResponse(BaseModel):
    admin_id: int
    username: str
    email: str | None = None
    role: str | None = None
    department_id: int | None = None


class AdminAuthResponse(BaseModel):
    message: str
    admin: AdminResponse


class DepartmentCreateRequest(BaseModel):
    department_name: str = Field(..., min_length=2)


class DepartmentResponse(BaseModel):
    department_id: int
    department_name: str
    number_of_complaints: int | None = 0


class LegacyComplaintCreateResponse(BaseModel):
    message: str
    complaint_text: str
    location: str | None
    user_id: int | None
    prediction: ComplaintPrediction
