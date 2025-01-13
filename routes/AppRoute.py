from fastapi import APIRouter, Depends
from controllers import UserController
from security import AuthController

router = APIRouter()

router.include_router(UserController.router, prefix="/user", tags=["user"])
router.include_router(AuthController.router, prefix="/auth", tags=["auth"])
