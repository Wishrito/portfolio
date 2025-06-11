from enum import Enum
import json
import os
from types import MethodType
from typing import Any, Optional
from functools import wraps
from pathlib import Path
from flask import request, abort
import aiohttp
from aiohttp import ClientResponse


class RequestType(Enum):
    POST = "post"
    GET = "get"
    PATCH = "patch"


class JsonDictionnary(Enum):
    SKILLS = "skills"
    LANGUAGES = "languages"
    PROJECTS = "projects"
    TUTORIALS = "tutorials"
    ALL = "all"


async def get_json_data(
    static_folder: str | Path, dictionnary: JsonDictionnary = JsonDictionnary.ALL
) -> Any:
    json_path = Path(static_folder) / "data" / "wishrito-data.json"
    with open(json_path, encoding="UTF-8") as f:
        data: dict[str, Any] = json.load(f)

    if dictionnary != JsonDictionnary.ALL:
        return data.get(dictionnary.value, {})
    return data


async def call_api(
    url: str = None,
    parameters: Optional[dict] = None,
    client_session: aiohttp.ClientSession = None,
    method: RequestType = RequestType.GET,
) -> dict[str, str]:
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
        if response.status == 200:
            api_response = await response.json()
            print(f"host : {response.host}")
        else:
            api_response = {
                "error": "tentative d'accès à un autre type de données qu'un fichier JSON",
                "charset": response.charset,
                "method": response.method,
                "status": response.status,
                "url": response.url,
                "reason": response.reason,
            }

        return api_response


# result = asyncio.run(call_api(method=RequestType.GET, url="https://www.google.com"))
# print(result)

import inspect
from functools import wraps
from flask import request, abort


def require_api_key(expected_key=os.getenv("LOCAL_API_KEY")):
    def decorator(f):
        if inspect.iscoroutinefunction(f):

            @wraps(f)
            async def async_wrapper(*args, **kwargs):
                api_key = request.args.get("api_key")
                if not api_key or api_key != expected_key:
                    abort(401, description="Clé API manquante ou invalide")
                return await f(*args, **kwargs)

            return async_wrapper
        else:

            @wraps(f)
            def sync_wrapper(*args, **kwargs):
                api_key = request.args.get("api_key")
                if not api_key or api_key != expected_key:
                    abort(401, description="Clé API manquante ou invalide")
                return f(*args, **kwargs)

            return sync_wrapper

    return decorator
