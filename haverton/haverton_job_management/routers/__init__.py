from fastapi import APIRouter

from .activities import router as activities_router
from .defects import router as defects_router
from .jobs import router as jobs_router
from .users import router as users_router
from .variations import router as variations_router
from .todo import router as todo

router = APIRouter()
router.include_router(todo, prefix="/todo", tags=["todo"])
router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
router.include_router(
    activities_router, prefix="/activities", tags=["activities"])
router.include_router(
    defects_router, prefix="/defects", tags=["defects"])
router.include_router(
    variations_router, prefix="/variations", tags=["variations"])
router.include_router(
    users_router, prefix="/users", tags=["users"])
