from flask import session

from models.user import User
from models.topic import Topic


def current_user():
    uid = session.get('user_id', '')
    u = User.find_by(id=uid)
    return u


def topic_by_id(_id):
    t = Topic.find(_id)
    return t


def to_str(n):
    return str(n)