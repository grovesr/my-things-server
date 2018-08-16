'''
Created on Jun 20, 2018

@author: grovesr
'''

#from mts_app import app, db, auth
from mts_app.models import db
from mts_app.admin import bp as admin_bp
from flask import current_app
from mts_app.models import User
from flask import make_response
from flask import jsonify
from flask import request
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Forbidden
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.security import check_password_hash

auth = HTTPBasicAuth()

@admin_bp.errorhandler(404)
def notFound(error):
    return make_response(jsonify({'error': error.description}), 404)

@admin_bp.errorhandler(405)
def methodNotAllowed(error):
    return make_response(jsonify({'error': error.description}), 405)

@admin_bp.errorhandler(400)
def invalidFormat(error):
    return make_response(jsonify({'error': error.description}), 400)

@admin_bp.errorhandler(403)
def forbidden(error):
    return make_response(jsonify({'error': error.description}), 403)

@admin_bp.errorhandler(500)
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

def validateUser():
    queryUser = User.query.filter_by(username=auth.username())
    if queryUser.count() == 0:
        raise Forbidden('Permission denied. Request API access.')

def validateAdmin():
    validateUser()
    queryUser = User.query.filter_by(username=auth.username())
    if queryUser.count() > 0 and not queryUser.first().isAdmin:
        raise Forbidden('User is not admin')

def validateEditor():
    validateUser()
    queryUser = User.query.filter_by(username=auth.username())
    if queryUser.count() > 0 and not queryUser.first().canEdit:
        raise Forbidden('User doesn''t have edit permission')
  
@admin_bp.route('/add/user', methods=['POST'])
@auth.login_required
def addUser():
    validateAdmin()
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        raise BadRequest('No username and/or pasword specified in add/user request')
    try:
        user = User(username=request.json['username'])
    except AssertionError as e:
        raise BadRequest('username error: ' + str(e))
    user.set_password(request.json['password'])
    if User.query.filter_by(username=request.json['username']).count():
        raise BadRequest('User already exists')
    if 'email' in request.json:
        try:
            user.email = request.json['email']
        except AssertionError as e:
            raise BadRequest('bad email format' + str(e))
    if 'isAdmin' in request.json:
        try:
            user.isAdmin = request.json['isAdmin']
        except AssertionError as e:
            raise BadRequest('isAdmin error: ' + str(e))
    if 'canEdit' in request.json:
        try:
            user.canEdit = request.json['canEdit']
        except AssertionError as e:
            raise BadRequest('canEdit error: ' + str(e))
    db.session.add(user)
    db.session.commit()
    return jsonify(user.buildPublicJson()), 201

@admin_bp.route('/check/user/<string:username>', methods=['GET'])
@auth.login_required
def checkUser(username):
    userQuery = User.query.filter_by(username=username)
    if userQuery.count() == 0:
        raise NotFound('User not found')
    user = userQuery.first()
    returnJson = {'id': user.id}
    return jsonify(returnJson)

@admin_bp.route('/user/<string:username>', methods=['GET'])
@auth.login_required
def getUser(username):
    validateUser()
    userQuery = User.query.filter_by(username=username)
    if not userQuery.count():
        raise NotFound('User not found')
    user = userQuery.first()
    return jsonify(user.buildPublicJson())

@admin_bp.route('/users', methods=['GET'])
@auth.login_required
def getUsers():
    validateAdmin()
    users = User.query.all()
    if len(users) == 0:
        raise NotFound('No users found')
    usersJson = {'users':[]}
    usersJson['userCount'] = len(users)
    for user in users:
        usersJson['users'].append(user.buildPublicJson())
    return jsonify(usersJson)

@admin_bp.route('/user/<string:username>', methods=['DELETE'])
@auth.login_required
def deleteUser(username):
    validateAdmin()
    userQuery = User.query.filter_by(username=username)
    if not userQuery.count():
        raise NotFound('User not found')
    db.session.delete(userQuery.first())
    db.session.commit()
    return jsonify({'result': userQuery.count() == 0})

@admin_bp.route('/user/<string:username>', methods=['PUT'])
@auth.login_required
def updateUser(username):
    validateAdmin()
    userQuery = User.query.filter_by(username=username)
    if not userQuery.count():
        raise NotFound('User not found')
    if not request.json:
        raise BadRequest('Not json data')
    user = userQuery.first()
    if 'username' in request.json:
        try:
            user.username = request.json['username']
        except AssertionError as e:
            raise BadRequest('username error: ' + str(e))
    if 'email' in request.json:
        try:
            user.email = request.json['email']
        except AssertionError as e:
            raise BadRequest(str(e))
    if 'isAdmin' in request.json:
        try:
            user.isAdmin = request.json['isAdmin']
        except AssertionError as e:
            raise BadRequest('isAdmin error: ' + str(e))
    if 'canEdit' in request.json:
        try:
            user.canEdit = request.json['canEdit']
        except AssertionError as e:
            raise BadRequest('canEdit error: ' + str(e))
    db.session.add(user)
    db.session.commit()
    return jsonify(user.buildPublicJson())