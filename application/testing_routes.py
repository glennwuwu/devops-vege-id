from functools import wraps

from flask import (
    request,
    jsonify,
    abort,
)

from application import app, utils
from application.data_models import User
from application.utils import (
    model_types,
)


def only_testing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if the application is in testing mode
        if not app.config.get("TESTING"):
            abort(403)  # Forbidden if not in testing mode
        return func(*args, **kwargs)

    return wrapper


@app.route("/api/upload", methods=["POST"])
@only_testing
def api_post_upload():
    model_size = int(request.form.get("model"))
    model_type = model_types[model_size]

    model_type, color_image_stream, prediction, confidence, prediction_time = (
        utils.get_prediction_meta(model_size, request.files["file"])
    )

    if prediction is not None:
        image, _ = utils.store_prediction(
            model_type,
            color_image_stream,
            prediction,
            confidence,
            prediction_time,
            user_id=1,
        )

        return jsonify({"error": None, "success": {"image_id": image.id}})
    return jsonify({"error": True, "success": None}), 500


@app.route("/api/prediction", methods=["GET"])
@only_testing
def api_get_prediction():
    data = request.get_json()
    image_id = data["image_id"]
    image = utils.get_image_entry(image_id)
    if image:
        prediction_name = utils.get_class_label(image.label)
        confidence = utils.get_confidence(image.id)
        _confidence = []
        for conf in confidence:
            _confidence.append((conf.prediction_class, conf.prediction_confidence))
        return jsonify(
            {
                "error": None,
                "success": {
                    "prediction_name": prediction_name,
                    "confidence": _confidence,
                },
            }
        )
    return jsonify(
        {
            "error": "Image Missing",
            "success": None,
        }
    )


@app.route("/api/prediction", methods=["DELETE"])
@only_testing
def api_delete_prediction():
    data = request.get_json()
    image_id = data["image_id"]
    utils.delete_image_by_id(image_id)
    return jsonify(
        {
            "error": None,
            "success": True,
        }
    )


@app.route("/api/history", methods=["POST"])
@only_testing
def api_post_history():
    pass


@app.route("/api/user/sign_up", methods=["POST"])
@only_testing
def api_register_user():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    result = utils.register_user(username, password)
    return jsonify({"error": result[0], "success": {"user_id": result[1]}})


@app.route("/api/user/sign_in", methods=["POST"])
@only_testing
def api_signin_user():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    user = User.query.filter_by(username=username).first()
    return jsonify({"success": utils.verify_signin_user(user, password)})
