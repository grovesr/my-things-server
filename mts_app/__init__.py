# this stuff runs wenever we load anything from this module

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os
import json

my_app = __name__

# get secrets
with open(os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/' + my_app + '/.secrets.json')) as f:
    secrets=json.loads(f.read())
        
app = Flask(__name__)

from mts_app.config import Config
app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql://' + 
			Config.DATABASE_USER + ':' +
			Config.DATABASE_PASSWORD + '@' + 
			Config.DATABASE)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/my-things-server.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('My Things Server startup')
    
    if Config.EMAIL_HOST:
        auth = None
        if Config.EMAIL_HOST_USER or Config.EMAIL_HOST_PASSWORD:
            auth = (Config.EMAIL_HOST_USER, Config.EMAIL_HOST_PASSWORD)
        secure = None
        if Config.EMAIL_USE_TLS:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(Config.EMAIL_HOST, Config.EMAIL_PORT),
            fromaddr='no-reply@' + Config.EMAIL_HOST,
            toaddrs=Config.ADMINS, subject='My Things Server Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

from mts_app import models
from mts_app.admin import routes as admin_routes
from mts_app import routes
from mts_app.helpers import checkDatabasePrerequisites

if not app.config['TESTING']:
    checkDatabasePrerequisites()
