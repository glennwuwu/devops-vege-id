from application import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)

    def get_id(self):
        return self.id


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_data = db.Column(db.LargeBinary, nullable=False)
    label = db.Column(db.Integer, nullable=False)
    prediction_model = db.Column(db.String(20), nullable=False)
    predicted_on = db.Column(db.DateTime, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", backref=db.backref("User", lazy=True))


class Confidence(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prediction_class = db.Column(db.Integer, nullable=False)
    prediction_confidence = db.Column(db.Float, nullable=False)

    image_id = db.Column(db.Integer, db.ForeignKey("image.id"), nullable=False)

    image = db.relationship("Image", backref=db.backref("Image", lazy=True))
