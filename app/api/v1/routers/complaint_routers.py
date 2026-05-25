from app.domain.services.complaint_service import ComplaintService
from app.models.models import User
from app.schema.complaintSchema import ComplaintFilterSchema, ComaplaintSchema
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
    complaintSchema: ComaplaintSchema,
    complaint_service: ComplaintService = Depends(instancia_complaint)
):
    complainted = complaint_service.create_comaplaint_service(complaintSchema)

    return complainted,201


@complaint_router.get("/")
async def list_complaiment(
    complaintFilterSchema: ComplaintFilterSchema = Depends(),
    complaint_service: ComplaintService = Depends(instancia_complaint),
    
):
    complaments = complaint_service.list_comaplaint_service(complaintFilterSchema)

    return complaments,200