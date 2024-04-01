from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import Flask, jsonify, make_response
from flask import render_template, redirect
from db_scripts import db_session
from db_scripts.data.users import User
from db_scripts.forms.login_form import LoginForm, RegisterForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if "@" in form.email.data:
            user = db_sess.query(User).filter(User.email == form.email.data).first()
        else:
            user = db_sess.query(User).filter(User.nickname == form.email.data).first()
        if user and user.check_password(form.password.data):
            if current_user.is_authenticated:
                logout_user()
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Wrong "
                                       "login or password",
                               form=form)
    return render_template('login.html', title='Log in', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="Passwords don't match")
        if len(form.password.data) < 8:
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="Password length should be more than 7 characters")
        if "@" in form.nickname.data:
            return render_template('register.html', title='Register',
                                   form=form,
                                   message='Don\'t use "@" in nickname')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="User with this email already exists")
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="User with this nickname already exists")

        user = User(
            email=form.email.data,
            nickname=form.nickname.data,
            surname=form.surname.data if form.surname.data else None,
            name=form.name.data,
            age=form.age.data
        )
        user.set_password(form.get_hashed_password())
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Register', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()

    return render_template("index.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/messenger.db")
    app.run(port=8080, host='127.0.0.1')