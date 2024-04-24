import sqlalchemy
from sqlalchemy import orm
from db_scripts.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Avatar(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'avatars'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
