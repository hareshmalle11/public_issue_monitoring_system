from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, complaints, dashboard, users


app = FastAPI(
    title="Public Issue Monitoring System API",
    description="Backend API for complaints, users, dashboard data, and ML predictions.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(complaints.router, prefix="/api/complaints", tags=["Complaints"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Public Issue Monitoring System API is running",
        "docs": "/docs",
    }
