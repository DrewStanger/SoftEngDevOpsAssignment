from unittest.mock import Mock, patch
from app import app
import pytest


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Tests for core routes


def test_index_route(client):
    response = client.get("/")
    # User not logged in so expect 302 for redirect
    assert response.status_code == 302
    # Should be redirected to /login
    assert response.headers["Location"] == "/login"


def test_login_route(client):
    response = client.get("/login")
    assert response.status_code == 200
    # Check we render the contents
    assert b'<h2 class="p-2">Login</h2>' in response.data


def test_login_post_route(client):
    # Mock the authenticate_user() function to always return True for testing purposes
    with patch("app.authenticate_user", return_value=True):
        response = client.post(
            "/login", data={"username": "test_user", "password": "test_password"}
        )

    # Assert successful POST results in redirect to dashboard
    assert response.status_code == 302
    assert response.headers["Location"] == "/dashboard"
    # Reset the mock for authenticate_user() after the test
    patch.stopall()


def test_logout_route(client):
    # Set user is logged in
    with client.session_transaction() as session:
        session["name"] = "test_user"

    response = client.get("/logout")
    # 302 for redirect and / for the route
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    # Test that there is no logged in user
    with client.session_transaction() as session:
        assert session.get("name") is None


def test_logout_route_when_not_logged_in(client):
    # Set no user logged in
    with client.session_transaction() as session:
        session["name"] = None

    response = client.get("/logout")
    # If a user accesses this endpoint without being logged in we just redirect to the login page
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_dashboard_route(client):
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_add_status_route(client):
    response = client.get("/dashboard/add")
    assert response.status_code == 200


# Should fail as usernames must be unique
def test_register_route_user_exists(client):
    # Mock qeury showing that the user already exists
    mock_query_existing_user = Mock()
    mock_query_existing_user.first.return_value = True  # Simulate an existing user

    # Mock the db.session object
    mock_db_session = Mock()
    mock_db_session.query.return_value.filter.return_value = mock_query_existing_user

    # Apply the mocks
    with patch("app.db.session", mock_db_session):
        # POST a registration with an existing username
        response_existing_user = client.post(
            "/register", data={"username": "existing_user", "password": "test_password"}
        )

        assert response_existing_user.status_code == 302
        assert response_existing_user.headers["Location"] == "/register"
    # Reset the mocks after the test
    patch.stopall()


def test_register_route_new_user(client):
    mock_query_new_user = Mock()
    # Simulate user not existing
    mock_query_new_user.filter.return_value.first.return_value = None

    mock_db_session = Mock()

    # Mock the session
    mock_session = {}

    with patch("app.db.session", mock_db_session), patch("app.session", mock_session):
        # POST a registeration with a new username
        response_new_user = client.post(
            "/register", data={"username": "new_user", "password": "test_password"}
        )

        # succesful registeration returns redirect to login
        assert response_new_user.status_code == 302

    # Reset the mocks after the test
    patch.stopall()
