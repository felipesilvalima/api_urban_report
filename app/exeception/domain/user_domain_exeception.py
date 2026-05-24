from app.exeception.domain.domain_exeception import DomainException


class EmailInvalid(DomainException):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message,self.status_code)

class PasswordInvalid(DomainException):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message,self.status_code)

class PhoneInvalid(DomainException):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message,self.status_code)

class CpfInvalid(DomainException):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message,self.status_code)


class AuthNotAuthorized(DomainException):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message,self.status_code)


class AuthNotFound(DomainException):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message,self.status_code)

class AuthConflict(DomainException):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message,self.status_code)