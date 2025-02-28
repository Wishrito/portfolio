import os
from pathlib import Path

import requests
from flask import Flask, redirect, render_template, request

from routes import api

app = Flask(__name__)
app.template_folder = Path(__file__).parent / "pages"
app.static_folder = Path(__file__).parent / "src"

app.register_blueprint(api, url_prefix="/api")


@app.errorhandler(404)
def page_not_found(error):
    """
    Handle 404 Page Not Found error.

    Args:
        error: The error object containing details about the 404 error.

    Returns:
        A rendered template for the 404 error page.
    """
    return render_template("404.html")


@app.get('/')
def home():
    """
    Renders the home page template.

    Returns:
        Response: The rendered HTML template for the home page.
    """
    return render_template("index.html")


@app.get('/projects')
def projects():
    """
    Renders the projects page.

    Returns:
        A rendered HTML template for the projects page.
    """
    return render_template("projects.html")


@app.get('/about')
def about():
    """
    Fetches tools data from an API endpoint and renders the 'about' page.

    This function retrieves the root URL from the environment variable 
    'VERCEL_PROJECT_PRODUCTION_URL'. If the environment variable is not set, 
    it defaults to the request's root URL. It then fetches data from the 
    '/api/tools' endpoint and passes this data to the 'about.html' template 
    for rendering.

    Returns:
        A rendered HTML template for the 'about' page with tools data.
    """
    root_url = os.getenv(
        "VERCEL_PROJECT_PRODUCTION_URL", "default")
    if root_url == "default":
        root_url = request.url_root
    else:
        root_url = "https://" + root_url
    libs_data = requests.get(
        f"{root_url}/api/tools")
    return render_template('about.html', tools_data=libs_data.json())

@app.get('/gists')
def get_gists():
    """
    Fetches the list of gists from the specified URL and renders the 'tutorials.html' template with the gists data.

    The function first retrieves the root URL from the environment variable 'VERCEL_PROJECT_PRODUCTION_URL'.
    If the environment variable is not set, it defaults to using the request's URL root.
    It then constructs the full URL to fetch the gists metadata and makes a GET request to that URL.
    Finally, it renders the 'tutorials.html' template with the fetched gists data and the root URL.

    Returns:
        str: The rendered 'tutorials.html' template with the gists data and root URL.
    """
    root_url = os.getenv(
        "VERCEL_PROJECT_PRODUCTION_URL", "default")
    if root_url == "default":
        root_url = request.url_root
    else:
        root_url = "https://" + root_url
    gists_list = requests.get(
        f"{root_url}/api/gist_metadata")
    return render_template('tutorials.html', gists=gists_list.json(), url=root_url)


@app.get('/gist')
def get_gist():
    """
    Fetches gist metadata and renders the tutorials template.
    This function retrieves the gist ID from the request arguments and constructs
    the root URL based on the environment variable 'VERCEL_PROJECT_PRODUCTION_URL'.
    If the environment variable is not set, it defaults to the request's root URL.
    It then fetches the gist metadata from the constructed URL and renders the
    'tutorials.html' template with the fetched data.
    Returns:
        A redirect to '/gists' if the gist ID is not provided, otherwise renders
        the 'tutorials.html' template with the gist metadata.
    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    gist_id = request.args.get('id')
    root_url = os.getenv(
        "VERCEL_PROJECT_PRODUCTION_URL", "default")
    if root_url == "default":
        root_url = request.url_root
    else:
        root_url = "https://" + root_url
    if not gist_id:
        return redirect('/gists')

    gist_data = requests.get(f"{root_url}/api/gist_metadata", {'id': gist_id})
    return render_template('tutorials.html', gist_data=gist_data.json())
