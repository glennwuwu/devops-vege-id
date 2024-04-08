from datetime import datetime
from io import BytesIO
import requests
import json
import time
import pytz
import numpy as np
import cv2
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from application import db, bcrypt
from application.data_models import User, Image, Confidence

# Constants
model_types = {31: "Small", 128: "Large"}

class_keys = {
    "Bean": 0,
    "Bitter Gourd": 1,
    "Bottle Gourd": 2,
    "Brinjal": 3,
    "Broccoli": 4,
    "Cabbage": 5,
    "Capsicum": 6,
    "Carrot": 7,
    "Cauliflower": 8,
    "Cucumber": 9,
    "Papaya": 10,
    "Potato": 11,
    "Pumpkin": 12,
    "Radish": 13,
    "Tomato": 14,
}

# URL endpoints for model predictions
urls = {
    31: "https://vegetable-classifier-service.onrender.com/v1/models/small:predict",
    128: "https://vegetable-classifier-service.onrender.com/v1/models/large:predict",
}


def get_current_time():
    # Get the current time in Asia/Singapore timezone
    return (
        datetime.utcnow()
        .replace(tzinfo=pytz.utc)
        .astimezone(pytz.timezone("Asia/Singapore"))
    )


def verify_signin_user(user, password):
    # Verify user credentials for sign-in
    return user and bcrypt.check_password_hash(user.password, password)


def register_user(username, password):
    # Register a new user and hash the password
    try:
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(
            username=username,
            password=hashed_password,
            registered_on=get_current_time(),
        )
        # Add the new user to the database
        db.session.add(user)
        db.session.commit()
        return None, user.id
    except IntegrityError:
        # Handle IntegrityError for duplicate usernames
        db.session.rollback()
        return {
            "error": "IntegrityError",
            "message": "Username already exists. Please choose a different username.",
        }, None


def get_username(current_user):
    try:
        username = current_user.username
    except AttributeError:
        return ""
    return username


def process_image(photo, size):
    image_stream = BytesIO(photo.read())
    img_array = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)

    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    resized_img = cv2.resize(img, (size, size))

    compressed_img = cv2.resize(img, (256, 256))

    grayscale_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)

    img_array = np.array(grayscale_img).reshape((size, size, 1))

    _, img_encoded = cv2.imencode(".png", grayscale_img)
    processed_image_stream = BytesIO(img_encoded).getvalue()

    _, img_encoded = cv2.imencode(".png", compressed_img)
    color_image_stream = BytesIO(img_encoded).getvalue()

    return img_array, processed_image_stream, color_image_stream


urls = {
    31: "https://vegetable-classifier-service.onrender.com/v1/models/small:predict",
    128: "https://vegetable-classifier-service.onrender.com/v1/models/large:predict",
}


def get_prediction(img_array, size, with_conf=False):
    if with_conf:
        output = None, None
    else:
        output = None

    img_array = img_array.tolist()
    data = json.dumps(
        {"signature_name": "serving_default", "instances": [img_array]}
    )  # see [C]
    headers = {"content-type": "application/json"}

    try:
        json_response = requests.post(
            urls[size], data=data, headers=headers, timeout=180
        )
        completed = True
    except requests.Timeout:
        return output
    except requests.ConnectionError:
        return output

    try:
        predictions = json.loads(json_response.content.decode("utf-8"))["predictions"]
    except Exception as e:
        return output

    if json_response.status_code == 200:
        output = int(np.argmax(predictions))
        if with_conf:
            output = (output, predictions)
    return output


def get_prediction_meta(model_size, photo):
    model_type = model_types[model_size]

    img_array, _, color_image_stream = process_image(photo, model_size)

    prediction, confidence = get_prediction(img_array, model_size, with_conf=True)
    prediction_time = get_current_time()

    return model_type, color_image_stream, prediction, confidence, prediction_time


def store_prediction(
    model_type, color_image_stream, prediction, confidence, prediction_time, user_id
):
    image = Image(
        image_data=color_image_stream,
        label=prediction,
        predicted_on=prediction_time,
        prediction_model=model_type,
        user_id=user_id,
    )
    db.session.add(image)
    db.session.commit()

    confidence = list(enumerate(confidence[0]))
    confidence = sorted(confidence, key=lambda x: x[1], reverse=True)

    for prediction_class, prediction_confidence in confidence[:5]:
        conf = Confidence(
            prediction_class=prediction_class,
            prediction_confidence=prediction_confidence,
            image_id=image.id,
        )

        db.session.add(conf)
        db.session.commit()

    return image, conf


def get_class_label(prediction):
    if isinstance(prediction, int):
        inverted_class_keys = {v: k for k, v in class_keys.items()}
        return inverted_class_keys[prediction]
    return prediction


def get_image_entry(image_id):
    image = db.session.query(Image).filter(Image.id == image_id).all()
    if isinstance(image, list):
        if len(image) > 0:
            return image[0]
    return False


def get_confidence(image_id):
    confidence = (
        db.session.query(Confidence)
        .filter(Confidence.image_id == image_id)
        .order_by(Confidence.prediction_confidence.desc())
        .all()
    )
    for conf in confidence:
        conf.prediction_class = get_class_label(conf.prediction_class)
        conf.prediction_confidence = round(conf.prediction_confidence * 10000) / 100

    return confidence


# history sort
def order_by_date(query, date_order):
    if date_order == "asc":
        return query.order_by(Image.predicted_on)
    elif date_order == "desc":
        return query.order_by(desc(Image.predicted_on))
    else:
        return query


def filter_model(query, model_name):
    if model_name is not None and model_name != "None":
        return query.filter(Image.prediction_model == model_name)
    else:
        return query


def filter_label(query, label):
    if label is not None and label != "None" and label != "":
        return query.filter(Image.label == label)
    else:
        return query


def check_database_status():
    try:
        db.session.execute("SELECT 1")
        return True  # Connection is successful
    except Exception as e:
        print(f"Error checking database status: {e}")
        time.sleep(1)
        return False  # Connection is not successful


def delete_user_by_username(username):
    # Delete user by username
    user = User.query.filter_by(username=username).first()
    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            # Handle database error during user deletion
            db.session.rollback()
    return False


def delete_image_by_id(image_id):
    # Delete image and associated confidences by image_id
    conf = Confidence.query.filter_by(image_id=image_id).all()
    for c in conf:
        db.session.delete(c)
    db.session.commit()
    image = get_image_entry(image_id)
    if image is not False:
        db.session.delete(image)
        db.session.commit()


def delete_user_like(substring):
    users_to_delete = User.query.filter(User.username.like(f"%{substring}%")).all()

    # Delete each user
    for user in users_to_delete:
        images_to_delete = Image.query.filter(Image.user_id == user.id).all()
        for image in images_to_delete:
            delete_image_by_id(image.id)
        db.session.delete(user)

    # Commit the changes to the database
    db.session.commit()
