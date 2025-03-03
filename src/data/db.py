import json
from pathlib import Path


class Project:
    def __init__(self, repo_name: str, repo_url: str, repo_description: str, languages: list["Language"]):
        self.repo_name: str = repo_name
        self.repo_url: str = repo_url
        self.repo_description: str = repo_description
        self.languages: list["Language"] = languages

    def to_dict(self):
        return {
            "repo": self.repo_name,
            "url": self.repo_url,
            "description": self.repo_description,
            "languages": [
                language.to_dict() for language in self.languages
            ]
        }


class Language:
    def __init__(self, name: str):
        self.name = name
        self.icon = f"{name.lower()}-logo"

    def to_dict(self):
        return {
            "name": self.name,
            "icon": self.icon
        }


class Pagination:
    def __init__(self, page: int, repos_per_page: int, total_repos: int):
        self.page = page
        self.repos_per_page = repos_per_page
        self.total_repos = total_repos
        self.total_pages = (total_repos // repos_per_page) + \
            (1 if total_repos % repos_per_page else 0)

    def to_dict(self):
        return {
            "page": self.page,
            "repos_per_page": self.repos_per_page,
            "total_repos": self.total_repos,
            "total_pages": self.total_pages
        }


class ProjectData:
    def __init__(self, projects: list[Project], pagination: Pagination):
        self.projects: list[Project] = projects
        self.pagination: Pagination = pagination

    def to_dict(self):
        return {
            "projects": [
                project.to_dict() for project in self.projects
            ],
            "pagination": self.pagination.to_dict()
        }

    def save_to_file(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(
                self.to_dict(),
                Path(__file__).parent / "src" / "data" / f,
                indent=4
            )
