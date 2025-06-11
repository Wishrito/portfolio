import os
from pathlib import Path
from typing import Any

from flask import Blueprint, Flask, request

from typing import TypedDict, List


class Url:

    @property
    def api_projects(self):
        return self.root_url + "/api/projects"

    @property
    def api_gists(self):
        return self.root_url + "/api/tutorials"

    @property
    def api_tools(self):
        return self.root_url + "/api/tools"

    @property
    def api_skills(self):
        return self.root_url + "/api/skills"

    @property
    def root_url(self):
        url = os.getenv("VERCEL_PROJECT_PRODUCTION_URL", "default")
        if url == "default":
            url = request.url_root
        else:
            url = "https://" + url
        return url


class Portfolio(Flask):
    """
    Portfolio class that extends the Flask class to create a custom Flask application.

    Attributes:
        url (Url): An instance of the Url class.
        vercel_project_production_url (str): The production URL of the Vercel project, retrieved from environment variables.
    """

    def __init__(
        self,
        import_name,
        static_url_path=None,
        static_host=None,
        host_matching=False,
        subdomain_matching=False,
        instance_path=None,
        instance_relative_config=False,
        root_path=None,
    ):
        super().__init__(
            import_name,
            static_url_path,
            Path(__file__).parent.parent / "src",
            static_host,
            host_matching,
            subdomain_matching,
            Path(__file__).parent.parent / "pages",
            instance_path,
            instance_relative_config,
            root_path,
        )
        self.url = Url()
        self.vercel_project_production_url = os.getenv("VERCEL_PROJECT_PRODUCTION_URL")


class CustomBlueprint(Blueprint):
    def __init__(
        self,
        name: str,
        import_name: str,
        static_folder: str | os.PathLike[str] | None = None,
        static_url_path: str | None = None,
        template_folder: str | os.PathLike[str] | None = None,
        url_prefix: str | None = None,
        subdomain: str | None = None,
        url_defaults: dict[str, Any] | None = None,
        root_path: str | None = None,
        cli_group: str | None = ...,  # type: ignore
    ) -> None:
        super().__init__(
            name,
            import_name,
            Path(__file__).parent.parent / "src",
            static_url_path,
            Path(__file__).parent.parent / "pages",
            url_prefix,
            subdomain,
            url_defaults,
            root_path,
            cli_group,
        )
        self.url = Url()
        self.vercel_project_production_url = os.getenv("VERCEL_PROJECT_PRODUCTION_URL")


class Api(CustomBlueprint):
    def __init__(
        self,
        name,
        import_name,
        static_folder=None,
        static_url_path=None,
        template_folder=None,
        url_prefix=None,
        subdomain=None,
        url_defaults=None,
        root_path=None,
        cli_group=...,
    ):
        super().__init__(
            name,
            import_name,
            static_folder,
            static_url_path,
            template_folder,
            url_prefix,
            subdomain,
            url_defaults,
            root_path,
            cli_group,
        )


class Database(CustomBlueprint):
    def __init__(
        self,
        name,
        import_name,
        static_folder=None,
        static_url_path=None,
        template_folder=None,
        url_prefix=None,
        subdomain=None,
        url_defaults=None,
        root_path=None,
        cli_group=...,
    ):
        super().__init__(
            name,
            import_name,
            static_folder,
            static_url_path,
            template_folder,
            url_prefix,
            subdomain,
            url_defaults,
            root_path,
            cli_group,
        )


class Error(CustomBlueprint):
    def __init__(
        self,
        name,
        import_name,
        static_folder=None,
        static_url_path=None,
        template_folder=None,
        url_prefix=None,
        subdomain=None,
        url_defaults=None,
        root_path=None,
        cli_group=...,
    ):
        super().__init__(
            name,
            import_name,
            static_folder,
            static_url_path,
            template_folder,
            url_prefix,
            subdomain,
            url_defaults,
            root_path,
            cli_group,
        )
