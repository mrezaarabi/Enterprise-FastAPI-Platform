from fastapi import APIRouter
from app.api.v1.endpoints import users, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Additional endpoint modules would be included here