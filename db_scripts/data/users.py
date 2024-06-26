import datetime
import sqlalchemy
from sqlalchemy import orm
from db_scripts.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)
    contacts = orm.relationship("Chat", back_populates='user')
    avatar = orm.relationship("Avatar", back_populates='user')

    # def __repr__(self):
    #     return f"<Colonist> {self.id} {self.surname} {self.name}"

    def set_password(self, password):
        self.hashed_password = password

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
