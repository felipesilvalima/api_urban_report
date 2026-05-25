
from app.infrastructure.repository.complaint_repository import ComplaintRepository
from sqlalchemy.orm import Session


class ComplaintService:
    def __init__(self, session: Session):
        self.complaint_repository = ComplaintRepository(session=session)


    def create_comaplaint_service(self):
        return True
