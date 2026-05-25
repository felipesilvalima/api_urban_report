from app.domain.services.complaint_service import ComplaintService
from fastapi import APIRouter, Depends,HTTPException
from app.infrastructure.database.connect_database import get_session
from sqlalchemy.orm import Session
from app.middleware.verify_token import verify_token
from fastapi_throttle import RateLimiter
from app.main import SECONDS_PER_DAY,REQUEST_LIMITER

limiter = RateLimiter(times=REQUEST_LIMITER, seconds=SECONDS_PER_DAY)

complaint_router = APIRouter(prefix="/api/complaint", tags=['api/complaint'], dependencies=[Depends(limiter)])

def instancia_complaint(session: Session = Depends(get_session)):
    return ComplaintService(session=session)



@complaint_router.post("/")
async def create_new_complaint(
    complaint_service: ComplaintService = Depends(instancia_complaint)
):
    return complaint_service.create_comaplaint_service()