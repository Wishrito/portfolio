from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UsedLib:
    name: str
    desc: str


@dataclass
class Language:
    id: str
    name: str
    icon_name: str
    desc: str
    used_libs: Optional[List[UsedLib]] = field(default_factory=list)

    def get_projects_count(self, db) -> int:
        return sum(1 for project in db.projects if self in project.languages)


@dataclass
class Software:
    id: str
    name: str
    icon_name: str


@dataclass
class Project:
    name: str
    languages: List[Language]
    repo: str

    def get_language_count(self):
        return len(self.languages)


@dataclass
class Database:
    softwares: List[Software]
    languages: List[Language]
    projects: List[Project]


# Exemple d'initialisation des données
db = Database(
    softwares=[
        Software(id="vsc", name="Visual Studio Code", icon_name="vsc-logo.png")
    ],
    languages=[
        Language(
            id="py",
            name="Python",
            icon_name="python-logo.png",
            desc="Développement de diverses applications en Python (voir <a href='/projects'>Projets</a>)",
            used_libs=[
                UsedLib(name="discord-py", desc="placeholder"),
                UsedLib(name="python-dotenv", desc="placeholder")
            ]
        ),
        Language(
            id="js",
            name="JavaScript",
            icon_name="javascript-logo.png",
            desc="Ajout d'interactivité et de dynamique aux pages web avec des scripts et des librairies."
        ),
        Language(
            id="java",
            name="Java",
            icon_name="java-logo.png",
            desc="Développement d'applications avec le language Java."
        ),
        Language(
            id="html",
            name="HTML/CSS",
            icon_name="html-logo.png",
            desc="Création de pages web avec structure sémantique et accessible."
        ),
        Language(
            id="sql",
            name="SQL",
            icon_name="sql-logo.png",
            desc="Manipulation de données avec système de gestion de base de données relationnelles."
        ),
        Language(
            id="vb",
            name="Visual Basic",
            icon_name="visualbasic-logo.png",
            desc="Développement d'applications console avec Visual Basic."
        )
    ],
    projects=[
        Project(
            name="Bread-Chan",
            languages=[
                Language(
                    id="py",
                    name="Python",
                    icon_name="python-logo.png",
                    desc="Développement de diverses applications en Python (voir <a href='/projects'>Projets</a>)",
                    used_libs=[
                        UsedLib(name="discord-py", desc="placeholder"),
                        UsedLib(name="python-dotenv", desc="placeholder")
                    ]
                ),
                Language(
                    id="html",
                    name="HTML/CSS",
                    icon_name="html-logo.png",
                    desc="Création de pages web avec structure sémantique et accessible."
                ),
                Language(
                    id="sql",
                    name="SQL",
                    icon_name="sql-logo.png",
                    desc="Manipulation de données avec système de gestion de base de données relationnelles."
                )
            ],
            repo="https://github.com/Wishrito/Bread-Chan"
        )
    ]
)
print(db.languages[0].get_projects_count(db))
