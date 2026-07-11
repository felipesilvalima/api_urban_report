from app.exeception.domain.domain_exeception import DomainException

class ImageNotFound(DomainException):
    def __init__(self, message, status_code:int | None = None):
        self.message = message
        self.status_code = 404
        super().__init__(self.message,self.status_code)



class ComplaintNotFound(DomainException):
    def __init__(self, message, status_code:int | None = None):
        self.message = message
        self.status_code = 404
        super().__init__(self.message,self.status_code)


class ComplaintStatusInvalid(DomainException):
    def __init__(self, message, status_code:int | None = None):
        self.message = message
        self.status_code = 404
        super().__init__(self.message,self.status_code)


class ComplaintConflict(DomainException):
    def __init__(self, message, status_code:int | None = None):
        self.message = message
        self.status_code = 409
        super().__init__(self.message,self.status_code)