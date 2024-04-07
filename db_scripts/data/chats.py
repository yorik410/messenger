import sqlalchemy
from sqlalchemy import orm
from db_scripts.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Chat(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("users.id"))
    contact = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    user = orm.relationship('User')
    messages = orm.relationship("Message", back_populates='chat')
