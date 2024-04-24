from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, IntegerField, DateField, \
    TextAreaField, FileField
from wtforms.validators import DataRequired
import wtforms.validators as validators
from werkzeug.security import check_password_hash, generate_password_hash


class LoginForm(FlaskForm):
    email = StringField('Nickname or email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')
    hashed_password = ""

    def set_password(self, password):  # Вроде не нужно
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):  # Вроде не нужно
        return check_password_hash(self.hashed_password, password)


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    nickname = StringField('Nickname', validators=[DataRequired()])
    surname = StringField('Surname (optional)')
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password',
                                   validators=[DataRequired()])
    submit = SubmitField('Register')

    hashed_password = ""

    def set_password(self, password):  # Вроде не нужно
        self.hashed_password = generate_password_hash(password)

    def get_hashed_password(self):
        return generate_password_hash(self.password.data)

    def check_password(self, password):  # Вроде не нужно
        return check_password_hash(self.hashed_password, password)


class EditProfileForm(FlaskForm):
    avatar = FileField("Avatar", validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    email = EmailField('Email', validators=[DataRequired()])
    nickname = StringField('Nickname', validators=[DataRequired()])
    surname = StringField('Surname (optional)')
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])

    submit = SubmitField('Submit edit')
