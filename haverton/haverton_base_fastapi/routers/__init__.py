from fastapi import APIRouter

from .attachments import router as attachments_router
from .auth import router as auth_router
from .general import router as general_router
from .users import router as users_router

router = APIRouter()
router.include_router(auth_router, tags=["auth"])
router.include_router(general_router, tags=["general"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(attachments_router, prefix="/attachments", tags=["attachments"])
