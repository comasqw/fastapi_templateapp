from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError
import json


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


def validation_errors_parser(validation_errors: None | str) -> dict:
    try:
        if validation_errors:
            validation_errors = validation_errors.replace("'", '"').replace("(", "[").replace(")", "]")
            return json.loads(validation_errors)
    except:
        raise HTTPException(detail="Invalid validation errors", status_code=422)


class TemplateApp(FastAPI):

    def __init__(self):
        from .exceptions import TemplateAppExceptions

        self.exceptions = TemplateAppExceptions()

        exception_handlers = {
            HTTPException: self.exceptions.http_exception_handler,
            RequestValidationError: self.exceptions.request_validation_exception_handler
        }

        super().__init__(docs_url=None,
                         redoc_url=None,
                         default_response_class=HTMLResponse,
                         exception_handlers=exception_handlers)

    def update_errors_templates(self, new_errors_templates: dict):
        self.exceptions.update_errors_templates(new_errors_templates)
