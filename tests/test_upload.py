import os


import pytest
from faker import Faker
from flask import json

from application.utils import model_types

fake = Faker()

UPLOAD_TEST_COUNT = 100


def get_random_image():
    image_file = fake.random_element(pytest.image_files)

    # Prepare the files dictionary for multipart/form-data
    file = {}
    file_path = os.path.join(pytest.image_folder_path, image_file)
    file["file"] = (open(file_path, "rb"), image_file)

    return file


def get_random_non_image():
    non_image_file = fake.random_element(pytest.non_image_files)

    # Prepare the files dictionary for multipart/form-data
    file = {}
    file_path = os.path.join(pytest.non_image_folder_path, non_image_file)
    file["file"] = (open(file_path, "rb"), non_image_file)
    return file


# validity testing when get_random_image(), it is a valid image
# expected failure testing when get_random_non_image(), it is not a valid image.
@pytest.mark.parametrize(
    "data",
    [get_random_image() for _ in range(UPLOAD_TEST_COUNT)]
    + [
        pytest.param(
            get_random_non_image(),
            marks=pytest.mark.xfail(strict=True, reason="wrong file type"),
        )
        for _ in range(UPLOAD_TEST_COUNT)
    ],
)
@pytest.mark.order(0)
@pytest.mark.prediction
def test_upload(client, data, capsys):

    with capsys.disabled():
        data["model"] = fake.random_element(list(model_types.keys()))
        response = client.post(
            "/api/upload", data=data, content_type="multipart/form-data"
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

        response_body = json.loads(response.get_data(as_text=True))
        assert response_body["error"] is None
        assert response_body["success"]

        pytest.image_ids.append(response_body["success"]["image_id"])
