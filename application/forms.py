from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    SelectField,
    BooleanField,
    StringField,
    PasswordField,
    FileField,
    SearchField,
)
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import InputRequired


class UploadForm(FlaskForm):
    photo = FileField(
        "Photo",
        validators=[
            InputRequired(),
            FileAllowed(["jpg", "jpeg", "png"], "Images only!"),
        ],
    )
    model = SelectField(
        "Model",
        validators=[InputRequired()],
        choices=[(31, "Small"), (128, "Large")],
    )


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    remember = BooleanField("Remember me")

    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

    submit = SubmitField("Sign Up")


class SortHistoryForm(FlaskForm):
    date_oldest_first = SelectField(
        "Date",
        validators=[InputRequired()],
        choices=[
            ("asc", "Ascending (Oldest first)"),
            ("desc", "Descending (Latest first)"),
        ],
    )
    model = SelectField(
        "Model",
        validators=[InputRequired()],
        choices=[(None, "*")] + [(31, "Small"), (128, "Large")],
    )
    label = SearchField()
    sort = SubmitField("Filter")
