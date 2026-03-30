from fastapi import APIRouter
from app.api.v1 import auth, contracts, operator

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(contracts.router)
router.include_router(operator.router)
