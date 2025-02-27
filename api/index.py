from github.GistFile import GistFile
from flask import Blueprint, request
import re
import os
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request
from github import Github
import requests

app = Flask(__name__)
app.template_folder = Path(__file__).parent.parent / "pages"
app.static_folder = Path(__file__).parent.parent / "src"


def register_blueprints(app: Flask):
    app.register_blueprint(api_bp, url_prefix="/api")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")

@app.get('/')
def home():
    return render_template("index.html")


@app.get('/projects')
def about():
    return render_template("projects.html")


@app.get('/gists')
def get_gists():
    root_url = os.getenv(
        "VERCEL_PROJECT_PRODUCTION_URL", request.url_root)
    gists_list = requests.get(
        f"{root_url}/api/gist_metadata")
    return render_template('tutorials.html', gists=gists_list.json())

@app.get('/gist')
def get_gist():
    gist_id = request.args.get('id')
    root_url = os.getenv(
        "VERCEL_PROJECT_PRODUCTION_URL", request.url_root)
    if not gist_id:
        return redirect('/gists')

    gist_data = requests.get(f"{root_url}/api/gist_metadata?id={gist_id}")
    return render_template('tutorials.html', gist_data=gist_data.json())


api_bp = Blueprint('api', __name__)
api_bp.template_folder = app.template_folder
api_bp.static_folder = app.static_folder


def parse_tuto_image(file: GistFile) -> list[str]:
    texte = file.content
    pattern = r"!\[([^\]]+)\]"
    match = re.findall(pattern, texte)
    return match


@api_bp.get('/gist_metadata')
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


register_blueprints(app)
