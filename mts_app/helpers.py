'''
Created on Jun 29, 2018

@author: grovesr
'''
from mts_app.models import db
from mts_app.models import User, Node
from mts_app.config import Config
from werkzeug.exceptions import InternalServerError
from dns.name import root

def checkDatabasePrerequisites():
    # make sure that the database has an admin user and a root node
    adminQuery=User.query.filter_by(username='Admin')
    if adminQuery.count() == 0:
    # create admin user using secrets
        admin = User(username=Config.ADMIN_USERNAME, email=Config.ADMIN_USER_EMAIL, isAdmin=True, canEdit=True)
        admin.set_password(Config.ADMIN_USER_PASSWORD)
        db.session.add(admin)
        db.session.commit()
    else:
        admin = adminQuery.first()
    rootNodeQuery = Node.query.filter_by(name=Config.ROOT_NODE_NAME, owner=admin)
    if rootNodeQuery.count() > 1:
        raise RuntimeError('More than one root node found. The database is corrupted. Fix and try again')
    if rootNodeQuery.count() == 0:
        rootNode = Node(name=Config.ROOT_NODE_NAME, owner=admin)
        db.session.add(rootNode)
        db.session.commit()
