from app.domain.services.complaint_service import ComplaintService
from app.models.models import User
from app.schema.complaintSchema import ComplaintFilterSchema, ComaplaintSchema, ComplaintStatusSchema
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
    user_loggin: User = Depends(verify_token)
    
):
    complaments = complaint_service.list_comaplaint_service(complaintFilterSchema,user_loggin)

    return complaments,200


@complaint_router.get("/{complaint_id}")
async def details_complaiment(
    complaint_id: int,
    complaint_service: ComplaintService = Depends(instancia_complaint),
    user_loggin: User = Depends(verify_token)
):
    details = complaint_service.details_complaint_service(complaint_id, user_loggin)

    return details,200



@complaint_router.patch("/{complaint_id}/status")
async def status_complaiment(
    complaint_id: int,
    status: ComplaintStatusSchema,
    complaint_service: ComplaintService = Depends(instancia_complaint),
    user_loggin: User = Depends(verify_token)
):
    altered_status = complaint_service.alter_status_service(complaint_id, status.status, user_loggin)

    return altered_status,200