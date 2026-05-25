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