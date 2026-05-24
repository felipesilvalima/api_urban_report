from app.exeception.domain.domain_exeception import DomainException


class ValidationError(DomainException):
    def __init__(self, message, status_code:int | None = None):
        self.message = message
        self.status_code = 400
        super().__init__(self.message,self.status_code)

class InternalError(DomainException):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message,self.status_code)

class LimitRate(DomainException):
    def __init__(self, message):
        self.message = message
        self.status_code = 429
        super().__init__(self.message,self.status_code)


class CepNotFound(DomainException):
    def __init__(self, message, status_code:int | None = None):
        self.message = message
        self.status_code = 404
        super().__init__(self.message,self.status_code)

