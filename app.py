from flask import Flask
import config


app = Flask(__name__)
app.secret_key = config.secret_key


from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.board import main as board_routes
from routes.mail import main as mail_routes
from routes.collect import main as collect_routes
from routes.score import main as score_routes
app.register_blueprint(index_routes)
app.register_blueprint(topic_routes, url_prefix='/topic')
app.register_blueprint(reply_routes, url_prefix='/reply')
app.register_blueprint(board_routes, url_prefix='/board')
app.register_blueprint(mail_routes, url_prefix='/mail')
app.register_blueprint(collect_routes, url_prefix='/collect')
app.register_blueprint(score_routes, url_prefix='/score')


if __name__ == '__main__':

    config = dict(
        debug=True,
        host='127.0.0.1',
        port=2000,
    )
    app.run(**config)
