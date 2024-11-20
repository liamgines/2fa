from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

class NameForm(FlaskForm):
    name = StringField("Email, if you dare", validators=None)
    submit = SubmitField("Next")


class PasswordForm(FlaskForm):
    password = PasswordField("Enter password for a change", validators=None)
    submit = SubmitField("Sign in")
