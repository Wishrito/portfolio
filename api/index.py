import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from github import Github


app = Flask(__name__)
app.template_folder = Path(__file__).parent.parent / "pages"
app.static_folder = Path(__file__).parent.parent / "src"


@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/projects')
def about():
    return render_template("projects.html")


@app.route('/gists', methods=["GET"])
def get_gists():
    TOKEN = os.getenv('GITHUB_TOKEN')
    USERNAME = os.getenv('GITHUB_USERNAME')
    g = Github(TOKEN)

    user = g.get_user(USERNAME)
    gists = user.get_gists()
    gists_list = [
        {
            'id': gist.id,
            'gist_description': gist.description,
            'files': [
                {
                    'name': gist.files[file].filename, 
                    'type': gist.files[file].type
                } for file in gist.files
            ],
            'title': '',
            'embed_url': f'https://gist.github.com/Wishrito/{gist.id}.js'
        } for gist in gists
    ]
    for gist in gists_list:
        gist['title'] = str(gist['files'][0]['name'].removesuffix(
        '.md').title().replace('_', ' '))
    g.close()

    return render_template('tutorials.html', gists=gists_list)


@app.route('/gist', methods=["GET"])
def get_gist():
    gist_id = request.args.get('id')
    if not gist_id:
        return render_template('tutorials.html')
    TOKEN = os.getenv('GITHUB_TOKEN')
    USERNAME = os.getenv('GITHUB_USERNAME')
    g = Github(TOKEN)

    user = g.get_user(USERNAME)
    gists = user.get_gists()

    for gist in gists:
        if gist.id == gist_id:
            gist_data = {
                'gist_id': gist.id,
                'files': [
                    {
                        'name': gist.files[file].filename,
                        'type': gist.files[file].type
                    } for file in gist.files
                ],
                'embed_url': f'https://gist.github.com/Wishrito/{gist.id}.js'
            }
            gist_data['title'] = str(gist_data['files'][0]['name'].removesuffix(
                '.md').title().replace('_', ' '))
            return render_template('tutorials.html', gist_data=gist_data)

    return 'Gist not found 😔', 404
