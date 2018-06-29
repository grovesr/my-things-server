'''
Created on Jun 20, 2018

@author: grovesr
'''

from mts_app import app, db, auth
from mts_app.models import Node
from mts_app.route_helpers import *
from mts_app.config import Config
from mts_app.helpers import getAdminAndRootNode
from flask import jsonify
from flask import request
from werkzeug.exceptions import BadRequest, HTTPException
from sqlalchemy.exc import IntegrityError
#from _mysql_exceptions import IntegrityError
  
@app.route(Config.API_PREFIX + '/get/main/nodes', methods=['GET'])
@auth.login_required
def getMainNodes():
    checkUser()
    admin, rootNode = getAdminAndRootNode()
    nodes = Node.query.filter_by(parent=rootNode.id).all()
    if len(nodes) == 0:
        raise NotFound('No main nodes found')
    nodesJson = {'nodes':[]}
    nodesJson['nodeCount'] = len(nodes)
    for node in nodes:
        nodesJson['nodes'].append(node.buildPublicJson())
    return jsonify(nodesJson)

@app.route(Config.API_PREFIX + '/get/node/<int:nodeId>', methods=['GET'])
@auth.login_required
def getNode(nodeId):
    checkUser()
    nodeQuery = Node.query.filter_by(id=nodeId)
    if nodeQuery.count() == 0:
        raise NotFound('Node not found')
    node = nodeQuery.first()
    return jsonify(node.buildPublicJson())

@app.route(Config.API_PREFIX + '/add/node', methods=['POST'])
@auth.login_required
def addNode():
    checkEditor()
    admin, rootNode = getAdminAndRootNode()
    if not request.json or not 'name' in request.json or not 'owner' in request.json or not 'parent' in request.json:
        raise BadRequest('No name and/or owner and/or parent specified in add/node request')
    ownerQuery = User.query.filter_by(id=request.json['owner'])
    if ownerQuery.count() == 0:
        raise NotFound('Owner not found. Can''t create node')
    owner = ownerQuery.first() 
    parentQuery = Node.query.filter_by(id=request.json['parent'])
    if parentQuery.count() > 0:
        parent = parentQuery.first()
    try:
        node = Node(name=request.json['name'], owner=owner, parent=parent)
        db.session.add(node)
        db.session.flush()
    except IntegrityError as e:
        db.session.rollback()
        raise BadRequest('This node already exists: ' + str(e))
    else:
        db.session.commit()
    return jsonify(node.buildPublicJson()), 201
