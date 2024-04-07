from db_scripts.data.chats import Chat
from db_scripts.data.messages import Message
from db_scripts.data.users import User
from db_scripts import db_session


class ContactCard:
    def __init__(self, chat):
        db_session.global_init("db/messenger.db")
        db_sess = db_session.create_session()
        contact = db_sess.query(User).get(chat.contact)
        self.id = chat.id
        if contact.nickname:
            self.showed_name = contact.nickname
        else:
            self.showed_name = contact.surname + " " + contact.name if contact.surname else contact.name
        forward = chat
        reverse = db_sess.query(Chat).filter(Chat.user_id == chat.contact, Chat.contact == chat.user_id).first()
        reverse = reverse.messages if reverse else None
        forward = forward.messages if forward else None
        if reverse and forward:
            self.last_message = max([reverse[-1], forward[-1]], key=lambda x: x.date_time).text
        elif reverse:
            self.last_message = reverse[-1].text
        elif forward:
            self.last_message = forward[-1].text
        else:
            self.last_message = ""
