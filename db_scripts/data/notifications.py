import sqlalchemy
import datetime
from sqlalchemy import orm
from db_scripts.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Notification(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'notifications'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    buttons = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sender_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    date_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    user = orm.relationship('User')

