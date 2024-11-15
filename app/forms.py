from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

class NameForm(FlaskForm):
    name = StringField("Email, phone, or Skype", validators=None)
    submit = SubmitField("Next")


class PasswordForm(FlaskForm):
    password = PasswordField("Enter password", validators=None)
    submit = SubmitField("Sign in")
