from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=4, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Register")


class AddUserStatusForm(FlaskForm):
    urconst = StringField("Urconst", validators=[DataRequired()])
    status = SelectField(
        "Status",
        choices=[
            ("neutral", "Neutral"),
            ("shadow-banned", "Shadow Banned"),
            ("trusted", "Trusted"),
            ("suspect", "Suspect"),
        ],
        validators=[DataRequired()],
    )
    reason = StringField("Reason", validators=[DataRequired()])
    submit = SubmitField("Add")


class EditStatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[
            ("neutral", "Neutral"),
            ("shadow-banned", "Shadow Banned"),
            ("trusted", "Trusted"),
            ("suspect", "Suspect"),
        ],
        validators=[DataRequired()],
    )
    reason = StringField("Reason")  # optional field
    submit = SubmitField("Update Status")


class EditUserPermsForm(FlaskForm):
    is_admin = SelectField(
        "Boolean",
        choices=[("true", "True"), ("false", "False")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Update User")
