from fastapi import Request
from fastapi.responses import JSONResponse
from app.exeception.domain.domain_exeception import DomainException


def register_exception_handlers(app):
    app.add_exception_handler(DomainException, domain_exception_handler)


async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message
        }
    )