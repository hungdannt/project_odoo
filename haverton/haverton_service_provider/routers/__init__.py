from fastapi import APIRouter

from .clients import router as clients_router
from .service_providers import router as service_providers_router

router = APIRouter()


router.include_router(clients_router,
                      prefix="/clients", tags=["clients"])
router.include_router(service_providers_router,
                      prefix="/service_providers", tags=["service_providers"])
