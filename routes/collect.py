from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.collect import Collect


main = Blueprint('collect', __name__)


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    form_topic_id = int(form.get('topic_id', ''))
    u = current_user()
    # print('DEBUG', form)
    if u is None:
        return redirect(url_for('topic.index'))
    else:
        d = {
            'user_id': u.id,
            'topic_id': form_topic_id
        }
        c = Collect.find_by(**d)
        # 已经m没有收藏过
        if c is None:
            m = Collect.new(form)
            m.set_user_id(u.id)

        # print('u.id', u)
        return redirect(url_for('topic.detail', id=form_topic_id))


@main.route("/delete", methods=["POST"])
def delete():
    form = request.form
    form_topic_id = int(form.get('topic_id', ''))
    u = current_user()
    # print('DEBUG', form)
    if u is None:
        return redirect(url_for('topic.index'))
    else:
        d = {
            'user_id': u.id,
            'topic_id': form_topic_id
        }
        c = Collect.find_by(**d)
        # 已经m没有收藏过
        if c is not None:
            c.delete()

        # print('u.id', u)
        return redirect(url_for('topic.detail', id=form_topic_id))
