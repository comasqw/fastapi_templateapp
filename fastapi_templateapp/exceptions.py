from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from .template_app import validate_template_response
import os

templates_path = f"{os.path.dirname(__file__)}/templates"
templates = Jinja2Templates(directory=templates_path)


async def http_exception_handler(request: Request, exc: HTTPException) -> HTMLResponse:
    template_response = {
        "request": request,
        "content": {
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    }

    validate_template_response(template_response)
    headers = getattr(exc, "headers", None)
    return templates.TemplateResponse("errors/base_error.html", template_response,
                                      status_code=exc.status_code, headers=headers)


async def request_validation_exception_handler(request: Request,
                                               exc: RequestValidationError) -> RedirectResponse | HTMLResponse:
    form_endpoint = dict(request.query_params).get("form_endpoint")
    if form_endpoint:
        return RedirectResponse(f"{form_endpoint}?validation_errors={exc.errors()}")
    raise HTTPException(detail=f"Validation Error - {exc.errors()}", status_code=HTTP_422_UNPROCESSABLE_ENTITY)
