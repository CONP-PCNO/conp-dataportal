# -*- coding: utf-8 -*-
import os
import sys
import inspect
from flask import Flask
from flask_user import UserManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from config import DevelopmentConfig, ProductionConfig


db = SQLAlchemy()
config = DevelopmentConfig()
migrate = Migrate(compare_type=True)
csrf_protect = CSRFProtect()
mail = Mail()
bootstrap = Bootstrap()


def create_app(config_settings=DevelopmentConfig):

    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config_settings)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf_protect.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    from app.main import main_bp  # noqa: E402
    app.register_blueprint(main_bp)

    from app.analytics import analytics_bp  # noqa: E402
    app.register_blueprint(analytics_bp)

    from app.search import search_bp  # noqa: E402
    app.register_blueprint(search_bp)

    from app.forums import forums_bp  # noqa: E402
    app.register_blueprint(forums_bp)

    from app.profile import profile_bp  # noqa: E402
    app.register_blueprint(profile_bp)

    from app.pipelines import pipelines_bp  # noqa: E402
    app.register_blueprint(pipelines_bp)

    from app.utils import utils_bp  # noqa: E402
    app.register_blueprint(utils_bp)

    from app.styleguide import styleguide_bp
    app.register_blueprint(styleguide_bp)

    from app.webhooks import webhooks_bp
    csrf_protect.exempt(webhooks_bp)
    app.register_blueprint(webhooks_bp)

    @app.context_processor
    def context_processor():
        return dict()

    return app

# Function to initialize the email and logs


def init_email_and_logs_error_handler(app):
    if app.debug and not app.testing:
        return

    import logging
    from logging.handlers import SMTPHandler

    if app.config['MAIL_SERVER']:
        auth = None

    if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
        auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = 90

        mail_handler = SMTPHandler(mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                                   fromaddr='no-reply@' +
                                   app.config['MAIL_SERVER'],
                                   toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                                   credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/portal.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                                      '%(asctime)s %(levelname)s: %(message)s '
                                      '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
