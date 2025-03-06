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
from sqlalchemy import select, update

from database import fetch_languages
from models import Gist, GistFile, GistFileImage, Project, db
from utils import Url, call_api


class Api(Blueprint):
    def __init__(self, name, import_name, static_folder=None, static_url_path=None, template_folder=None, url_prefix=None, subdomain=None, url_defaults=None, root_path=None, cli_group=...):
        super().__init__(name, import_name, static_folder, static_url_path,
                         template_folder, url_prefix, subdomain, url_defaults, root_path, cli_group)
        self.url = Url()


api_route = Api('api', __name__, url_prefix="/api")
api_route.template_folder = Path(__file__).parent / "pages"
api_route.static_folder = Path(__file__).parent / "src"


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


@api_route.route("/tests", methods=['GET', 'POST'])
async def tests():
    match request.method:
        case 'GET':
            stmt = (
                select(Gist, GistFile, GistFileImage)
                .where(Gist.author == "Wishrito")
                # Condition de jointure correcte pour GistFile
                .join(GistFile, GistFile.gist_id == Gist.id)
                # Condition de jointure correcte pour GistFileImage
                .join(GistFileImage, GistFileImage.gistfile_id == GistFile.id)
            )
            result = db.session.execute(stmt)
            print(result.all())
            if result is None:
                return "pas de résultat"
            return str(result.all())
        case "POST":
            response: list[dict] = await call_api(api_route.url.api_projects)
            for project in response:
                select_stmt = (
                    select(Gist, GistFile, GistFileImage)
                    .where(Gist.author == project['author'])
                    # Condition de jointure correcte pour GistFile
                    .join(GistFile, GistFile.gist_id == Gist.id)
                    # Condition de jointure correcte pour GistFileImage
                    .join(GistFileImage, GistFileImage.gistfile_id == GistFile.id)
                )
                exists = db.session.execute(select_stmt).first()
                if exists:
                    update_stmt = (
                        update(Gist)
                        .where(Gist.id == exists[0].id)
                        .values(**project)
                    )
                    print(update_stmt)
                    db.session.execute(update_stmt)
                else:
                    create_gist(project)
                db.session.commit()


def create_gist(gist_data: dict):
    new_gist = Gist(
        id=gist_data['id'],
        author=gist_data['author'],
        description=gist_data['description'],
        embed_url=gist_data['embed_url']
    )

    db.session.add(new_gist)
    db.session.commit()

    # Créer un objet GistFile associé à ce Gist

    gf_list = [
        GistFile(
            gist_id=new_gist.id,  # Associer ce fichier à un gist existant
            name=gf['name'],
            type=gf['type']
        ) for gf in gist_data['files']
    ]
    db.session.add_all(gf_list)
    db.session.commit()
    gfi_list = []
    for i, gfi in enumerate(gf_list):
        db.session.refresh(gfi)

        gfi_list = [
            GistFileImage(
                gistfile_id=gfi.id,  # Associer cette image au fichier
                image=gf
            ) for gf in gist_data['files'][i]['images']
        ]

    db.session.add_all(gfi_list)
    db.session.commit()
    db.session.close()


@api_route.get("/projects")
async def fetch_projects():
    """
    Load and return project data from GitHub with pagination.
    """
    API_KEY = os.getenv('LOCAL_API_KEY')
    if ('api_key' not in request.args) | (request.args.get('api_key') != API_KEY):
        return {
            "error": "Tu n'as pas accès à cette ressource."
        }, 403
    TOKEN = os.getenv('GITHUB_TOKEN')
    USERNAME = os.getenv('GITHUB_USERNAME')
    repos_request = None
    async with aiohttp.ClientSession() as session:
        repos_request = await session.get(
            f"https://api.github.com/users/{USERNAME}/repos",
            headers={"Authorization": f"Bearer {TOKEN}"},
            timeout=10
        )

        if repos_request.status == 403:
            return {
                "error": "Tu n'as pas accès à cette ressource."
            }, 403

        repos = await repos_request.json()

        # Liste de coroutines pour récupérer les langues de tous les projets
        language_tasks = [
            fetch_languages(session, repo['name']) for repo in repos if not repo['fork']
        ]
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
                json_repos['projects'].append(
                    {
                        "repo": repo['name'],
                        "url": repo['html_url'],
                        "description": repo['description'],
                        "languages": repo_languages,
                        "string_languages": ", ".join(languages.keys()).lower(),
                    }
                )

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


@api_route.get("/tools")
def fetch_env_metadata():
    """
    Retrieves metadata about the current Python environment and used libraries.
    Returns:
        dict: A dictionary containing the Python version and a list of dictionaries 
              with the names and versions of the used libraries.
    """

    API_KEY = os.getenv('LOCAL_API_KEY')
    if ('api_key' not in request.args) | (request.args.get('api_key') != API_KEY):
        return {
            "error": "Tu n'as pas accès à cette ressource."
        }, 403

    used_libs = ['flask', 'pygithub', 'aiohttp']

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


@api_route.get('/gist_metadata')
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

    API_KEY = os.getenv('LOCAL_API_KEY')
    if ('api_key' not in request.args) | (request.args.get('api_key') != API_KEY):
        return {
            "error": "Tu n'as pas accès à cette ressource."
        }, 403
    TOKEN = os.getenv('GITHUB_TOKEN')
    USERNAME = os.getenv('GITHUB_USERNAME')
    github = Github(TOKEN)

    user = github.get_user(USERNAME)
    gists = user.get_gists()

    if "id" in request.args:
        gist_id = request.args.get("id")

        for g in gists:
            if g.id == gist_id:
                gist_data = {
                    'author': g.owner.name,
                    'gist_id': g.id,
                    'description': g.description,
                    'files': [
                        {
                            'name': g.files[file].filename,
                            'type': g.files[file].type,
                            'images': [
                                f"{url}.jpg" for url in parse_tuto_image(g.files[file])
                            ]
                        } for file in g.files
                    ],
                    'embed_url': f'https://gist.github.com/Wishrito/{g.id}.js'
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
        for g in gists_list:
            g['title'] = str(g['files'][0]['name'].removesuffix(
                '.md').title().replace('_', ' '))
        return gists_list
    github.close()
