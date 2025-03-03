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

from flask import request, jsonify
import json
import os
import re
import sys
from importlib.metadata import version
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request, url_for
from github import Github
from github.GistFile import GistFile

api = Blueprint('api', __name__)
api.template_folder = Path(__file__).parent / "pages"
api.static_folder = Path(__file__).parent / "src"


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


@api.get("/projects")
def fetch_projects():
    """
    Load and return project data from GitHub with pagination.
    This function loads project data from GitHub and supports pagination
    through the 'page' query parameter.
    Returns:
        dict: A dictionary containing the project data loaded from GitHub.
    """
    TOKEN = os.getenv('GITHUB_TOKEN')
    USERNAME = os.getenv('GITHUB_USERNAME')

    # Récupérer les paramètres de pagination (page et repos par page)
    # Par défaut, la page 1 si pas de paramètre
    page = int(request.args.get('page', 1))
    repos_per_page = 5  # Nombre de dépôts par page

    github = Github(TOKEN)
    user = github.get_user(USERNAME)

    # Récupérer les repos avec pagination
    repos = user.get_repos()

    # Préparer la réponse
    json_repos = {
        "projects": [
            {
                "repo": repo.name,
                "url": repo.url,
                "description": repo.description,
                "languages": [
                    {
                        "name": name,
                        "icon": f"{name.lower()}-logo"
                    } for name in repo.get_languages()
                ]
            } for repo in repos
        ]
    }

    # Récupérer le nombre total de repos pour le calcul des pages
    total_repos = user.public_repos  # Nombre total de repos publics
    total_pages = (total_repos // repos_per_page) + \
        (1 if total_repos % repos_per_page else 0)

    # Ajouter les informations de pagination
    json_repos["pagination"] = {
        "page": page,
        "repos_per_page": repos_per_page,
        "total_repos": total_repos,
        "total_pages": total_pages
    }

    return jsonify(json_repos)


@api.get("/tools")
def fetch_env_metadata():
    """
    Retrieves metadata about the current Python environment and used libraries.
    Returns:
        dict: A dictionary containing the Python version and a list of dictionaries 
              with the names and versions of the used libraries.
    """
    used_libs = ['flask', 'pygithub', 'python-dotenv', 'requests']

    tools_data = {
        'python': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'libs': [
            {
                'name': lib,
                'version': version(lib)
            } for lib in used_libs
        ]
    }

    return tools_data


@api.get('/gist_metadata')
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
    TOKEN = os.getenv('GITHUB_TOKEN')
    USERNAME = os.getenv('GITHUB_USERNAME')
    github = Github(TOKEN)

    user = github.get_user(USERNAME)
    gists = user.get_gists()

    if "id" in request.args:
        gist_id = request.args.get("id")

        for gist in gists:
            if gist.id == gist_id:
                gist_data = {
                    'author': gist.owner.name,
                    'gist_id': gist.id,
                    'description': gist.description,
                    'files': [
                        {
                            'name': gist.files[file].filename,
                            'type': gist.files[file].type,
                            'images': [
                                f"{url}.jpg" for url in parse_tuto_image(gist.files[file])
                            ]
                        } for file in gist.files
                    ],
                    'embed_url': f'https://gist.github.com/Wishrito/{gist.id}.js'
                }
                gist_data['title'] = str(gist_data['files'][0]['name'].removesuffix(
                    '.md').title().replace('_', ' '))
                return gist_data
    else:

        gists_list = [
            {
                'id': gist.id,
                'description': gist.description,
                'files': [
                    {
                        'name': gist.files[file].filename,
                        'type': gist.files[file].type,
                        'images': [
                            f"{url}.jpg" for url in parse_tuto_image(gist.files[file])
                        ]
                    } for file in gist.files
                ],
                'title': '',
                'embed_url': f'https://gist.github.com/Wishrito/{gist.id}.js'
            } for gist in gists
        ]
        for gist in gists_list:
            gist['title'] = str(gist['files'][0]['name'].removesuffix(
                '.md').title().replace('_', ' '))
        return gists_list
    github.close()
