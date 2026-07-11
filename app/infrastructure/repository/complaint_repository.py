from datetime import datetime
from sqlalchemy.orm import Session
from app.infrastructure.repository.base.repository_base import RepostiroyBase
from app.models.models import Complaint

class ComplaintRepository(RepostiroyBase):

    def __init__(self, session: Session):
        super().__init__(session=session,model=Complaint)

    def search_cpf(self, cpf: str):
       cpf = self.filter_repository([Complaint.cpf == cpf]).first()

       if cpf:
           return cpf

       return False

    def count_by_cpf_today(self, cpf: str) -> int:
        start_of_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        return self.filter_repository([
            Complaint.cpf == cpf,
            Complaint.created_at >= start_of_today,
        ]).count()


    def search_complaint(self, complaint_id: int):
       complaint = self.filter_repository([Complaint.id == complaint_id]).first()

       if complaint:
           return complaint
       
       return False