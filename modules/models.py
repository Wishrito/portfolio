import aiohttp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import (DeclarativeBase, Mapped, MappedAsDataclass,
                            mapped_column, relationship)


# Initialisation de l'application Flask et SQLAlchemy
# Base de données en mémoire pour cet exemple
class Table(DeclarativeBase, MappedAsDataclass):
    ...


db = SQLAlchemy(model_class=Table)

# Modèle Language (langages de programmation)


class Language(Table):
    """a table containing programming languages"""
    __tablename__ = "language"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    icon: Mapped[int] = mapped_column(nullable=False)
    use_rate: Mapped[int] = mapped_column(nullable=False)


class Project(Table):
    """a table containing projects"""
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    url: Mapped[str] = mapped_column(unique=True, nullable=False)
    # Fonction pour insérer les données du JSON dans la base de données
    description: Mapped[str] = mapped_column(nullable=True)
    languages: Mapped[str] = mapped_column(
        nullable=True, default="Aucun language trouvé")

    async def populate(self):
        async with aiohttp.ClientSession() as session:
            session.get()


class GistFileImage(Table):
    """a table containing a gist file's images"""
    __tablename__ = "gistfileimage"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    gistfile_id: Mapped[int] = mapped_column(ForeignKey(
        "gistfile.id"), nullable=False)  # Clé étrangère vers GistFile
    image: Mapped[str] = mapped_column(nullable=False)

    # Ajout de la relation
    gistfile = relationship("GistFile", back_populates="images")


class GistFile(Table):
    """a table containing a gist's files"""
    __tablename__ = "gistfile"
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False)
    gist_id: Mapped[str] = mapped_column(ForeignKey(
        "gist.id"), nullable=False)  # Clé étrangère vers Gist
    name: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)

    # Ajout de la relation
    gist = relationship("Gist", back_populates="files")
    images = relationship("GistFileImage", back_populates="gistfile")


class Gist(Table):
    """a table containing gists"""
    __tablename__ = "gist"
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    embed_url: Mapped[str] = mapped_column(nullable=False)

    # Ajout de la relation
    files = relationship("GistFile", back_populates="gist")
