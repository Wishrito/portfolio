import os
from pathlib import Path

import aiohttp
from dotenv import load_dotenv
from flask import redirect, render_template, request
from werkzeug.routing import Rule

from modules.classes import Portfolio
from modules.database import db_bp
from modules.api import api_bp
from modules.handlers import handler_bp
from modules.models import db
from modules.utils import call_api


def has_no_empty_params(rule: Rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


app = Portfolio("Portfolio")
if not app.vercel_project_production_url:
    app.config["SERVER_NAME"] = "localhost:5000"
load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

# Désactive la modification du suivi
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(db_bp)
app.register_blueprint(api_bp)
app.register_blueprint(handler_bp)


@app.get('/')
def home():
    """
    Renders the home page template.

    Returns:
        Response: The rendered HTML template for the home page.
    """
    return render_template("index.html")


@app.route("/site-map")
def site_map():
    links: list[tuple[str, str]] = []
    for page in Path(app.template_folder).glob("*.html"):
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        links.append((page.stem, page.name))
    return render_template("sitemap.html", routes=links)


@app.get('/projects')
async def projects():
    """
    Renders the projects page.

    Returns:
        A rendered HTML template for the projects page.
    """
    projects_data = await call_api(
        url=app.url.api_projects,
        parameters={
            'api_key': os.getenv('LOCAL_API_KEY')
        }
    )
    return render_template("projects.html", data=projects_data)


@app.get('/about')
async def about():
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
    async with aiohttp.ClientSession() as session:
        libs_data = await session.get(app.url.api_tools, params={'api_key': os.getenv('LOCAL_API_KEY')})
        return render_template('about.html', tools_data=await libs_data.json())

@app.get('/gists')
async def get_gists():
    """
    Fetches the list of gists from the specified URL and renders the 'tutorials.html' template with the gists data.

    The function first retrieves the root URL from the environment variable 'VERCEL_PROJECT_PRODUCTION_URL'.
    If the environment variable is not set, it defaults to using the request's URL root.
    It then constructs the full URL to fetch the gists metadata and makes a GET request to that URL.
    Finally, it renders the 'tutorials.html' template with the fetched gists data and the root URL.

    Returns:
        str: The rendered 'tutorials.html' template with the gists data and root URL.
    """
    async with aiohttp.ClientSession() as session:
        gists_list = await session.get(app.url.api_gists, params={'api_key': os.getenv('LOCAL_API_KEY')})
        return render_template('tutorials.html', gists=await gists_list.json())


@app.get('/gist')
async def get_gist():
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

    async with aiohttp.ClientSession() as session:
        gist_data = await session.get(app.url.api_gists, params={'id': gist_id, 'api_key': os.getenv('LOCAL_API_KEY')})
        return render_template('tutorials.html', gist_data=await gist_data.json())

if not app.vercel_project_production_url:
    app.run(host="localhost", port=5000, debug=True)
