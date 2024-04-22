from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, IntegerField, DateField, \
    TextAreaField
from wtforms.validators import DataRequired


class SendMessageForm(FlaskForm):
    text = TextAreaField('Send message', validators=[DataRequired()])

    submit = SubmitField('Send >')
