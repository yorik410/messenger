from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, IntegerField, DateField, TextAreaField
from wtforms.validators import DataRequired


class NotificationsForm(FlaskForm):
    ok = SubmitField('Ok')
    accept = SubmitField('Accept')
    reject = SubmitField('Reject')
