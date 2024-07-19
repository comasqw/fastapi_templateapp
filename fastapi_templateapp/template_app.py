from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError


class FormEndpoint(BaseModel):
    form_endpoint: str | None = None


class TemplateContentModel(BaseModel):
    request: Request
    content: dict

    class Config:
        arbitrary_types_allowed = True


def validate_template_response(template_response: dict):
    try:
        TemplateContentModel(**template_response)
    except ValidationError as e:
        raise HTTPException(detail=str(e), status_code=500)


class TemplateApp(FastAPI):

    def __init__(self):
        from .exceptions import http_exception_handler, request_validation_exception_handler

        exception_handlers = {
            HTTPException: http_exception_handler,
            RequestValidationError: request_validation_exception_handler
        }

        super().__init__(docs_url=None,
                         redoc_url=None,
                         default_response_class=HTMLResponse,
                         exception_handlers=exception_handlers)

