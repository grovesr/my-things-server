'''
Created on Jun 21, 2018

@author: grovesr
'''

import os
from mts_app import secrets

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    
    API_PREFIX = '/my_things/api/v1.0'
    ADMIN_USERNAME = 'Admin'
    ADMIN_USER_PASSWORD = secrets['ADMIN_USER_PASSWORD']
    ADMIN_USER_EMAIL = secrets['ADMIN_USER_EMAIL']
    ROOT_NODE_NAME = 'Root'
    DATABASE_USER = secrets['DATABASE_USER']
    DATABASE_PASSWORD = secrets['DATABASE_PASSWORD']
    DATABASE = secrets['DATABASE']
    DEBUG = os.environ.get('DEBUG') or False
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') or False
    USE_I18N = os.environ.get('USE_I8N') or True
    USE_L10N = os.environ.get('USE_L10N') or True
    USE_TZ = os.environ.get('USE_TZ') or True
    EMAIL_HOST = secrets['MY_THINGS_EMAIL_HOST']
    EMAIL_PORT = int(secrets['MY_THINGS_EMAIL_PORT'])
    EMAIL_HOST_USER = secrets['MY_THINGS_EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = secrets['MY_THINGS_EMAIL_HOST_PASSWORD']
    EMAIL_USE_TLS = eval(secrets['MY_THINGS_EMAIL_USE_TLS'])
    EMAIL_USE_SSL = eval(secrets['MY_THINGS_EMAIL_USE_SSL'])
    SERVER_EMAIL = secrets['MY_THINGS_EMAIL_FROM_USER']
    ADMINS = [SERVER_EMAIL] 
    
    @staticmethod
    def init_app(app):
        pass
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = ('mysql://' + 
            Config.DATABASE_USER + ':' +
            Config.DATABASE_PASSWORD + '@' + 
            Config.DATABASE)


class TestingConfig(Config):
    TESTING = True
    SERVER_NAME='localhost:5000'
    SQLALCHEMY_DATABASE_URI = ('mysql://' + 
            Config.DATABASE_USER + ':' +
            Config.DATABASE_PASSWORD + '@' + 
            (os.environ.get('TEST_DB') or 'localhost/my_things_test'))
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = ('mysql://' + 
            Config.DATABASE_USER + ':' +
            Config.DATABASE_PASSWORD + '@' + 
            Config.DATABASE)
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    SSL_REDIRECT = True if os.environ.get('DYNO') else False

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # handle reverse proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.INFO)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'docker': DockerConfig,
    'unix': UnixConfig,
    'default': DevelopmentConfig
}