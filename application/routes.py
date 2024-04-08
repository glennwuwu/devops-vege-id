from io import BytesIO
import cv2

from flask import (
    render_template,
    request,
    flash,
    url_for,
    redirect,
    abort,
    session,
    send_file,
)
from flask_login import login_user, logout_user, login_required, current_user

from application import app, login_manager, utils
from application.data_models import User, Image
from application.forms import (
    UploadForm,
    LoginForm,
    RegisterForm,
    SortHistoryForm,
)
from application.utils import (
    order_by_date,
    filter_label,
    filter_model,
    model_types,
    class_keys,
)


# Handles http://127.0.0.1:5000/
@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/about")
def index_page():
    return render_template(
        "index.html", docs=True, username=utils.get_username(current_user)
    )


@app.route("/history", methods=["GET", "POST"])
@login_required
def history_page():
    # Get parameters from the request and initialize the form
    page_number = int(request.args.get("page") or 1)

    form = SortHistoryForm()

    date_order = request.args.get("date_order")
    model_type = request.args.get("model")
    label = request.args.get("label")

    print(f"Date Order: {date_order}\nModel Type: {model_type}\nLabel: {label}")

    # Set form data based on request or form defaults
    date_order = form.date_oldest_first.data or date_order  # asc or desc
    form.date_oldest_first.data = date_order

    model_type = form.model.data or model_type  # 31 or 128 or None
    if model_type is not None and model_type != "None":
        model_name = model_types[int(model_type)]
    else:
        model_name = None
    form.model.data = model_type

    if form.label.data == "" or form.label.data is None:
        label = ""
    else:
        label = form.label.data
    form.label.data = label

    # Handle label case sensitivity and mapping
    lower_case_keys = {k.lower(): v for k, v in class_keys.items()}
    if label.lower() in lower_case_keys:
        label = lower_case_keys[label.lower()]
    elif label != "":
        label = -1

    suggestions = list(class_keys.keys())

    # Set up pagination and handle potential errors
    prev_page = page_number - 1
    next_page = page_number + 1

    items_per_page = 10

    image_query = Image.query.filter_by(user_id=current_user.id)

    image_query = order_by_date(image_query, date_order)
    image_query = filter_model(image_query, model_name)
    image_query = filter_label(image_query, label)

    while True:
        try:
            pagination = image_query.paginate(
                page=page_number, per_page=items_per_page, max_per_page=items_per_page
            )
            paginated_images = pagination.items

            if len(paginated_images) == 0:
                print("No matching images.")

            for i, image in enumerate(paginated_images):
                paginated_images[i].label = utils.get_class_label(image.label)

            break
        except:
            page_number -= 1

    return render_template(
        "history.html",
        page_number=page_number,
        form=form,
        suggestions=suggestions,
        username=utils.get_username(current_user),
        predictions=paginated_images,
        pagination=pagination,
        prev_page=prev_page,
        next_page=next_page,
    )


@app.route("/upload", methods=["GET"])
@login_required
def upload_image():
    form = UploadForm()
    return render_template(
        "upload.html", upload=True, form=form, username=utils.get_username(current_user)
    )


@app.route("/upload", methods=["POST"])
@login_required
def uploaded_image():
    form = UploadForm()

    if form.validate_on_submit():
        photo = form.photo.data
        model_size = int(form.model.data)

        try:
            model_type, color_image_stream, prediction, confidence, prediction_time = (
                utils.get_prediction_meta(model_size, photo)
            )
        except:
            prediction = None

        if prediction is not None:
            image, _ = utils.store_prediction(
                model_type,
                color_image_stream,
                prediction,
                confidence,
                prediction_time,
                current_user.id,
            )

            return redirect(url_for("display_prediction", image_id=image.id))

    flash("Error in getting prediction. Try again.", "danger")
    return redirect(url_for("upload_image"))


@app.route("/prediction", methods=["GET"])
@login_required
def display_prediction():
    image_id = request.args.get("image_id")
    image = utils.get_image_entry(image_id)
    if current_user.id == image.user_id:
        prediction_name = utils.get_class_label(image.label)
        confidence = utils.get_confidence(image.id)
        return render_template(
            "prediction.html",
            image_id=image_id,
            label=prediction_name,
            image=image,
            confidence=confidence,
            username=utils.get_username(current_user),
        )
    return abort(404)


@app.route("/prediction/delete/<int:image_id>", methods=["GET", "POST"])
def delete_prediction(image_id):
    utils.delete_image_by_id(image_id)

    return redirect(url_for("history_page"))


@app.route("/static/image/")
@login_required
def display_processed_image():
    # Retrieve the processed image from the BytesIO object
    image_id = request.args.get("image_id")
    image = utils.get_image_entry(image_id)
    if current_user.id == image.user_id:
        if image:
            image_stream = BytesIO(image.image_data)

            # Return the image using send_file
            return send_file(image_stream, mimetype="image/png")

    return abort(404)


@app.route("/user/sign_in", methods=["GET", "POST"])
def signin_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if utils.verify_signin_user(user, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Sign in successful!", "success")
            return redirect(url_for("upload_image"))
        else:
            flash(
                "Sign in unsuccessful. Please check your username and password.",
                "danger",
            )
    return render_template(
        "signin.html",
        title="Sign In",
        form=form,
        username=utils.get_username(current_user),
    )


@app.route("/user/sign_up", methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    next_page = request.args.get("next")
    if form.validate_on_submit():
        error, success = utils.register_user(form.username.data, form.password.data)
        if success:
            flash("Sign up successful! You can now log in.", "success")
            return redirect(url_for("signin_page"))
        else:
            print(error)
            if error["error"] == "IntegrityError":
                flash(
                    error["message"],
                    "danger",
                )
    return render_template(
        "signup.html", form=form, username=utils.get_username(current_user)
    )


@app.route("/user/sign_out")
def signout_page():
    logout_user()
    return redirect(url_for("signin_page"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", username=utils.get_username(current_user)), 404


# for users without appropriate credentials
@login_manager.unauthorized_handler
def unauthorized_callback():
    print(request)
    session["next"] = request.url
    return redirect("/user/sign_in")


def redirect_to_requested():
    if current_user.is_authenticated:
        try:
            next_page = session["next"]
        except:
            return
        if next_page is not None:
            session["next"] = None
            return redirect(next_page)
