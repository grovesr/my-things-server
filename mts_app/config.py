'''
Created on Jun 21, 2018

@author: grovesr
'''

import os
from mts_app import my_app
from mts_app import secrets

class Config(object):
    
    APP = my_app
    API_PREFIX = '/my_things/api/v1.0'
    ADMIN_USERNAME = 'Admin'
    ADMIN_USER_PASSWORD = secrets['ADMIN_USER_PASSWORD']
    ADMIN_USER_EMAIL = secrets['ADMIN_USER_EMAIL']
    ROOT_NODE_NAME = 'Root'
    DATABASE_USER = secrets['DATABASE_USER']
    DATABASE_PASSWORD = secrets['DATABASE_PASSWORD']
    DATABASE = secrets['DATABASE']
    BASE_DIR = os.environ.get('BASE_DIR') or os.path.dirname(os.path.dirname(__file__))
    DEBUG = os.environ.get('DEBUG') or True
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') or False
    TEST_DB = os.environ.get('TEST_DB') or 'localhost/my_things_test'
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