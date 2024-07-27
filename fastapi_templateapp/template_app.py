from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError
import json
import httpx


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


class AsyncRequestsManager:
    def __init__(self, whitelist_urls: list = None):
        if whitelist_urls is None:
            self.whitelist_urls = []

    async def _send_request(self, url: str, method: str, data: dict | None = None) -> httpx.Response:
        try:
            async with httpx.AsyncClient() as client:
                if method == "get":
                    response = await client.get(url, params=data)
                elif method == "post":
                    response = await client.post(url, json=data)
                else:
                    raise ValueError("Invalid request method")
        except Exception as e:
            raise HTTPException(detail="Error while sending a request", status_code=500)
        else:
            return response

    async def send_request(self, url: str, method: str, data: dict | None = None) -> httpx.Response:
        if self.whitelist_urls and url not in self.whitelist_urls:
            raise HTTPException(detail=f"{url} is not in whitelist", status_code=422)

        response = await self._send_request(url, method, data)

        return response
