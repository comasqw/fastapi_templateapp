import httpx
from starlette.exceptions import HTTPException


class HTTPMethods:
    GET = "get"
    POST = "post"


class AsyncRequestsManager:
    def __init__(self, whitelist_urls: list[str] = None):
        self.whitelist_urls = whitelist_urls or []

    async def _send_request(self, url: str, method: str, data: dict | None = None) -> httpx.Response:
        try:
            async with httpx.AsyncClient() as client:
                if method == HTTPMethods.GET:
                    response = await client.get(url, params=data)
                elif method == HTTPMethods.POST:
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
