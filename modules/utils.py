from enum import Enum
from types import MethodType
from typing import Optional

import aiohttp
from aiohttp import ClientResponse


class RequestType(Enum):
    POST = "post"
    GET = "get"
    PATCH = "patch"


async def call_api(
    parameters: Optional[dict] = None,
    client_session: aiohttp.ClientSession = None,
    url: str = None,
    method: RequestType = RequestType.GET,
) -> dict:
    if client_session is None:
        client_session = aiohttp.ClientSession()
    async with client_session as session:
        api_response: dict = {}
        http_method: MethodType = getattr(session, method.value)
        if parameters is not None:
            response: ClientResponse = await http_method(url, params=parameters)
        else:
            response: ClientResponse = await http_method(url)
        if response.status == 200 and response.charset in [
            "application/json",
            "text/json",
        ]:
            api_response.update(await response.json())

        api_response.update(
            {
                "error": "tentative d'accès à un autre type de données qu'un fichier JSON",
                "charset": response.charset,
                "method": response.method,
            }
        )

        return api_response


# result = asyncio.run(call_api(method=RequestType.GET, url="https://www.google.com"))
# print(result)
