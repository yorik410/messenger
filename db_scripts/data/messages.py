import sqlalchemy
import datetime
from sqlalchemy import orm
from db_scripts.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Message(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("chats.id"))
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    date_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    chat = orm.relationship('Chat')

