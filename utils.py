import os
from typing import Any
import aiohttp
from flask import request


class Url:

    @property
    def api_projects(self):
        return self.root_url + "/api/projects"

    @property
    def api_gists(self):
        return self.root_url + "/api/gist_metadata"

    @property
    def api_tools(self):
        return self.root_url + "/api/tools"

    @property
    def root_url(self):
        url = os.getenv("VERCEL_PROJECT_PRODUCTION_URL", "default")
        if url == "default":
            url = request.url_root
        else:
            url = "https://" + url
        return url


async def call_api(client_session: aiohttp.ClientSession = None, url: str = None, method: str = "get", parameters: dict = {}) -> Any:
    if client_session is None:
        client_session = aiohttp.ClientSession()
    async with client_session as session:
        http_method = getattr(session, method)
        if method in dir(session) and callable(http_method):
            response = await http_method(url, params=parameters)
            if response.status == 200:
                api_response = await response.json()
                return api_response
