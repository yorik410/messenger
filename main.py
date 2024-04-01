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
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # if form.password.data != form.password_again.data:
        #     return render_template('register.html', title='Регистрация',
        #                            form=form,
        #                            message="Пароли не совпадают")
        # db_sess = db_session.create_session()
        # if db_sess.query(User).filter(User.email == form.email.data).first():
        #     return render_template('register.html', title='Регистрация',
        #                            form=form,
        #                            message="Такой пользователь уже есть")
        # user = User(
        # )
        # form.set_password(form.password.data)
        # user.set_password(form.hashed_password)
        # db_sess.add(user)
        # db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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