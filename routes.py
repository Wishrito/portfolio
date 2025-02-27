import os
import re
from pathlib import Path

from flask import Blueprint, request
from github import Github
from github.GistFile import GistFile

api = Blueprint('api', __name__)
api.template_folder = Path(__file__).parent / "pages"
api.static_folder = Path(__file__).parent / "src"


def parse_tuto_image(file: GistFile) -> list[str]:
    texte = file.content
    pattern = r"!\[([^\]]+)\]"
    match = re.findall(pattern, texte)
    return match


@api.get('/gist_metadata')
def get_gist_metadata():
    TOKEN = os.getenv('GITHUB_TOKEN')
    USERNAME = os.getenv('GITHUB_USERNAME')
    g = Github(TOKEN)

    user = g.get_user(USERNAME)
    gists = user.get_gists()

    if "id" in request.args:
        gist_id = request.args.get("id")

        for gist in gists:
            if gist.id == gist_id:
                gist_data = {
                    'gist_id': gist.id,
                    'gist_description': gist.description,
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
                'gist_description': gist.description,
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
    g.close()
