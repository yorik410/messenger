from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, IntegerField, DateField, \
    TextAreaField
from wtforms.validators import DataRequired


class AddChatForm(FlaskForm):
    nickname = StringField('User nickname', validators=[DataRequired()])

    submit = SubmitField('+ Add')
