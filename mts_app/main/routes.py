'''
Created on Jun 20, 2018

@author: grovesr
'''

#from mts_app import app, db, auth
import json
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
from werkzeug.exceptions import InternalServerError
from flask import jsonify
from flask import request
from flask import make_response
from werkzeug.exceptions import BadRequest, HTTPException
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import literal
from sqlalchemy.sql.expression import select
from sqlalchemy.sql import func
from sqlalchemy import and_
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

@main_bp.route('/main/nodes/info/3', methods=['GET'])
@auth.login_required
def getMainNodesWithInfo3():
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
        owner = ownerQuery.first()
    rootNode = Node.query.filter_by(parent=None).first()
    
    # get all nodes with the given filter
    all1 = db.session.query(Node)\
                  .filter_by(**filterBy)\
                  .subquery()
    filterBy['parentId'] = rootNode.id
    # get all sub nodes of main nodes under root node               
    sub1 = db.session.query(Node)\
                  .filter(Node.parentId.in_(db.session.query(Node.id)\
                  .filter_by(**filterBy)))\
                  .subquery()
    # accumulate all leaf item info and add to each sub item
    sub2 = db.session.query(sub1)\
                  .join(all1, sub1.c.id==all1.c.parentId)\
                  .distinct()\
                  .add_columns(select([func.avg(Node.rating)]).where(Node.parentId==sub1.c.id).label('averageRating'),
                               select([func.count()]).where(and_(Node.parentId==sub1.c.id, Node.need==True)).label('needChildren'),
                               select([func.count()]).where(and_(Node.parentId==sub1.c.id, Node.haveTried==True)).label('haveTriedChildren'),
                               select([func.count()]).where(Node.parentId==sub1.c.id).label('numberChildren'))\
                   .subquery()
    # get all main nodes
    main1 = db.session.query(Node)\
                   .filter_by(**filterBy)\
                   .subquery()

    asub2  = aliased(sub2)
    # inner join sub nodes to main nodes on sub.parentId=main.id
    rows = db.session.query(main1)\
                  .join(sub2, main1.c.id==sub2.c.parentId)\
                  .add_columns(select([func.round(func.avg(asub2.c.averageRating))]).where(asub2.c.parentId==main1.c.id).label('averageLeafRating'),
                               select([func.sum(asub2.c.needChildren)]).where(asub2.c.parentId==main1.c.id).label('needLeaves'),
                               select([func.sum(asub2.c.haveTriedChildren)]).where(asub2.c.parentId==main1.c.id).label('haveTriedLeaves'),
                               select([func.sum(asub2.c.numberChildren)]).where(asub2.c.parentId==main1.c.id).label('numberLeaves'),
                               select([func.count()]).where(asub2.c.parentId==main1.c.id).label('numberSubs'))\
                   .distinct()\
                   .all()
    nodes = []
    for row in rows:
        rowDict = row._asdict()
        node = Node.query.filter(Node.id==rowDict['id']).first()
        if node.nodeInfo is None:
            node.nodeInfo = {}
        nodeInfo = json.loads(node.nodeInfo)
        try:
            nodeInfo['averageLeafRating'] = int(rowDict.pop('averageLeafRating'))
        except TypeError:
            nodeInfo['averageLeafRating'] = None
        nodeInfo['needLeaves'] = int(rowDict.pop('needLeaves'))
        nodeInfo['haveTriedLeaves'] = int(rowDict.pop('haveTriedLeaves'))
        nodeInfo['numberLeaves'] = int(rowDict.pop('numberLeaves'))
        nodeInfo['numberSubs'] = int(rowDict.pop('numberSubs'))
        node.nodeInfo = nodeInfo
        nodes.append(node)
    nodes.append(rootNode)
    db.session.commit()
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
            if request.json['dateTried'] is not None and request.json['dateTried'] is not '' :
                try:
                    node.dateTried = parse(request.json['dateTried'])
                except ValueError:
                    raise BadRequest('Provided dateTried is not a valid date format')
        if 'review' in request.json:
            node.review = request.json['review']
        if 'dateReviewed' in request.json:
            if request.json['dateReviewed'] is not None and request.json['dateReviewed'] is not '':
                try:
                    node.dateReviewed = parse(request.json['dateReviewed'])
                except ValueError:
                    raise BadRequest('Provided dateReviewed is not a valid date format')
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
