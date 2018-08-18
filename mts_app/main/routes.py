'''
Created on Jun 20, 2018

@author: grovesr
'''

#from mts_app import app, db, auth
from mts_app.models import db
from mts_app.main import bp as main_bp
from mts_app.admin.routes import validateAdmin, validateEditor, validateUser
from flask import current_app
from mts_app.models import Node, User
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Forbidden
from werkzeug.exceptions import MethodNotAllowed
from flask import jsonify
from flask import request
from flask import make_response
from werkzeug.exceptions import BadRequest, HTTPException
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError
from dateutil.parser import parse
from sqlalchemy.orm import aliased


auth = HTTPBasicAuth()  

@main_bp.errorhandler(404)
def notFound(error):
    return make_response(jsonify({'error': error.description}), 404)

@main_bp.errorhandler(405)
def notFound(error):
    return make_response(jsonify({'error': error.description}), 405)

@main_bp.errorhandler(400)
def invalidFormat(error):
    return make_response(jsonify({'error': error.description}), 400)

@main_bp.errorhandler(403)
def forbidden(error):
    return make_response(jsonify({'error': error.description}), 403)

@main_bp.errorhandler(500)
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

@main_bp.route('/main/nodes', methods=['GET'])
@auth.login_required
def getMainNodes():
    validateUser()
    filterBy = {}
    for key,value in iter(request.args.to_dict().items()):
        if key in Node.validSearchFields() and key != 'orderField' and key != 'orderDir':
            filterBy[key] = value
    orderField = request.args.get('orderField', 'name')
    orderDir = request.args.get('orderDir', 'desc')
    if orderField and orderField not in Node.validOrderByFields():
        raise BadRequest('orderField is not valid. Valid fields = ' + str(Node.validOrderByFields()))
    if orderDir.lower() not in ['asc', 'desc']:
        raise BadRequest('orderBy can only be "asc" or "desc"')
    if filterBy.get('ownerId', None):
        ownerQuery = User.query.filter_by(id= filterBy['ownerId'])
        if ownerQuery.count() == 0:
            raise NotFound('Invalid ownername specified in main/nodes request, so no nodes could be found')
    rootNode = Node.query.filter_by(parent=None).first()
    filterBy['parentId'] = rootNode.id
    nodes = Node.query.filter_by(**filterBy).order_by(orderField).all()
    nodes.append(rootNode)
    nodesJson = {'nodes':[]}
    nodesJson['nodeCount'] = len(nodes)
    for node in nodes:
        node.childCount = len(node.children);
        nodesJson['nodes'].append(node.buildPublicJson())
    return jsonify(nodesJson)

@main_bp.route('/nodes', methods=['GET'])
@auth.login_required
def getNodes():
    validateUser()
    filterBy = {}
    for key,value in iter(request.args.to_dict().items()):
        if key in Node.validSearchFields() and key != 'orderField' and key != 'orderDir':
            filterBy[key] = value
    orderField = request.args.get('orderField', 'name')
    orderDir = request.args.get('orderDir', 'desc')
    if orderField and orderField not in Node.validOrderByFields():
        raise BadRequest('orderField is not valid. Valid fields = ' + str(Node.validOrderByFields()))
    if orderDir.lower() not in ['asc', 'desc']:
        raise BadRequest('orderBy can only be "asc" or "desc"')
    if filterBy.get('ownerId', None):
        ownerQuery = User.query.filter_by(id= filterBy['ownerId'])
        if ownerQuery.count() == 0:
            raise NotFound('Invalid ownername specified in nodes request, so no nodes could be found')
    nodes = Node.query.filter(Node.parent != None).filter_by(**filterBy).order_by(orderField).all()
    rootNode = Node.query.filter_by(parent=None).first()
    nodes.append(rootNode)
    nodesJson = {'nodes':[]}
    nodesJson['nodeCount'] = len(nodes)
    for node in nodes:
        node.childCount = len(node.children);
        nodesJson['nodes'].append(node.buildPublicJson())
    return jsonify(nodesJson)

@main_bp.route('/node/<string:nodeId>', methods=['GET'])
@auth.login_required
def getNodeFromId(nodeId):
    validateUser()
    nodeQuery = Node.query.filter_by(id=nodeId)
    if nodeQuery.count() == 0:
        raise NotFound('Node not found')
    node = nodeQuery.first()
    node.childCount = len(node.children);
    return jsonify(node.buildPublicJson())

@main_bp.route('/node/<string:nodeId>', methods=['DELETE'])
@auth.login_required
def deleteNode(nodeId):
    validateEditor()
    nodeQuery = Node.query.filter_by(id=nodeId)
    if nodeQuery.count() == 0:
        raise NotFound('Node not found')
    node = nodeQuery.first()
    if node.name == 'Root' and node.parent == None:
        raise Forbidden('Deletion of the Root node is not permitted')
    db.session.delete(node)
    db.session.commit()
    return jsonify({'result': nodeQuery.count() == 0})

@main_bp.route('/add/node', methods=['POST'])
@auth.login_required
def addNode():
    validateEditor()
    if not request.json or not 'name' in request.json:
        raise BadRequest('No name specified in add/node request')
    if not 'owner' in request.json:
        raise BadRequest('No owner specified in add/node request')
    if not 'type' in request.json:
        raise BadRequest('No type specified in add/node request')
    ownerQuery = User.query.filter_by(username=request.json['owner'])
    if ownerQuery.count() == 0:
        raise NotFound('Owner not found. Can''t create node')
    owner = ownerQuery.first()
    if 'parentId' in request.json:
        parentQuery = Node.query.filter_by(id=request.json['parentId'])
        if parentQuery.count() > 0:
            parent = parentQuery.first()
        else:
            raise NotFound('Parent not found. Can''t create node')
    else:
        if request.json['name'] == 'Root':
            raise Forbidden('There can be only one Root node')
        parent = Node.query.filter_by(name='Root', parent=None).first()
    try:
        node = Node(name=request.json['name'], owner=owner, parent=parent)
        if 'name' in request.json:
            node.name = request.json['name']
        if 'type' in request.json:
            node.type = request.json['type']
        if 'description' in request.json:
            node.description = request.json['description']
        if 'nodeInfo' in request.json:
            node.nodeInfo = request.json['nodeInfo']
        if 'haveTried' in request.json:
            node.haveTried = request.json['haveTried']
        if 'dateTried' in request.json:
            node.dateTried = parse(request.json['dateTried']).date()
        if 'review' in request.json:
            node.review = request.json['review']
        if 'dateReviewed' in request.json:
            node.dateReviewed = parse(request.json['dateReviewed']).date()
        if 'rating' in request.json:
            node.rating = request.json['rating']
        if 'sortIndex' in request.json:
            node.sortIndex = request.json['sortIndex']
        if 'ownerId' in request.json:
            raise BadRequest('You can''t specify a node''s owner by setting the ownerId attribute. set ''owner=username'' instead')
        db.session.add(node)
        db.session.flush()
    except IntegrityError as e:
        db.session.rollback()
        raise BadRequest('This node already exists. Try a different name.')
    else:
        db.session.commit()
    node.childCount = 0
    return jsonify(node.buildPublicJson()), 201

@main_bp.route('/node/<string:nodeId>', methods=['PUT'])
@auth.login_required
def updateNode(nodeId):
    validateEditor()
    if not request.json :
        raise BadRequest('No information to update in update/node request')
    node = Node.query.filter_by(id=nodeId).first()
    try:
        if 'name' in request.json:
            node.name = request.json['name']
        if 'type' in request.json:
            node.type = request.json['type']
        if 'description' in request.json:
            node.description = request.json['description']
        if 'nodeInfo' in request.json:
            node.nodeInfo = request.json['nodeInfo']
        if 'haveTried' in request.json:
            node.haveTried = request.json['haveTried']
        if 'dateTried' in request.json:
            if request.json['dateTried'] is not None and request.json['dateTried'] is not '' :
                try:
                    node.dateTried = parse(request.json['dateTried'])
                except ValueError:
                    raise BadRequest('Provided dateTried is not a valid date format')
            else:
               node.dateTried = request.json['dateTried']    
        if 'review' in request.json:
            node.review = request.json['review']
        if 'dateReviewed' in request.json:
            if request.json['dateReviewed'] is not None and request.json['dateReviewed'] is not '':
                try:
                    node.dateReviewed = parse(request.json['dateReviewed'])
                except ValueError:
                    raise BadRequest('Provided dateReviewed is not a valid date format')
            else:
               node.dateReviewed = request.json['dateReviewed']    
        if 'rating' in request.json:
            node.rating = request.json['rating']
        if 'sortIndex' in request.json:
            node.sortIndex = request.json['sortIndex']
        if 'need' in request.json:
            node.need = request.json['need']
        if 'ownerId' in request.json:
            raise BadRequest('You can''t change a node''s owner with an update/node request' )
        if 'parentId' in request.json:
            raise BadRequest('You can''t change a node''s parent with an update/node request' )
        db.session.add(node)
        db.session.flush()
    except AssertionError as e:
        raise BadRequest('Problem with node attributes: ' + str(e))
    except IntegrityError as e:
        db.session.rollback()
        raise BadRequest('This node already exists: ' + str(e))
    else:
        db.session.commit()
    node.childCount = len(node.children);
    return jsonify(node.buildPublicJson())
