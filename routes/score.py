from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.score import Score


main = Blueprint('score', __name__)


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    form_topic_id = int(form.get('topic_id', 0))
    form_grade = int(form.get('grade', 1))
    print('score form', form)
    u = current_user()
    # print('DEBUG', form)
    if u is None:
        return redirect(url_for('topic.index'))
    else:
        d = {
            'user_id': u.id,
            'topic_id': form_topic_id,
        }
        s = Score.find_by(**d)
        if s is None:
            s = Score.new(form)
            s.set_user_id(u.id)
        else:
            print('update grade')
            sd = {
                'grade': form_grade,
            }
            s.update(sd)
        # print('u.id', u)
        return redirect(url_for('topic.detail', id=form_topic_id))

