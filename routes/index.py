from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    make_response,
    send_from_directory,
)
from werkzeug.utils import secure_filename
from models.user import User
from config import user_file_director
import os
import random

from models.topic import Topic
from utils import log

main = Blueprint('index', __name__)


def current_user():
    # 从 session 中找到 user_id 字段, 找不到就 -1
    # 然后 User.find_by 来用 id 找用户
    # 找不到就返回 None
    uid = session.get('user_id', -1)
    u = User.find_by(id=uid)
    return u


@main.route("/")
def index():
    u = current_user()
    if u is None:
        u = {
            'username': '游客',
            'id': 0,
        }
    return render_template("index.html", user=u)


@main.route("/register", methods=['POST'])
def register():
    form = request.form
    # 用类函数来判断
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    if u is None:
        # 转到 topic.index 页面
        return redirect(url_for('topic.index'))
    else:
        # session 中写入 user_id
        session['user_id'] = u.id
        # 设置 cookie 有效期为 永久
        session.permanent = True
        return redirect(url_for('topic.index'))


@main.route('/profile/<int:id>')
def profile(id):
    current_u = current_user()
    print('current_u', current_u)
    hide = 'hide'
    hide_mail = 'hide'
    # 使用 id 来查看用户
    u = User.find(id)
    if u is None:
        return redirect(url_for('.index'))
    else:
        cs = u.user_collect()
        ts = []
        for c in cs:
            t = Topic.find(c.topic_id)
            ts.append(t)
        stars = u.user_star()
        ss = []
        for s in stars:
            t = Topic.find(s.topic_id)
            ss.append(t)
        # 在查看别人的 profile
        if current_u is not None:
            if current_u.id != u.id:
                hide_mail = ''
            if current_u.id == u.id:
                hide = ''
        return render_template('profile.html', user=u, ts=ts, ss=ss, hide=hide, hide_mail=hide_mail)


def allow_file(filename):
    suffix = filename.split('.')[-1]
    from config import accept_user_file_type
    return suffix in accept_user_file_type


@main.route('/addimg', methods=["POST"])
def add_img():
    u = current_user()

    if u is None:
        return redirect(url_for(".profile"))

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if allow_file(file.filename):
        filename = secure_filename(file.filename)
        new_filename = str(random.randint(1, 100000)) + '_' + filename
        new_path = user_file_director + '/head'
        file.save(os.path.join(new_path, new_filename))
        u.user_image = filename
        # u.save()
        dict_img = {
            'user_image': new_filename
        }
        u.update(dict_img)
        print('u_id', u.id)
    return redirect(url_for(".profile", id=u.id))


@main.route("/uploads/<filename>")
def uploads(filename):
    print('filename', filename)
    return send_from_directory(user_file_director, filename)


@main.route("/uploads/head/<filename>")
def pic(filename):
    path = user_file_director + '/head'
    print('path img', path)
    return send_from_directory(path, filename)
