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
    url: str = None,
    parameters: Optional[dict] = None,
    client_session: aiohttp.ClientSession = None,
    method: RequestType = RequestType.GET,
) -> dict:
    print(
        f'url : "{url}", params : "{parameters}", session : "{client_session is not None}", method : "{method.value}"'
    )

    if client_session is None:
        client_session = aiohttp.ClientSession()
    async with client_session as session:
        api_response = None
        http_method: MethodType = getattr(session, method.value)
        if parameters != None:
            response: ClientResponse = await http_method(url, params=parameters)
        else:
            response: ClientResponse = await http_method(url)
        if response.status == 200 and response.charset in [
            "application/json",
            "text/json",
            None,
        ]:
            api_response = await response.json()
            print(f"host : {response.host}")
        else:
            api_response = {
                "error": "tentative d'accès à un autre type de données qu'un fichier JSON",
                "charset": response.charset,
                "method": response.method,
            }

        return api_response


# result = asyncio.run(call_api(method=RequestType.GET, url="https://www.google.com"))
# print(result)
