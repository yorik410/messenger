from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import Flask, jsonify, make_response
from flask import redirect, request
import flask
from db_scripts import db_session

from db_scripts.data.users import User
from db_scripts.data.chats import Chat
from db_scripts.data.messages import Message
from db_scripts.data.notifications import Notification
from db_scripts.data.avatars import Avatar

from db_scripts.forms.login_form import LoginForm, RegisterForm, EditProfileForm
from db_scripts.forms.add_chat import AddChatForm
from db_scripts.forms.change_password import ChangePasswordForm
from db_scripts.forms.send_message import SendMessageForm

from scripts.cards import ContactCard, NoticeCard

import os
import io
import sys
import datetime
import signal
from PIL import Image, ImageChops


static_path = os.path.join("\\".join(sys.argv[0].split("\\")[:-1]), "src")
app = Flask(__name__, static_folder=static_path)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()

login_manager.init_app(app)


def render_template(*args, **kwargs):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        avatar = db_sess.query(Avatar).filter(Avatar.user_id == current_user.id).first()
    else:
        avatar = None
    return flask.render_template(*args, **kwargs, avatar=avatar.id if avatar else None)


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
        db_sess.close()
        if user and user.check_password(form.password.data):
            if current_user.is_authenticated:
                logout_user()
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Wrong login or password",
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
        if len(form.nickname.data) < 5:
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="Nickname length should be more than 4 characters")
        if len(form.nickname.data) > 15:
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="Nickname length should be less than 16 characters")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            db_sess.close()
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="User with this email already exists")
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            db_sess.close()
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
        db_sess.close()
        return redirect('/login')
    return render_template('register.html', title='Register', form=form)


@app.route("/")
@app.route("/chats", methods=["GET", "POST"])
def index():
    visible_notif = all((request.args.get("visible_notif", type=bool, default=False), current_user.is_authenticated))
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        contacts = list(map(lambda x: ContactCard(x),
                            db_sess.query(Chat).filter(Chat.user_id == current_user.id).all()))
        notifications = list(map(lambda x: NoticeCard(x),
                                 db_sess.query(Notification).filter(Notification.user_id == current_user.id).all()))
    else:
        contacts = []
        notifications = []
    return render_template("index.html", title="Chats", contacts=contacts, notifications=notifications,
                           notifications_default_visible=visible_notif)


@app.route("/chats/<int:id_>", methods=['GET', 'POST'])
def chat_by_id(id_: int):
    visible_notif = all((request.args.get("visible_notif", type=bool, default=False), current_user.is_authenticated))
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        if db_sess.query(Chat).get(id_).user_id != current_user.id:
            return redirect("/")
        contacts = list(map(lambda x: ContactCard(x),
                            db_sess.query(Chat).filter(Chat.user_id == current_user.id).all()))
        chat = db_sess.query(Chat).get(id_)
        forward = chat.messages if chat else []
        reverse = db_sess.query(Chat).filter(Chat.user_id == chat.contact,
                                             Chat.contact == chat.user_id).first()
        reverse = reverse.messages if reverse else []
        messages = list(sorted(forward + reverse, key=lambda x: x.date_time))

        notifications = list(map(lambda x: NoticeCard(x),
                                 db_sess.query(Notification).filter(Notification.user_id == current_user.id).all()))

        form = SendMessageForm()
        if form.validate_on_submit():
            message_text = form.text.data.strip()
            if not message_text:
                db_sess.close()
                return render_template('chat.html', id=id_, title="Chats",
                                       contacts=contacts, messages=messages, notifications=notifications, chat_id=id_,
                                       user_id=current_user.id, form=form, notifications_default_visible=visible_notif)
            mess = Message()
            mess.chat_id = id_
            mess.text = message_text
            mess.date_time = datetime.datetime.now()
            db_sess.add(mess)
            db_sess.commit()
            db_sess.close()
            return redirect(f"/chats/{id_}")
        return render_template('chat.html', id=id_, title="Chats",
                               contacts=contacts, messages=messages, notifications=notifications, chat_id=id_,
                               user_id=current_user.id, form=form, notifications_default_visible=visible_notif)
    else:
        contacts = []
        notifications = []
    return render_template("index.html", title="Chats", contacts=contacts, notifications=notifications)


@app.route("/add_chat", methods=['GET', 'POST'])
def add_chat():
    form = AddChatForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not current_user.is_authenticated:
            db_sess.close()
            return render_template('add_chat.html',
                                   message="You have not logged in, yet",
                                   form=form,
                                   title="Add chat")
        user = db_sess.query(User).filter(User.nickname == form.nickname.data).all()
        if len(user) == 0:
            db_sess.close()
            return render_template('add_chat.html',
                                   message="Wrong nickname",
                                   form=form,
                                   title="Add chat")
        user = user[0]
        if current_user.id == user.id:
            db_sess.close()
            return render_template('add_chat.html',
                                   message="You cannot add yourself in chat",
                                   form=form,
                                   title="Add chat")
        if len(db_sess.query(Chat).filter(Chat.user_id == current_user.id, Chat.contact == user.id).all()) > 0:
            db_sess.close()
            return render_template('add_chat.html',
                                   message="You already have this chat",
                                   form=form,
                                   title="Add chat")
        chat = Chat(
            user_id=current_user.id,
            contact=user.id
        )
        db_sess.add(chat)

        notification = Notification(
            user_id=user.id,
            text=f"You have been invited to chat with {db_sess.query(User).get(current_user.id).nickname}",
            type="Invitation",
            buttons="accept;reject",
            sender_id=current_user.id
        )
        db_sess.add(notification)
        db_sess.commit()
        db_sess.close()
        return redirect("/")

    return render_template("add_chat.html", title="Add chat", form=form)


@app.route("/notif_sub_ok/<int:id_>", methods=["POST", "GET"])
def notification_submit_ok(id_: int):
    chat_id = request.args.get("chat", type=int, default=-1)
    db_sess = db_session.create_session()
    if current_user.is_authenticated and current_user.id == db_sess.query(Notification).get(id_).user_id:
        db_sess.query(Notification).filter(Notification.id == id_).delete()
        db_sess.commit()
    url = "/?visible_notif=true" if chat_id == -1 else f"/chats/{chat_id}?visible_notif=true"
    return redirect(url)


@app.route("/notif_sub_ac/<int:id_>", methods=["POST", "GET"])
def notification_submit_ac(id_: int):
    chat_id = request.args.get("chat", type=int, default=-1)
    db_sess = db_session.create_session()
    notif = db_sess.query(Notification).get(id_)
    if current_user.is_authenticated and current_user.id == notif.user_id:
        chat = Chat(
            user_id=current_user.id,
            contact=notif.sender_id
        )
        db_sess.add(chat)
        notification = Notification(
            user_id=notif.sender_id,
            text=f"{current_user.nickname} accepted your invitation",
            type="Notification",
            buttons="ok",
            sender_id=current_user.id
        )
        db_sess.add(notification)
        db_sess.query(Notification).filter(Notification.id == id_).delete()
        db_sess.commit()
    url = "/?visible_notif=true" if chat_id == -1 else f"/chats/{chat_id}?visible_notif=true"
    return redirect(url)


@app.route("/notif_sub_rj/<int:id_>", methods=["POST", "GET"])
def notification_submit_rj(id_: int):
    chat_id = request.args.get("chat", type=int, default=-1)
    db_sess = db_session.create_session()
    notif = db_sess.query(Notification).get(id_)
    if current_user.is_authenticated and current_user.id == notif.user_id:
        db_sess.query(Chat).filter(Chat.user_id == notif.sender_id, Chat.contact == current_user.id).delete()
        notification = Notification(
            user_id=notif.sender_id,
            text=f"{current_user.nickname} rejected your invitation",
            type="Notification",
            buttons="ok",
            sender_id=current_user.id
        )
        db_sess.add(notification)
        db_sess.query(Notification).filter(Notification.id == id_).delete()
        db_sess.commit()
    url = "/?visible_notif=true" if chat_id == -1 else f"/chats/{chat_id}?visible_notif=true"
    return redirect(url)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    edit = request.args.get("edit", type=bool, default=False)
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        form = EditProfileForm()
        form.email.data = current_user.email
        avatar = db_sess.query(Avatar).filter(Avatar.user_id == current_user.id).first()
        if form.validate_on_submit():
            if form.avatar.data:
                image = Image.open(io.BytesIO(form.avatar.data.read()))
                image = image.resize((532, 532))
                if avatar:
                    try:
                        diff = ImageChops.difference(Image.open(f"./src/img/avatars/#{avatar.id}.png"), image).getbbox()
                    except ValueError:
                        diff = True
                else:
                    diff = True
                try:
                    difft = ImageChops.difference(Image.open(f"./src/img/user-profile-icon.png"), image).getbbox()
                except ValueError:
                    difft = True
                if diff and difft:
                    if not avatar:
                        avatar = Avatar()
                        avatar.user_id = current_user.id
                        db_sess.add(avatar)
                        db_sess.commit()
                    avatar = db_sess.query(Avatar).filter(Avatar.user_id == current_user.id).first()
                    image.save(f"./src/img/avatars/#{avatar.id}.png")

            temp = ["email", "nickname", "name", "surname", "age"]
            for i in temp:
                if (eval(f"form.{i}.data") != eval(f"current_user.{i}") and not (eval(f"current_user.{i}") is None
                                                                                 and not eval(f"form.{i}.data"))):
                    break
            else:
                return redirect("/profile")

            if "@" in form.nickname.data:
                return render_template("profile.html", title="Profile", edit=edit, form=form,
                                       message='Don\'t use "@" in nickname')

            if len(form.nickname.data) < 5:
                return render_template("profile.html", title="Profile", edit=edit, form=form,
                                       message="Nickname length should be more than 4 characters")

            if len(form.nickname.data) > 15:
                return render_template("profile.html", title="Profile", edit=edit, form=form,
                                       message="Nickname length should be less than 16 characters")

            if db_sess.query(User).filter(User.nickname == form.nickname.data, User.id != current_user.id).first():
                db_sess.close()
                return render_template("profile.html", title="Profile", edit=edit, form=form,
                                       message="User with this nickname already exists")

            user = db_sess.query(User).get(current_user.id)
            user.nickname = form.nickname.data
            user.name = form.name.data
            user.surname = form.surname.data if form.surname.data else None
            user.age = form.age.data
            user.modified_date = datetime.datetime.now()
            db_sess.commit()
            return redirect("/profile")
        else:
            form.nickname.data = current_user.nickname
            form.name.data = current_user.name
            form.surname.data = current_user.surname if current_user.surname else ""
            form.age.data = current_user.age
            return render_template("profile.html", title="Profile", edit=edit, form=form)
    return redirect("/")


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if current_user.is_authenticated:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            if not current_user.check_password(form.old_password.data):
                return render_template("change_password.html", title="Change password", form=form,
                                       message="Wrong previous password")
            if form.new_password.data != form.new_password_again.data:
                return render_template("change_password.html", title="Change password", form=form,
                                       message="Passwords don't match")
            if len(form.new_password.data) < 8:
                return render_template("change_password.html", title="Change password", form=form,
                                       message="Password length should be more than 7 characters")
            if form.new_password.data == form.old_password.data:
                return render_template("change_password.html", title="Change password", form=form,
                                       message="Your new password matches with previous one")
            db_sess = db_session.create_session()
            user = db_sess.query(User).get(current_user.id)
            user.set_password(form.get_hashed_password())
            db_sess.commit()
            return redirect("/profile")
        return render_template("change_password.html", title="Change password", form=form)
    return redirect("/")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/update_from_github")
def update():
    if current_user.id == 1:
        with open("notif.txt", "w") as file:
            file.write("r")
            file.close()
        os.kill(os.getpid(), signal.SIGINT)
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/messenger.db")
    # app.run(port=8080, host='127.0.0.1')
    # ngrok http --domain=loved-cute-dodo.ngrok-free.app 8080
    app.run(port=8080, host='0.0.0.0')
