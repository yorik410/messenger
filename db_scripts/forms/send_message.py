from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, IntegerField, DateField, \
    TextAreaField
from wtforms.validators import DataRequired, Length


class SendMessageForm(FlaskForm):
    text = TextAreaField('Send message',
                         validators=[DataRequired(),
                                     Length(max=3000, message="You can't enter more than 3000 symbols")])

    submit = SubmitField('Send >')
