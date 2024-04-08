import os
import pytest


from application import db, utils
from application import app as flask_app


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    print(flask_app.config["SQLALCHEMY_DATABASE_URI"])

    yield flask_app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def cleanup(request, app):
    created_entities = []

    def fin():
        with app.app_context():
            for entity in created_entities:
                db.session.delete(entity)
            db.session.commit()

    request.addfinalizer(fin)

    return created_entities


def pytest_configure(config):
    # configure custom pytest marks
    config.addinivalue_line("markers", "db: mark test to run only db tests")
    config.addinivalue_line(
        "markers", "prediction: mark test to run only prediction tests"
    )
    config.addinivalue_line("markers", "user: mark test to run only user tests")
    config.addinivalue_line("markers", "rpa: mark test to run only RPA tests")

    pytest.usernames = []
    pytest.image_ids = []
    pytest.rpa_image_ids = []
    pytest.user_id = 1

    image_relative_folder_path = "/tests/assets/images/"
    pytest.image_folder_path = os.getcwd() + image_relative_folder_path

    # Get a list of all files in the folder
    pytest.image_files = [
        f
        for f in os.listdir(pytest.image_folder_path)
        if os.path.isfile(os.path.join(pytest.image_folder_path, f))
    ]

    non_image_relative_folder_path = "/tests/assets/non-images/"
    pytest.non_image_folder_path = os.getcwd() + non_image_relative_folder_path

    pytest.non_image_files = [
        f
        for f in os.listdir(pytest.non_image_folder_path)
        if os.path.isfile(os.path.join(pytest.non_image_folder_path, f))
    ]


def pytest_addoption(parser):
    parser.addoption(
        "--loc",
        choices=["local", "CI"],
        default="local",
    )
    parser.addoption(
        "--browser",
        choices=["chrome", "firefox", "edge"],
        default="chrome",
    )


@pytest.fixture(scope="session")
def loc(request):
    """:returns true or false from --local option"""
    return request.config.getoption("--loc")


@pytest.fixture(scope="session")
def browser(request):
    """:returns true or false from --local option"""
    return request.config.getoption("--browser")


def pytest_sessionstart(session):
    # Establish a Flask application context before the session starts
    flask_app.app_context().push()


def pytest_sessionfinish(session, exitstatus):
    # Clean up after the test session finishes
    with flask_app.app_context():
        if db.session.dirty or db.session.new:
            db.session.commit()
        for username in pytest.usernames:
            utils.delete_user_by_username(username)
        for image_id in pytest.image_ids:
            utils.delete_image_by_id(image_id)
