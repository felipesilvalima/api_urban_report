from sqlalchemy.orm import Session
from app.infrastructure.repository.base.repository_base import RepostiroyBase
from app.models.models import User

class AuthRepository(RepostiroyBase):

    def __init__(self, session: Session):
        super().__init__(session=session,model=User)