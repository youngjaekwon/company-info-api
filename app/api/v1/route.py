from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.company import router as company_router

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

router.include_router(company_router)
router.include_router(admin_router)
