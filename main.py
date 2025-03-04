import json
import os
from pathlib import Path

import requests
from flask import Flask, redirect, render_template, request, url_for

from routes import api


class Url:

    def __init__(self):
        """"""

    @property
    def api_projects(self):
        return self.root_url + "api/projects"

    @property
    def api_gists(self):
        return self.root_url + "api/gist_metadata"

    @property
    def api_tools(self):
        return self.root_url + "/api/tools"

    @property
    def root_url(self):
        url = os.getenv("VERCEL_PROJECT_PRODUCTION_URL", "default")
        if url == "default":
            url = request.url_root
        else:
            url = "https://" + url
        return url


class Portfolio(Flask):
    def __init__(self, import_name, static_url_path=None, static_folder="static", static_host=None, host_matching=False, subdomain_matching=False, template_folder="templates", instance_path=None, instance_relative_config=False, root_path=None):
        super().__init__(import_name, static_url_path, Path(__file__).parent / "src", static_host, host_matching,
                         subdomain_matching, Path(__file__).parent / "pages", instance_path, instance_relative_config, root_path)
        self.url = Url()


app = Portfolio("Portfolio")

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

    projects_data = requests.get(app.url.api_projects)
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
    libs_data = requests.get(app.url.api_tools)
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
    gists_list = requests.get(app.url.api_gists)
    return render_template('tutorials.html', gists=gists_list.json())


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

    if not gist_id:
        return redirect('/gists')

    gist_data = requests.get(app.url.api_gists, {'id': gist_id})
    return render_template('tutorials.html', gist_data=gist_data.json())
