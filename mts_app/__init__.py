# this stuff runs wenever we load anything from this module

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_migrate
from flask_migrate import Migrate
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os
import json
from sqlalchemy import sql
import sqlalchemy

# define current version
VERSION=('1.0.0','2018/07/01','completed initial unit tests and have functional rest service deployment')

# get secrets
with open(os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/' + 'mts_app' + '/.secrets.json')) as f:
    secrets=json.loads(f.read())
    
from mts_app.config import config

#db = SQLAlchemy()
migrate = Migrate()
#from mts_app import models

def create_app(config_name = os.environ.get('FLASK_ENV') or 'development'):
    #from mts_app.models import User, Node
    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    from mts_app.models import db
    db.init_app(app)
    migrate.init_app(app, db)
    from mts_app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix = '/admin')
    
    from mts_app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    if not app.testing:
        if app.config['EMAIL_HOST']:
            auth = None
            if app.config['EMAIL_HOST_USER'] or app.config['EMAIL_HOST_PASSWORD']:
                auth = (app.config['EMAIL_HOST_USER'],
                        app.config['EMAIL_HOST_PASSWORD'])
            secure = None
            if app.config['EMAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['EMAIL_HOST'], app.config['EMAIL_PORT']),
                fromaddr='no-reply@' + app.config['EMAIL_HOST'],
                toaddrs=app.config['ADMINS'], subject='My Things Server Failure',
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
            file_handler = RotatingFileHandler('logs/mythingsserver.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('My Things Server startup')

    return app