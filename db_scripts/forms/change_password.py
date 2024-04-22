from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, IntegerField, DateField, \
    TextAreaField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash, generate_password_hash


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Previous password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    new_password_again = PasswordField('New password again', validators=[DataRequired()])

    submit = SubmitField('Change')

    def get_hashed_password(self):
        return generate_password_hash(self.new_password.data)
