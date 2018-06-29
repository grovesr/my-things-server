'''
Created on Jun 28, 2018

@author: grovesr
'''

from mts_app import app, auth
from mts_app.models import User
from flask import make_response
from flask import jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Forbidden
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

auth = HTTPBasicAuth()

@app.errorhandler(404)
def notFound(error):
    return make_response(jsonify({'error': error.description}), 404)

@app.errorhandler(400)
def invalidFormat(error):
    return make_response(jsonify({'error': error.description}), 400)

@app.errorhandler(403)
def forbidden(error):
    return make_response(jsonify({'error': error.description}), 403)

@app.errorhandler(500)
def serverError(error):
    return make_response(jsonify({'error': error.description}), 500)

@auth.verify_password
def verify_password(username, password):
    userQuery=User.query.filter_by(username=username)
    if userQuery.count() > 0:
        return check_password_hash(userQuery.first().password_hash, password)
    return False

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

def checkUser():
    queryUser = User.query.filter_by(username=auth.username())
    if queryUser.count() == 0:
        raise Forbidden('Permission denied. Request API access.')

def checkAdmin():
    checkUser()
    queryUser = User.query.filter_by(username=auth.username())
    if queryUser.count() > 0 and not queryUser.first().isAdmin:
        raise Forbidden('User is not admin')

def checkEditor():
    checkUser()
    queryUser = User.query.filter_by(username=auth.username())
    if queryUser.count() > 0 and not queryUser.first().canEdit:
        raise Forbidden('User doesn''t have edit permission')
  