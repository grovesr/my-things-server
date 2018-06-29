'''
Created on Jun 20, 2018

@author: grovesr
'''

from mts_app import app, db, auth
from mts_app.models import User
from mts_app.route_helpers import *
from mts_app.config import Config
from flask import jsonify
from flask import request


  
@app.route(Config.API_PREFIX + '/admin/add/user', methods=['POST'])
@auth.login_required
def addUser():
    checkAdmin()
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        raise BadRequest('No username and/or pasword specified in add/user request')
    try:
        user = User(username=request.json['username'])
        user.set_password(request.json['password'])
    except AssertionError as e:
        raise BadRequest('username error: ' + str(e))
    if User.query.filter_by(username=request.json['username']).count():
        raise BadRequest('User already exists')
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
    return jsonify(user.buildPublicJson()), 201

@app.route(Config.API_PREFIX + '/admin/check/user/<string:username>', methods=['GET'])
@auth.login_required
def checkUser(username):
    checkAdmin()
    if not User.query.filter_by(username=username).count():
        raise NotFound('User not found')
    returnJson = {username + ' exists': User.query.filter_by(username=username).count() == 1}
    return jsonify(returnJson)

@app.route(Config.API_PREFIX + '/admin/get/user/<string:username>', methods=['GET'])
@auth.login_required
def getUser(username):
    checkAdmin()
    userQuery = User.query.filter_by(username=username)
    if not userQuery.count():
        raise NotFound('User not found')
    user = userQuery.first()
    return jsonify(user.buildPublicJson())

@app.route(Config.API_PREFIX + '/admin/get/users', methods=['GET'])
@auth.login_required
def getUsers():
    checkAdmin()
    users = User.query.all()
    if len(users) == 0:
        raise NotFound('No users found')
    usersJson = {'users':[]}
    usersJson['userCount'] = len(users)
    for user in users:
        usersJson['users'].append(user.buildPublicJson())
    return jsonify(usersJson)

@app.route(Config.API_PREFIX + '/admin/delete/user/<string:username>', methods=['DELETE'])
@auth.login_required
def deleteUser(username):
    checkAdmin()
    userQuery = User.query.filter_by(username=username)
    if not userQuery.count():
        raise NotFound('User not found')
    db.session.delete(userQuery.first())
    db.session.commit()
    return jsonify({'result': True})

@app.route(Config.API_PREFIX + '/admin/update/user/<string:username>', methods=['PUT'])
@auth.login_required
def updateUser(username):
    checkAdmin()
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