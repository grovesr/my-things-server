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

    from mts_app.helpers import checkDatabasePrerequisites
    with app.app_context():
        db.create_all()
    if not app.config['TESTING']:
        with app.app_context():
            checkDatabasePrerequisites()


    return app