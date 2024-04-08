import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from datetime import timedelta


# create the Flask app
app = Flask(__name__)

cors = CORS(app)

# load configuration from config.cfg
app.config.from_pyfile("config.cfg")

# csrf = CSRFProtect(app)

# create database
db = SQLAlchemy()

try:
    if os.environ["FLASK_ENV"] == "testing":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
except:
    print("FLASK_ENV not set, defaulting to prod")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["TESTING"] = False


from .data_models import User, Image, Confidence


with app.app_context():
    db.init_app(app)

    db.create_all()
    db.session.commit()
    print("Created Database!")

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

app.config["REMEMBER_COOKIE_DURATION"] = timedelta(
    days=7
)  # Example: Remember the user for 7 days


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# run the file routes.py
from application import routes, testing_routes

from application import utils

# clean up after rpa
with app.app_context():
    utils.delete_user_like("_rpa_user")
