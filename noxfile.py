import nox


@nox.session
def tests(session):
    session.install("-r", "requirements.txt")
    session.install("pytest")
    session.install("pytest-cov")
    session.run("pytest", "--cov=rcdesign", "tests/")
