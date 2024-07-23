from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from .template_app import validate_template_response
import os
from pydantic import BaseModel
from typing import Dict, Tuple

templates_path = f"{os.path.dirname(__file__)}/templates"
templates = Jinja2Templates(directory=templates_path)


def redirect_with_validation_errors(endpoint, data, status_code=422):
    return RedirectResponse(f"{endpoint}?validation_errors={data}", status_code=status_code)


class ErrorsTemplateModel(BaseModel):
    errors_templates: Dict[int | str, Tuple[Jinja2Templates, str]]

    class Config:
        arbitrary_types_allowed = True


class TemplateAppExceptions:

    def __init__(self, errors_templates: dict = None):

        if errors_templates is None:
            self.errors_templates = {
                "base_error": (templates, "errors/base_error.html"),
            }
        else:
            ErrorsTemplateModel(errors_templates=errors_templates)
            self.errors_templates = errors_templates

    def update_errors_templates(self, new_errors_templates: dict):
        ErrorsTemplateModel(errors_templates=new_errors_templates)
        self.errors_templates.update(new_errors_templates)

    async def http_exception_handler(self, request: Request, exc: HTTPException) -> HTMLResponse:
        status_code = exc.status_code
        template_response = {
            "request": request,
            "content": {
                "detail": exc.detail,
                "status_code": status_code
            }
        }

        validate_template_response(template_response)
        headers = getattr(exc, "headers", None)

        template = self.errors_templates.get(status_code, self.errors_templates.get("base_error"))

        return template[0].TemplateResponse(template[1], template_response,
                                            status_code=status_code, headers=headers)

    @staticmethod
    async def handle_validation_error_get_request(request, exc) -> RedirectResponse:
        request_query_params = dict(request.query_params)
        form_endpoint = request_query_params.get("form_endpoint")
        if form_endpoint:
            redirect_query_params = {"errors": exc.errors(), "data": request_query_params}
            return redirect_with_validation_errors(form_endpoint, redirect_query_params)

    @staticmethod
    async def handle_validation_error_post_request(request, exc) -> RedirectResponse | HTMLResponse:
        request_headers = request.headers
        request_content_type = request_headers.get("content-type")
        request_referer_endpoint = request_headers.get("referer")

        if request_referer_endpoint:
            data = {}
            if request_content_type in ["application/x-www-form-urlencoded", "multipart/form-data"]:
                data = dict(await request.form())
            elif request_content_type == "application/json":
                data = await request.json()

            redirect_query_params = {"errors": exc.errors(), "data": data}
            return redirect_with_validation_errors(request_referer_endpoint, redirect_query_params, status_code=303)

    async def request_validation_exception_handler(self, request: Request,
                                                   exc: RequestValidationError) -> RedirectResponse | HTMLResponse:
        request_method = request.method
        response = None

        if request_method == "GET":
            response = await self.handle_validation_error_get_request(request, exc)
        elif request_method == "POST":
            response = await self.handle_validation_error_post_request(request, exc)

        if response:
            return response

        raise HTTPException(detail=f"Validation Error - {exc.errors()}", status_code=HTTP_422_UNPROCESSABLE_ENTITY)
