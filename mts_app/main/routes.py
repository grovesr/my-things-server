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

def getNodesFromLevel(level=1, limit=-1, excludeRoot=False):
    """
    Filter and return nodes from the given level of hierarchy. Include Root node unless
    excludeRoot is specified.
    """
    exactFilterBy = {}
    likeFilterBy = {}
    for key,value in iter(request.args.to_dict().items()):
        if key in Node.validExactSearchFields():
            exactFilterBy[key] = value
        if key in Node.validLikeSearchFields():
            likeFilterBy[key] = value
    orderField = request.args.get('orderField', 'name')
    orderDir = request.args.get('orderDir', 'desc')
    if orderField and orderField not in Node.validOrderByFields():
        raise BadRequest('orderField is not valid. Valid fields = ' + str(Node.validOrderByFields()))
    if orderDir.lower() not in ['asc', 'desc']:
        raise BadRequest('orderBy can only be "asc" or "desc"')
    if exactFilterBy.get('ownerId', None):
        ownerQuery = User.query.filter_by(id= exactFilterBy['ownerId'])
        if ownerQuery.count() == 0:
            raise NotFound('Invalid ownername specified in main/nodes request, so no nodes could be found')
        
    if level != 1 and level != 3:
        raise BadRequest('Retrieving level specific nodes from other than level 3 or 1 is not supported yet.')
    if level == 1:
        infoDepth = int(request.args.get('infoDepth', -1))
        if infoDepth == -1:
            return getLevel1Nodes(exactFilterBy=exactFilterBy, 
                                  likeFilterBy=likeFilterBy, 
                                  orderField=orderField, 
                                  orderDir=orderDir, 
                                  limit=limit,
                                  excludeRoot=excludeRoot)
        else:
            return getLevel1NodesWithInfo(exactFilterBy=exactFilterBy, 
                                          likeFilterBy=likeFilterBy, 
                                          orderField=orderField, 
                                          orderDir=orderDir, 
                                          limit=limit,
                                          excludeRoot=excludeRoot, 
                                          infoDepth=infoDepth)
    if level == 3:
        return getLevel3Nodes(exactFilterBy=exactFilterBy, 
                              likeFilterBy=likeFilterBy, 
                              orderField=orderField, 
                              orderDir=orderDir, 
                              limit=limit,
                              excludeRoot=excludeRoot)
    
def getLevel3Nodes(exactFilterBy={}, 
                   likeFilterBy={}, 
                   orderField=None, 
                   orderDir=None, 
                   limit=-1, 
                   excludeRoot=False):
    ownerTypeFilterBy={}
    if exactFilterBy.get('ownerId', None):
        ownerTypeFilterBy['ownerId'] = exactFilterBy.get('ownerId')
        ownerQuery = User.query.filter_by(id= exactFilterBy['ownerId'])
        if ownerQuery.count() == 0:
            raise NotFound('Invalid ownername specified in main/nodes request, so no nodes could be found')
    else:
        raise NotFound('Owner ID not specified')
    if exactFilterBy.get('type', None):
        ownerTypeFilterBy['type'] = exactFilterBy.get('type')
    else:
        raise NotFound('Type not specified')
    rootNode = Node.query.filter_by(parent=None).first()
    # get all nodes with the given owner and type
    all1 = db.session.query(Node)\
                  .filter_by(**ownerTypeFilterBy)\
                  .subquery()
    
    ownerTypeFilterBy['parentId'] = rootNode.id
    # get all sub nodes of main nodes under root node with given owner and type              
    sub1 = db.session.query(Node.id)\
                  .filter(Node.parentId.in_(db.session.query(Node.id)\
                  .filter_by(**ownerTypeFilterBy)))\
                  .subquery()
    # get the depth 3 nodes and filter appropriately
    nodes = db.session.query(Node)\
                  .filter(Node.parentId.in_(sub1))\
                  .filter_by(**exactFilterBy)
    for likeKey, likeValue in likeFilterBy.items():
        if likeKey == 'name':
            nodes = nodes.filter(Node.name.ilike('%' + likeValue + '%'))
        if likeKey == 'description':
            nodes = nodes.filter(Node.description.ilike('%' + likeValue + '%'))
        if likeKey == 'review':
            nodes = nodes.filter(Node.review.ilike('%' + likeValue + '%'))
    if limit != -1:
        nodes = nodes.limit(limit).all()
    else:
        nodes = nodes.all()
    if not excludeRoot:
        nodes.append(rootNode)
    nodesJson = {'nodes':[]}
    nodesJson['nodeCount'] = len(nodes)
    for node in nodes:
        node.childCount = len(node.children);
        nodesJson['nodes'].append(node.buildPublicJson())
    return jsonify(nodesJson)

def getLevel1Nodes(exactFilterBy={}, 
                   likeFilterBy={}, 
                   orderField=None, 
                   orderDir=None, 
                   limit=-1,
                   excludeRoot=False):
    
    rootNode = Node.query.filter_by(parent=None).first()
    exactFilterBy['parentId'] = rootNode.id
    nodes = Node.query.filter(Node.parent != None).filter_by(**exactFilterBy)
    for likeKey, likeValue in likeFilterBy.items():
        if likeKey == 'name':
            nodes = nodes.filter(Node.name.ilike('%' + likeValue + '%'))
        if likeKey == 'description':
            nodes = nodes.filter(Node.description.ilike('%' + likeValue + '%'))
        if likeKey == 'review':
            nodes = nodes.filter(Node.review.ilike('%' + likeValue + '%'))
    nodes = nodes.order_by(orderField)
    if limit != -1:
        nodes = nodes.limit(limit).all()
    else:
        nodes = nodes.all()
    if(not excludeRoot):
        nodes.append(rootNode)
    nodesJson = {'nodes':[]}
    nodesJson['nodeCount'] = len(nodes)
    for node in nodes:
        node.childCount = len(node.children);
        nodesJson['nodes'].append(node.buildPublicJson())
    return jsonify(nodesJson)

def getLevel1NodesWithInfo(exactFilterBy={}, 
                           likeFilterBy={}, 
                           orderField=None, 
                           orderDir=None, 
                           limit=-1,
                           excludeRoot=False, 
                           infoDepth=None):
    if infoDepth != 3:
        raise BadRequest('Requesting level 1 nodes with information to a depth other than 3 not supported yet')
    if exactFilterBy.get('ownerId', None):
        ownerQuery = User.query.filter_by(id= exactFilterBy['ownerId'])
        if ownerQuery.count() == 0:
            raise NotFound('Invalid ownername specified in main/nodes/info/depth/3 request, so no nodes could be found')
        owner = ownerQuery.first()
    rootNode = Node.query.filter_by(parent=None).first()
    
    # get all nodes with the given filter
    all1 = db.session.query(Node)\
                  .filter_by(**exactFilterBy)
    for likeKey, likeValue in likeFilterBy.items():
        if likeKey == 'name':
            all1 = all1.filter(Node.name.ilike('%' + likeValue + '%'))
        if likeKey == 'description':
            all1 = all1.filter(Node.description.ilike('%' + likeValue + '%'))
        if likeKey == 'review':
            all1 = all1.filter(Node.review.ilike('%' + likeValue + '%'))
    all1 = all1.subquery()
    exactFilterBy['parentId'] = rootNode.id
    # get all sub nodes of main nodes under root node               
    sub1 = db.session.query(Node)\
                  .filter(Node.parentId.in_(db.session.query(Node.id)\
                  .filter_by(**exactFilterBy)))
    for likeKey, likeValue in likeFilterBy.items():
        if likeKey == 'name':
            sub1 = all1.filter(Node.name.ilike('%' + likeValue + '%'))
        if likeKey == 'description':
            sub1 = all1.filter(Node.description.ilike('%' + likeValue + '%'))
        if likeKey == 'review':
            sub1 = all1.filter(Node.review.ilike('%' + likeValue + '%'))
    sub1 = sub1.subquery()
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
                  .filter_by(**exactFilterBy)
    for likeKey, likeValue in likeFilterBy.items():
        if likeKey == 'name':
            main1 = main1.filter(Node.name.ilike('%' + likeValue + '%'))
        if likeKey == 'description':
            main1 = main1.filter(Node.description.ilike('%' + likeValue + '%'))
        if likeKey == 'review':
            main1 = main1.filter(Node.review.ilike('%' + likeValue + '%'))
    main1 = main1.subquery()
    asub2  = aliased(sub2)
    asub1=aliased(sub1)
    main1WithNumSubs = db.session.query(main1)\
                  .outerjoin(sub1, main1.c.id==sub1.c.parentId)\
                  .add_columns(select([func.count()]).where(asub1.c.parentId==main1.c.id).label('numberSubs'))\
                  .distinct()\
                  .subquery()
    # outer join sub nodes to main nodes on sub.parentId=main.id
    rows = db.session.query(main1WithNumSubs)\
                  .outerjoin(sub2, main1WithNumSubs.c.id==sub2.c.parentId)\
                  .add_columns(select([func.round(func.avg(asub2.c.averageRating))]).where(asub2.c.parentId==main1WithNumSubs.c.id).label('averageLeafRating'),
                               select([func.sum(asub2.c.needChildren)]).where(asub2.c.parentId==main1WithNumSubs.c.id).label('needLeaves'),
                               select([func.sum(asub2.c.haveTriedChildren)]).where(asub2.c.parentId==main1WithNumSubs.c.id).label('haveTriedLeaves'),
                               select([func.sum(asub2.c.numberChildren)]).where(asub2.c.parentId==main1WithNumSubs.c.id).label('numberLeaves'))\
                   .distinct()
    if limit != -1:
        rows = rows.limit(limit).all()
    else:
        rows = rows.all()
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
        try:
            nodeInfo['needLeaves'] = int(rowDict.pop('needLeaves'))
        except TypeError:
            nodeInfo['needLeaves'] = 0
        try:
            nodeInfo['haveTriedLeaves'] = int(rowDict.pop('haveTriedLeaves'))
        except TypeError:
            nodeInfo['haveTriedLeaves'] = 0
        try:
            nodeInfo['numberLeaves'] = int(rowDict.pop('numberLeaves'))
        except TypeError:
            nodeInfo['numberLeaves'] = 0
        try:
            nodeInfo['numberSubs'] = int(rowDict.pop('numberSubs'))
        except TypeError:
            nodeInfo['numberSubs'] = 0
        node.nodeInfo = nodeInfo
        nodes.append(node)
    if(not excludeRoot):
        nodes.append(rootNode)
    db.session.commit()
    nodesJson = {'nodes':[]}
    nodesJson['nodeCount'] = len(nodes)
    for node in nodes:
        node.childCount = len(node.children);
        nodesJson['nodes'].append(node.buildPublicJson())
    return jsonify(nodesJson)

@main_bp.route('/tree', methods=['GET'])
@auth.login_required
def getTreeWithNode():
    """
    Return the tree starting at the root node that includes the given node to the given depth.
    If excludeRoot is specified, exclude the root node
    """
    validateUser()
    id = request.args.get('id', None)
    depth = int(request.args.get('depth', -1))
    if id is None:
        raise BadRequest('Request must include the id of a Node')
    if depth == -1:
        raise BadRequest('Request must include the desired depth of the tree to retrieve')
    if depth != 3:
        raise BadRequest('Retrieving trees of depth not equal to 3 is not currently supported')
    excludeRoot = 'excludeRoot' in request.args
    rootNode = Node.query.filter_by(parent=None).first()
    node = Node.query.filter_by(id = id).first()
    mainNode = node
    while mainNode.parent is not rootNode:
        mainNode = mainNode.parent
    nodes = [mainNode]
    if(not excludeRoot):
        rootNode = Node.query.filter_by(parent=None).first()
        nodes.append(rootNode)
    # find all descendants of mainNode and add them to nodes
    for mn in mainNode.children:
        nodes.append(mn)
        for cn in mn.children:
            nodes.append(cn)
    nodesJson = {'nodes':[]}
    nodesJson['nodeCount'] = len(nodes)
    for node in nodes:
        node.childCount = len(node.children);
        nodesJson['nodes'].append(node.buildPublicJson())
    return jsonify(nodesJson)

@main_bp.route('/nodes', methods=['GET'])
@auth.login_required
def getNodes():
    """
    Return all the nodes that satisfy the given filter criteria. Tack on the Root node
    unless excludeRoot is specified
    """
    
    level = int(request.args.get('level', -1))
    if 'limit' in request.args:
        try:
            limit = int(request.args.get('limit', ''))
        except ValueError as e:
            raise BadRequest('limit argument must be numeric')
        if limit <= 0:
            raise BadRequest('limit argument must be greater than 0')
    else:
        limit = -1    
    excludeRoot = 'excludeRoot' in request.args
    if level > -1:
        return getNodesFromLevel(level=level, limit=limit, excludeRoot=excludeRoot)
    validateUser()
    exactFilterBy = {}
    likeFilterBy = {}
    excludeRoot = 'excludeRoot' in request.args
    for key,value in iter(request.args.to_dict().items()):
        if key in Node.validExactSearchFields():
            exactFilterBy[key] = value
        if key in Node.validLikeSearchFields():
            likeFilterBy[key] = value
    orderField = request.args.get('orderField', 'name')
    orderDir = request.args.get('orderDir', 'desc')
    if orderField and orderField not in Node.validOrderByFields():
        raise BadRequest('orderField is not valid. Valid fields = ' + str(Node.validOrderByFields()))
    if orderDir.lower() not in ['asc', 'desc']:
        raise BadRequest('orderBy can only be "asc" or "desc"')
    if exactFilterBy.get('ownerId', None):
        ownerQuery = User.query.filter_by(id= exactFilterBy['ownerId'])
        if ownerQuery.count() == 0:
            raise NotFound('Invalid ownername specified in nodes request, so no nodes could be found')
    nodes = Node.query.filter(Node.parent != None).filter_by(**exactFilterBy)
    for likeKey, likeValue in likeFilterBy.items():
        if likeKey == 'name':
            nodes = nodes.filter(Node.name.ilike('%' + likeValue + '%'))
        if likeKey == 'description':
            nodes = nodes.filter(Node.description.ilike('%' + likeValue + '%'))
        if likeKey == 'review':
            nodes = nodes.filter(Node.review.ilike('%' + likeValue + '%'))
    nodes = nodes.order_by(orderField)
    if limit != -1:
        nodes = nodes.limit(limit).all()
    else:
        nodes = nodes.all()    
    if(not excludeRoot):
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
    if not node:
        raise NotFound('Node not found')
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
