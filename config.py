from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def make_celery(app):
    celery = Celery(
        'test_task',
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


class FlaskSettings:

    def __init__(self):
        self.flask_app = Flask(__name__)

        self.flask_app.config.update(
            CELERY_BROKER_URL='pyamqp://guest@localhost//',
            CELERY_RESULT_BACKEND='rpc://',
            SQLALCHEMY_DATABASE_URI='sqlite:///hh_vacancies.db',
            SQLALCHEMY_TRACK_MODIFICATIONS=False
        )


def make_flask_app():
    flask_config = FlaskSettings()
    return flask_config.flask_app


def make_db(flask_app):
    return SQLAlchemy(flask_app)


flask_app = make_flask_app()

db = make_db(flask_app)

celery_app = make_celery(flask_app)
celery_app.add_defaults(lambda: flask_app)