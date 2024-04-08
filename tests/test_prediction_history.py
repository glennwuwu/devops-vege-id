from datetime import datetime
import random
import urllib
import os


import pytest
from faker import Faker
from flask import json

from application import db, utils, bcrypt
from application.utils import model_types
from application.data_models import User, Image, Confidence

fake = Faker()

PREDICTION_HISTORY_TEST_COUNT = 100


# consistency testing and validity testing
@pytest.mark.parametrize("index", [i for i in range(PREDICTION_HISTORY_TEST_COUNT)])
@pytest.mark.order(1)
@pytest.mark.prediction
def test_prediction_history(client, index, capsys):

    with capsys.disabled():
        image_id = pytest.image_ids[index]
        data = {"image_id": image_id}
        with db.session.no_autoflush:
            response_1 = client.get("/api/prediction", json=data)

        assert response_1.status_code == 200
        assert response_1.headers["Content-Type"] == "application/json"

        response_1_body = json.loads(response_1.get_data(as_text=True))
        assert response_1_body["success"]["prediction_name"]
        assert response_1_body["success"]["confidence"]
        assert response_1_body["error"] is None

        with db.session.no_autoflush:
            response_2 = client.get("/api/prediction", json=data)

        assert response_2.status_code == 200
        assert response_2.headers["Content-Type"] == "application/json"

        response_2_body = json.loads(response_2.get_data(as_text=True))
        assert response_2_body["success"]["prediction_name"]
        assert response_2_body["success"]["confidence"]
        assert response_2_body["error"] is None

        assert (
            response_1_body["success"]["prediction_name"]
            == response_2_body["success"]["prediction_name"]
        )
        assert response_1_body["error"] == response_2_body["error"]


# validiting testing
@pytest.mark.parametrize("index", [i for i in range(PREDICTION_HISTORY_TEST_COUNT)])
@pytest.mark.order(1)
@pytest.mark.prediction
def test_delete_prediction_history(client, index, capsys):

    with capsys.disabled():
        image_id = pytest.image_ids[index]
        data = {"image_id": image_id}
        with db.session.no_autoflush:
            response = client.delete("/api/prediction", json=data)

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

        response_body = json.loads(response.get_data(as_text=True))
        assert response_body["error"] is None
        assert response_body["success"]

        with db.session.no_autoflush:
            response_2 = client.get("/api/prediction", json=data)

        assert response_2.status_code == 200
        assert response_2.headers["Content-Type"] == "application/json"

        response_2_body = json.loads(response_2.get_data(as_text=True))
        assert response_2_body["success"] is None
        assert response_2_body["error"]


# expected failure testing
@pytest.mark.parametrize("index", [i for i in range(PREDICTION_HISTORY_TEST_COUNT)])
@pytest.mark.order(1)
@pytest.mark.prediction
@pytest.mark.xfail(strict=True)
def test_get_prediction_hiory_failure(client, index, capsys):

    with capsys.disabled():
        image_id = fake.random_int(min=10000)
        data = {"image_id": image_id}
        with db.session.no_autoflush:
            response_1 = client.get("/api/prediction", json=data)

        assert response_1.status_code == 200
        assert response_1.headers["Content-Type"] == "application/json"

        response_1_body = json.loads(response_1.get_data(as_text=True))
        assert response_1_body["success"]["prediction_name"]
        assert response_1_body["success"]["confidence"]
        assert response_1_body["error"] is None

        with db.session.no_autoflush:
            response_2 = client.get("/api/prediction", json=data)

        assert response_2.status_code == 200
        assert response_2.headers["Content-Type"] == "application/json"

        response_2_body = json.loads(response_2.get_data(as_text=True))
        assert response_2_body["success"]["prediction_name"]
        assert response_2_body["success"]["confidence"]
        assert response_2_body["error"] is None

        assert (
            response_1_body["success"]["prediction_name"]
            == response_2_body["success"]["prediction_name"]
        )
        assert response_1_body["error"] == response_2_body["error"]
