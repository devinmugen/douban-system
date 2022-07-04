from flask_paginate import Pagination, get_page_parameter
from config import PER_PAGE

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    abort,
)

from routes import *

from models.topic import Topic
from models.board import Board
from models.score import Score


main = Blueprint('topic', __name__)


import uuid
csrf_tokens = dict()


@main.route("/")
def index():
    # ---
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    # ---
    # board_id = 2
    # board_id = [1, 2,]
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        ms = Topic.all()
    else:
        ms = Topic.find_all(board_id=board_id)
    token = str(uuid.uuid4())
    u = current_user()
    if u is None:
        user = {
            'username': '游客',
            'id': 0,
        }
    else:
        user = u
        csrf_tokens['token'] = u.id
    bs = Board.all()
    # print('ms', type(ms))
    #
    split_ms = ms[start:end]

    total = len(ms)
    pagination = Pagination(css_framework='bootstrap3', page=page, total=total, per_page=PER_PAGE, inner_window=2)

    #
    return render_template("topic/home.html", ms=split_ms, token=token, bs=bs, pagination=pagination, user=user)


@main.route('/<int:id>')
def detail(id):
    m = Topic.get(id)
    u = current_user()
    s1 = ''
    s2 = ''
    s3 = ''
    s4 = ''
    s5 = ''
    if u is None:
        collect_or_not = '登录后收藏'
        collect_hide = 'hide'
        collect_add = ''
    else:
        # 处理收藏
        cs = u.user_collect()
        collect_or_not = '未收藏'
        collect_hide = 'hide'
        collect_add = ''
        for c in cs:
            # print('board_id', type(c), c.topic_id)
            if c.topic_id == id:
                collect_or_not = '已收藏'
                collect_add = 'hide'
                collect_hide = ''
        # 处理评分
        sd = {
            'user_id': u.id,
            'topic_id': id,
        }
        s = Score.find_by(**sd)
        print('s-----', s)
        if s is not None:
            i = s.grade
            print('i-----', i)
            if i >= 1:
                s1 = 'starstar'
            if i >= 2:
                s2 = 'starstar'
            if i >= 3:
                s3 = 'starstar'
            if i >= 4:
                s4 = 'starstar'
            if i >= 5:
                s5 = 'starstar'
        # print('cs', cs)
    # collect_or_not =
    # print('m', m)

    # 传递 topic 的所有 reply 到 页面中
    return render_template("topic/detail.html", topic=m, collect_or_not=collect_or_not, s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, collect_hide=collect_hide, collect_add=collect_add)


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    u = current_user()
    m = Topic.new(form, user_id=u.id)
    return redirect(url_for('.detail', id=m.id))


@main.route("/delete")
def delete():
    id = int(request.args.get('id'))
    token = request.args.get('token')
    u = current_user()
    # 判断 token 是否是我们给的
    if token in csrf_tokens and csrf_tokens[token] == u.id:
        csrf_tokens.pop(token)
        if u is not None:
            print('删除 topic 用户是', u, id)
            Topic.delete(id)
            return redirect(url_for('.index'))
        else:
            abort(404)
    else:
        abort(403)


@main.route("/new")
def new():
    bs = Board.all()
    return render_template("topic/new.html", bs=bs)
