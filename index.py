from github.GistFile import GistFile
from flask import Blueprint, request
import re
import os
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request
from github import Github
import requests

from routes import api


app = Flask(__name__)
app.template_folder = Path(__file__).parent / "pages"
app.static_folder = Path(__file__).parent / "src"

app.register_blueprint(api, url_prefix="/api")

# def register_blueprints(app: Flask):
#     app.register_blueprint(api_bp, url_prefix="/api")


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
