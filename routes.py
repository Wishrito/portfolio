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

from flask import Blueprint, jsonify, request
from github import Github
from github.GistFile import GistFile

api = Blueprint('api', __name__)
api.template_folder = Path(__file__).parent / "pages"
api.static_folder = Path(__file__).parent / "src"


async def fetch_languages(session: aiohttp.ClientSession, repo_name: str):
    async with session.get(f"https://api.github.com/repos/Wishrito/{repo_name}/languages", timeout=5) as response:
        return await response.json()


# def lighten_color(hex_code: str, lightness: int = 50) -> str:
#     """
#     Éclaire la couleur hexadécimale en augmentant les valeurs de chaque composant RGB.
    
#     Args:
#         hex_code (str): Le code hexadécimal à éclaircir.
#         lightness (int): Le facteur d'éclaircissement (de 0 à 255).
        
#     Returns:
#         str: Le code hexadécimal éclairci.
#     """
#     # Extraire les composantes RGB du code hexadécimal
#     r, g, b = int(hex_code[:2], 16), int(
#         hex_code[2:4], 16), int(hex_code[4:6], 16)

#     # Appliquer l'éclaircissement
#     r = min(255, r + lightness)
#     g = min(255, g + lightness)
#     b = min(255, b + lightness)

#     # Retourner le code hexadécimal ajusté
#     return f"{r:02x}{g:02x}{b:02x}"


# def convert_to_hex(texte: str, lightness: int = 50) -> str:
#     """
#     Convertit un texte en code hexadécimal de 6 caractères et l'éclaire.

#     Args:
#         texte (str): Le texte à convertir.
#         lightness (int): Le facteur d'éclaircissement de la couleur (de 0 à 255).

#     Returns:
#         str: Le code hexadécimal éclairci.
#     """
#     hex_code = ''.join(format(ord(char), '02x') for char in texte)
#     # On ne garde que les 6 premiers caractères pour le code hex
#     hex_code = hex_code[:6]
#     return lighten_color(hex_code, lightness)


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
async def fetch_projects():
    """
    Load and return project data from GitHub with pagination.
    """
    TOKEN = os.getenv('GITHUB_TOKEN')
    USERNAME = os.getenv('GITHUB_USERNAME')

    async with aiohttp.ClientSession() as session:
        repos_request = await session.get(
            f"https://api.github.com/users/{USERNAME}/repos",
            headers={"Authorization": f"Bearer {TOKEN}"},
            timeout=10
        )
        if repos_request.status in [403, 429]:
            return "Désolé, j'ai un peu de mal à suivre, il y a beaucoup de trafic 😅 réessaie dans quelques minutes, s'il te plaît", repos_request.status
        if repos_request.ok:
            repos = await repos_request.json()

            # Liste de coroutines pour récupérer les langues de tous les projets
            language_tasks = [fetch_languages(
                session, repo['name']) for repo in repos if not repo['fork']]
            languages_results = await asyncio.gather(*language_tasks)

            json_repos = {
                "projects": []
            }

            for repo, languages in zip(repos, languages_results):
                if not repo['fork']:  # Ignorer les forks
                    repo_languages = [
                        {
                            "name": lang,
                            "icon": f"{lang.lower()}-logo",
                            "use_rate": int(count)
                        }
                        for lang, count in languages.items()
                    ]
                    json_repos['projects'].append({
                        "repo": repo['name'],
                        "url": repo['html_url'],
                        "description": repo['description'],
                        "languages": repo_languages,
                        "string_languages": ", ".join(languages.keys()).lower(),
                    })

            # Extraire les langues uniques
            languages_set = set()
            for project in json_repos['projects']:
                languages_set.update(lang['name'].lower()
                                     for lang in project['languages'])

            json_repos['languages'] = list(languages_set)

            # # Déterminer la langue dominante et affecter la couleur
            # for project in json_repos['projects']:
            #     lang_name = [language['name']
            #                  for language in project['languages']]
            #     lang_use_rate = [language['use_rate']
            #                      for language in project['languages']]
            #     max_val_couple = max(
            #         zip(lang_name, lang_use_rate), key=lambda x: x[1], default=('', 0))
            #     project['hex_color'] = convert_to_hex(max_val_couple[0])

            return jsonify(json_repos)

        return jsonify(await repos_request.json())


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
