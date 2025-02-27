import os
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request
from github import Github
import requests

from utils import register_blueprints

app = Flask(__name__)
app.template_folder = Path(__file__).parent.parent / "pages"
app.static_folder = Path(__file__).parent.parent / "src"

register_blueprints(app)

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
    match gists_list.status_code:
        case 200:
            return render_template('tutorials.html', gists=gists_list.json())
        case _:
            return "Error", gists_list.status_code


@app.get('/gist')
def get_gist():
    gist_id = request.args.get('id')
    root_url = os.getenv(
        "VERCEL_PROJECT_PRODUCTION_URL", request.url_root)
    if not gist_id:
        return redirect('/gists')

    gist_data = requests.get(f"{root_url}/api/gist_metadata?id={gist_id}")
    match gist_data:
        case 200:
            return render_template('tutorials.html', gist_data=gist_data.json())
        case _:
            return 'Gist not found 😔', 404


app.run(debug=True)
