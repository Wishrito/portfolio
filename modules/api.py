"""This module defines API routes for a Flask application to interact with GitHub gists and retrieve environment metadata.
Routes:
    - /tools: Retrieves metadata about the current Python environment and used libraries.
    - /gist_metadata: Fetches metadata for GitHub gists of a user.
Functions:
    - parse_tuto_image(file: GistFile) -> list[str]: Extracts image URLs from the content of a GistFile.
    - get_env_metadata() -> dict: Retrieves metadata about the current Python environment and used libraries.
    - get_gist_metadata() -> Union[dict, list]: Fetches metadata for GitHub gists of a user.
Dependencies:
    - flask: For creating the API routes.
    - pygithub: For interacting with the GitHub API.
    - python-dotenv: For loading environment variables.
    - requests: For making HTTP requests."""

import asyncio
import os
import re
import sys
from importlib.metadata import version
from pathlib import Path

import aiohttp
from flask import jsonify, request
from github import Github
from sqlalchemy import select, update

from .classes import Api
from .database import fetch_languages
from .models import Gist, GistFile, GistFileImage, Project, db
from .utils import call_api

api_bp = Api("api", __name__, url_prefix="/api")
api_bp.template_folder = Path(__file__).parent.parent / "pages"
print(api_bp.template_folder)
api_bp.static_folder = Path(__file__).parent.parent / "src"


def parse_tuto_image(file: GistFile | str) -> list[str]:
    """
    Extracts image URLs from the content of a GistFile.

    Args:
        file (GistFile): The GistFile object containing the content to parse.

    Returns:
        list[str]: A list of image URLs found in the content.
    """
    texte = None
    if isinstance(file, GistFile):
        texte = file.content
    else:
        texte = file
    pattern = r"!\[[^\]]+\]\(([^)]+)\)"  # Capture uniquement l'URL
    match = re.findall(pattern, texte)
    return match


if api_bp.vercel_project_production_url is None:

    @api_bp.route("/refresh_db", methods=["GET", "POST"])
    async def refresh_db():
        gists: list[dict] = await call_api(api_bp.url.api_gists)
        for g in gists:
            select_stmt = (
                select(Gist, GistFile, GistFileImage).where(Gist.author == g["author"])
                # Condition de jointure correcte pour GistFile
                .join(GistFile, GistFile.gist_id == Gist.id)
                # Condition de jointure correcte pour GistFileImage
                .join(GistFileImage, GistFileImage.gistfile_id == GistFile.id)
            )
            exists = db.session.execute(select_stmt).first()
            if exists:
                update_stmt = update(Gist).where(Gist.id == exists[0].id).values(**g)
                db.session.execute(update_stmt)
            else:
                create_gist(g)
            db.session.commit()
        return {"error": "forbidden"}, 403


def create_gist(gist_data: dict):
    new_gist = Gist(
        id=gist_data["id"],
        author=gist_data["author"],
        description=gist_data["description"],
        embed_url=gist_data["embed_url"],
    )

    db.session.add(new_gist)
    db.session.commit()

    # Créer un objet GistFile associé à ce Gist

    files: list[dict] = gist_data["files"]
    gf_list = [
        GistFile(
            gist_id=new_gist.id,  # Associer ce fichier à un gist existant
            name=gf["name"],
            type=gf["type"],
        )
        for gf in files
    ]
    db.session.add_all(gf_list)
    db.session.commit()
    gfi_list = []
    for i, gfi in enumerate(gf_list):
        db.session.refresh(gfi)

        gfi_list = [
            GistFileImage(
                gistfile_id=gfi.id, image=gf  # Associer cette image au fichier
            )
            for gf in files[i]["images"]
        ]

    db.session.add_all(gfi_list)
    db.session.commit()
    db.session.close()


@api_bp.get("/projects")
async def fetch_projects():
    """
    Load and return project data from GitHub with pagination.
    """
    API_KEY = os.getenv("LOCAL_API_KEY")
    if ("api_key" not in request.args) | (request.args.get("api_key") != API_KEY):
        return {"error": "Tu n'as pas accès à cette ressource."}, 403
    TOKEN = os.getenv("GITHUB_TOKEN")
    USERNAME = os.getenv("GITHUB_USERNAME")
    repos_request = None
    async with aiohttp.ClientSession() as session:
        repos_request = await session.get(
            f"https://api.github.com/users/{USERNAME}/repos",
            headers={"Authorization": f"Bearer {TOKEN}"},
            timeout=10,
        )

        if repos_request.status == 403:
            return {"error": "Tu n'as pas accès à cette ressource."}, 403

        repos: list[dict] = await repos_request.json()

        # Liste de coroutines pour récupérer les langues de tous les projets
        language_tasks = [
            fetch_languages(session, r["name"]) for r in repos if not r["fork"]
        ]
        languages_results: list[dict[str, int]] = await asyncio.gather(*language_tasks)

        json_repos = {"projects": []}

        for repo, languages in zip(repos, languages_results):
            if not repo["fork"]:  # Ignorer les forks
                repo_languages = [
                    {
                        "name": lang,
                        "icon": f"{lang.lower()}-logo",
                        "use_rate": int(count),
                    }
                    for lang, count in languages.items()
                ]
                json_repos["projects"].append(
                    {
                        "repo": repo["name"],
                        "url": repo["html_url"],
                        "description": repo["description"],
                        "languages": repo_languages,
                        "string_languages": ", ".join(languages.keys()).lower(),
                    }
                )

        # Extraire les langues uniques
        languages_set = set()
        for project in json_repos["projects"]:
            languages_set.update(lang["name"].lower() for lang in project["languages"])

        json_repos["languages"] = list(languages_set)

        return jsonify(json_repos)

    return jsonify(await repos_request.json())


@api_bp.get("/tools")
def fetch_env_metadata():
    """
    Retrieves metadata about the current Python environment and used libraries.
    Returns:
        dict: A dictionary containing the Python version and a list of dictionaries
              with the names and versions of the used libraries.
    """

    API_KEY = os.getenv("LOCAL_API_KEY")
    if ("api_key" not in request.args) | (request.args.get("api_key") != API_KEY):
        return {"error": "Tu n'as pas accès à cette ressource."}, 403

    used_libs = ["flask", "pygithub", "aiohttp"]

    tools_data = {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "libs": [{"name": lib, "version": version(lib)} for lib in used_libs],
    }

    return tools_data


@api_bp.get("/gist_metadata")
def fetch_gist_metadata():
    """
    Fetches metadata for GitHub gists of a user.
    This function retrieves the metadata of GitHub gists for a user specified by the
    environment variables 'GITHUB_TOKEN' and 'GITHUB_USERNAME'. If an 'id' parameter
    is provided in the request arguments, it returns the metadata for the specific gist
    with that ID. Otherwise, it returns a list of metadata for all gists of the user.
    Returns:
        dict: Metadata of a specific gist if 'id' is provided in request arguments.
        list: List of metadata for all gists if 'id' is not provided in request arguments.
    Metadata includes:
        - author: Name of the gist owner.
        - gist_id: ID of the gist.
        - description: Description of the gist.
        - files: List of files in the gist, each containing:
            - name: Filename.
            - type: File type.
            - images: List of image URLs parsed from the file.
        - embed_url: URL to embed the gist.
        - title: Title derived from the first file's name.
    """

    API_KEY = os.getenv("LOCAL_API_KEY")
    if ("api_key" not in request.args) | (request.args.get("api_key") != API_KEY):
        return {"error": "Tu n'as pas accès à cette ressource."}, 403
    TOKEN = os.getenv("GITHUB_TOKEN")
    USERNAME = os.getenv("GITHUB_USERNAME")
    github = Github(TOKEN)

    user = github.get_user(USERNAME)
    gists = user.get_gists()

    if "id" in request.args:
        gist_id = request.args.get("id")

        for g in gists:
            if g.id == gist_id:
                gist_data = {
                    "author": g.owner.name,
                    "gist_id": g.id,
                    "description": g.description,
                    "files": [
                        {
                            "name": g.files[file].filename,
                            "type": g.files[file].type,
                            "images": [
                                f"{url}.jpg" for url in parse_tuto_image(g.files[file])
                            ],
                        }
                        for file in g.files
                    ],
                    "embed_url": f"https://gist.github.com/Wishrito/{g.id}.js",
                }
                gist_data["title"] = str(
                    gist_data["files"][0]["name"]
                    .removesuffix(".md")
                    .title()
                    .replace("_", " ")
                )
                return gist_data
    else:

        gists_list = [
            {
                "id": gist.id,
                "description": gist.description,
                "files": [
                    {
                        "name": gist.files[file].filename,
                        "type": gist.files[file].type,
                        "images": [
                            f"{url}.jpg" for url in parse_tuto_image(gist.files[file])
                        ],
                    }
                    for file in gist.files
                ],
                "title": "",
                "embed_url": f"https://gist.github.com/Wishrito/{gist.id}.js",
            }
            for gist in gists
        ]
        for g in gists_list:
            g["title"] = str(
                g["files"][0]["name"].removesuffix(".md").title().replace("_", " ")
            )
        return gists_list
    github.close()
