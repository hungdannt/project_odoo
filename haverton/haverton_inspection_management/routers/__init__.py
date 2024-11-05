from fastapi import APIRouter

from .inspections import router as inspections_router
from .users import router as users_router

router = APIRouter()
router.include_router(inspections_router, prefix="/inspections", tags=["inspections"])
router.include_router(users_router, prefix="/users", tags=["users"])
