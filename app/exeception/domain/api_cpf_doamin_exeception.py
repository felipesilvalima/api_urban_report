
from app.exeception.domain.domain_exeception import DomainException

class CpfNotFound(DomainException):
    def __init__(self, message, status_code:int | None = None):
        self.message = message
        self.status_code = 404
        super().__init__(self.message,self.status_code)


class CpfNotAuthorized(DomainException):
    def __init__(self, message, status_code:int | None = None):
        self.message = message
        self.status_code = 403
        super().__init__(self.message,self.status_code)