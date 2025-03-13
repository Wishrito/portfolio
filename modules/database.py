from pathlib import Path

import aiohttp
from flask import Blueprint

from modules.utils import Url


class Database(Blueprint):
    def __init__(
        self,
        name,
        import_name,
        static_folder=None,
        static_url_path=None,
        template_folder=None,
        url_prefix=None,
        subdomain=None,
        url_defaults=None,
        root_path=None,
        cli_group=...,
    ):
        super().__init__(
            name,
            import_name,
            static_folder,
            static_url_path,
            template_folder,
            url_prefix,
            subdomain,
            url_defaults,
            root_path,
            cli_group,
        )
        self.url = Url()


db_route = Database("db", __name__, url_prefix="/db")

db_route.template_folder = Path(__file__).parent / "pages"
db_route.static_folder = Path(__file__).parent / "src"


async def fetch_languages(session: aiohttp.ClientSession, repo_name: str):
    async with session.get(
        f"https://api.github.com/repos/Wishrito/{repo_name}/languages", timeout=5
    ) as response:
        return await response.json()


@db_route.post("/refresh")
def db_refresh(): ...
