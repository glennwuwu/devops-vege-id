from datetime import datetime

import pytest
from faker import Faker

from application import db, utils, bcrypt
from application.data_models import User, Image, Confidence

fake = Faker()


def generate_random_user():
    password = fake.password()
    return (
        User(
            username=fake.user_name(),
            password=bcrypt.generate_password_hash(password).decode("utf-8"),
            registered_on=datetime.utcnow(),
        ),
        password,
    )


def generate_random_image(user_id):
    return Image(
        image_data=fake.binary(length=32),
        label=fake.random_int(min=1, max=10),
        prediction_model=fake.word(),
        predicted_on=datetime.utcnow(),
        user_id=user_id,
    )


def generate_random_confidence(image_id):
    return Confidence(
        prediction_class=fake.random_int(min=1, max=10),
        prediction_confidence=fake.pyfloat(left_digits=2, right_digits=2),
        image_id=image_id,
    )


# validity testing
@pytest.mark.db
def test_user_model(app, cleanup):
    """Test the User model."""
    with app.app_context():
        user, password = generate_random_user()
        db.session.add(user)
        db.session.commit()

        retrieved_user = User.query.filter_by(username=user.username).first()
        assert retrieved_user is not None
        assert utils.verify_signin_user(retrieved_user, password)

        cleanup.append(user)


# validity testing
@pytest.mark.db
def test_image_model(app, cleanup):
    """Test the Image model."""
    with app.app_context():
        user, _ = generate_random_user()
        db.session.add(user)
        db.session.commit()

        image = generate_random_image(user.id)
        db.session.add(image)
        db.session.commit()

        retrieved_image = Image.query.filter_by(id=image.id).first()
        assert retrieved_image is not None
        assert retrieved_image.user.username == user.username

        cleanup.append(user)
        cleanup.append(image)


# validity testing
@pytest.mark.db
def test_confidence_model(app, cleanup):
    """Test the Confidence model."""
    with app.app_context():
        user, _ = generate_random_user()
        db.session.add(user)
        db.session.commit()

        image = generate_random_image(user.id)
        db.session.add(image)
        db.session.commit()

        confidence = generate_random_confidence(image.id)
        db.session.add(confidence)
        db.session.commit()

        retrieved_confidence = Confidence.query.filter_by(id=confidence.id).first()
        assert retrieved_confidence is not None
        assert retrieved_confidence.image.label == image.label

        cleanup.append(user)
        cleanup.append(image)
        cleanup.append(confidence)
