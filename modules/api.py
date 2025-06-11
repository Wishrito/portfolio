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
import json
import os
import re
import sys
from importlib.metadata import version


from flask import jsonify

from .classes import Api
from .utils import JsonDictionnary, get_json_data, require_api_key

api_bp = Api("api", __name__, url_prefix="/api")


@api_bp.get("/projects")
@require_api_key()
async def fetch_projects():
    """
    Load and return project data from GitHub with pagination.
    """
    static_folder = api_bp.static_folder
    if static_folder is None:
        return jsonify({"error": "Static folder not configured"}), 500

    data = await get_json_data(static_folder)

    languages: list[dict] = data.get("languages", [])

    projects: list[dict] = data.get("projects", [])
    used_languages = []
    for project in projects:
        project["string_languages"] = ", ".join(
            [languages[lang["index"]]["name"] for lang in project.get("languages", [])]
        )
        for lang in project.get("languages", []):
            lang_index = lang["index"]
            del lang["index"]
            lang["name"] = languages[lang_index]["name"]
            used_languages.append(lang["name"])
    return {"projects": projects, "languages": list(set(used_languages))}


@api_bp.get("/skills")
@require_api_key()
async def fetch_skills():
    """
    Load and return skill data from GitHub with pagination.
    """
    static_folder = api_bp.static_folder
    if static_folder is None:
        return jsonify({"error": "Static folder not configured"}), 500

    skills: list[dict] = await get_json_data(static_folder, JsonDictionnary.SKILLS)
    for skill in skills:
        skill["name"] = skill["name"].capitalize()

    return {"skills": skills}


@api_bp.get("/tools")
@require_api_key()
def fetch_env_metadata():
    """
    Retrieves metadata about the current Python environment and used libraries.
    Returns:
        dict: A dictionary containing the Python version and a list of dictionaries
              with the names and versions of the used libraries.
    """

    used_libs = ["flask", "python-dotenv"]

    tools_data = {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "libs": [{"name": lib, "version": version(lib)} for lib in used_libs],
    }

    return tools_data


@api_bp.get("/tutorials")
@require_api_key()
def fetch_tutorials():
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

    return jsonify(), 403
