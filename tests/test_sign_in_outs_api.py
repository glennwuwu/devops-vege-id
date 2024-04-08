import pytest
from faker import Faker
from flask import json

fake = Faker()

CREATED_USERS_COUNT = 100
CONSISTENCY_TEST_COUNT = 2


# sign up and sign in with the same username and credentials to verify that those systems are working
# validity testing
@pytest.mark.parametrize(
    "run_type",
    ["normal"] * CREATED_USERS_COUNT,
)
@pytest.mark.user
def test_api_register_and_sign_in(client, run_type, capsys):
    with capsys.disabled():  # so that print() statements will not be caught by pytest
        username = None
        while username in pytest.usernames or username is None:
            username = fake.user_name()
        pytest.usernames.append(username)
        data = {
            "username": username,
            "password": fake.password(),
        }

        response = client.post("/api/user/sign_up", json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["error"] is None or result["error"]["error"] == "IntegrityError"
        assert "success" in result

        response = client.post("/api/user/sign_in", json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["success"] is True


# iterate over the list of created users for each run (consistency testing)
# prevent registering with same username
# expected failure testing
@pytest.mark.parametrize(
    "run_type",
    ["normal"] * CONSISTENCY_TEST_COUNT,
)
@pytest.mark.user
def test_api_register_existing(client, run_type, capsys):
    with capsys.disabled():
        for username in pytest.usernames:
            data = {
                "username": username,
                "password": fake.password(),
            }
            response = client.post("/api/user/sign_up", json=data)
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result["error"]["error"] == "IntegrityError"
            assert result["success"]["user_id"] is None


# iterate over the list of created users for each run (consistency testing)
# prevent signing in with incorrect credentials
# expected failure testing
@pytest.mark.parametrize(
    "run_type",
    ["normal"] * CONSISTENCY_TEST_COUNT,
)
@pytest.mark.user
def test_api_sign_in_incorrect(client, run_type, capsys):
    with capsys.disabled():
        for username in pytest.usernames:
            data = {
                "username": username,
                "password": fake.password(),
            }
            response = client.post("/api/user/sign_in", json=data)
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result["success"] is False
