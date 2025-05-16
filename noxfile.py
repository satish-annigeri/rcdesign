import sys
import os


import nox


sys.path.insert(0, os.path.abspath("src"))

python38 = "/home/satish/.local/share/uv/python/cpython-3.8.20-linux-x86_64-gnu/bin/python3.8"
python39 = "/home/satish/.local/share/uv/python/cpython-3.9.22-linux-x86_64-gnu/bin/python3.9"
python310 = "/home/satish/.local/share/uv/python/cpython-3.10.17-linux-x86_64-gnu/bin/python3.10"


@nox.session(python="3.12")
def docs(session: nox.Session) -> None:
    """Build the documentation."""
    requirements = nox.project.load_toml("pyproject.toml")["dependency-groups"]["docs"]

    session.install(*requirements)
    session.install("-e", ".")
    session.run("mkdocs", "build")


@nox.session(python="3.12")
def tests(session):
    """Run unit tests using pytest."""

    session.install("pytest")  # Install pytest inside the session
    session.install("-e", ".")
    session.run("pytest")
