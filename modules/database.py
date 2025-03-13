from pathlib import Path

import aiohttp

from .classes import Database

db_bp = Database("db", __name__, url_prefix="/db")

db_bp.template_folder = Path(__file__).parent.parent / "pages"
db_bp.static_folder = Path(__file__).parent.parent / "src"


async def fetch_languages(session: aiohttp.ClientSession, repo_name: str):
    async with session.get(
        f"https://api.github.com/repos/Wishrito/{repo_name}/languages", timeout=5
    ) as response:
        return await response.json()


@db_bp.post("/refresh")
def db_refresh(): ...
