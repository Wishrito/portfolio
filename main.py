import json
import os
from pathlib import Path
import sys

import aiohttp
from dotenv import load_dotenv
from flask import redirect, render_template, request, send_file
from werkzeug.routing import Rule

from modules.api import api_bp
from modules.classes import Portfolio
from modules.handlers import handler_bp
from modules.utils import call_api


def has_no_empty_params(rule: Rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


app = Portfolio("Portfolio")
if not app.vercel_project_production_url:
    app.config['SERVER_NAME'] = "localhost:5000"
load_dotenv()

app.register_blueprint(api_bp)
app.register_blueprint(handler_bp)


@app.get("/")
async def home():
    """
    Renders the home page template.

    Returns:
        Response: The rendered HTML template for the home page.
    """
    skills = await call_api(
        app.url.api_skills, parameters={"api_key": os.getenv("LOCAL_API_KEY")}
    )
    print(f"skills : {skills}")
    return render_template("index.j2", skills=skills.get("skills", []))


@app.route("/site-map")
async def site_map():
    if app.template_folder:
        links: list[tuple[str, str]] = [
            (page.stem, page.name) for page in Path(app.template_folder).glob("*.j2")
        ]

        return render_template("sitemap.j2", routes=links)
    else:
        return redirect("/")


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
    return render_template("projects.j2", data=projects_data)


@app.get('/about')
async def about():
    """
    Fetches tools data from an API endpoint and renders the 'about' page.

    This function retrieves the root URL from the environment variable
    'VERCEL_PROJECT_PRODUCTION_URL'. If the environment variable is not set,
    it defaults to the request's root URL. It then fetches data from the
    '/api/tools' endpoint and passes this data to the 'about.j2' template
    for rendering.

    Returns:
        A rendered HTML template for the 'about' page with tools data.
    """
    libs_data = await call_api(
        url=app.url.api_tools, parameters={"api_key": os.getenv("LOCAL_API_KEY")}
    )
    return render_template("about.j2", tools_data=libs_data)


@app.get("/tutorials")
async def get_gists():
    """
    Fetches the list of gists from the specified URL and renders the 'tutorials.j2' template with the gists data.

    The function first retrieves the root URL from the environment variable 'VERCEL_PROJECT_PRODUCTION_URL'.
    If the environment variable is not set, it defaults to using the request's URL root.
    It then constructs the full URL to fetch the gists metadata and makes a GET request to that URL.
    Finally, it renders the 'tutorials.j2' template with the fetched gists data and the root URL.

    Returns:
        str: The rendered 'tutorials.j2' template with the gists data and root URL.
    """
    if "id" in request.args:
        gist_id = request.args.get("id")

        gist_data = call_api(
            app.url.api_gists, {"id": gist_id, "api_key": os.getenv("LOCAL_API_KEY")}
        )
        return render_template("tutorials.j2", gist_data=gist_data)

    else:
        tutorials_list = await call_api(
            app.url.api_gists, {"api_key": os.getenv("LOCAL_API_KEY")}
        )
        return render_template("tutorials.j2", gists=tutorials_list)


@app.get("/grille")
def grille():
    """
    Renders the 'skill grille'.

    Returns:
        str: The rendered HTML template for the grille page.
    """
    return send_file(f"{app.static_folder}/data/BTS SIO 2025 - Tableau de synthese.pdf")


if not app.vercel_project_production_url:
    app.run(host="localhost", port=5000, debug=True)
