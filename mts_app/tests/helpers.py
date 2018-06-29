'''
Created on Jun 25, 2018

@author: grovesr
'''
from mts_app import app, db
from mts_app.models import *

# def createTestAdminUser(username='Admin', email='admin@example.com', password="test"):
#     adminQuery = User.query.filter_by(username=username, email=email, isAdmin=True, canEdit=True)
#     if adminQuery.count() > 1:
#         return adminQuery.first()
#     admin = User(username=username, email=email, isAdmin=True, canEdit=True)
#     admin.set_password(password)
#     db.session.add(admin)
#     db.session.commit()
#     return admin
# 
# def createTestReadonlyUser(username='Readonly', email='readonly@example.com', password="test"):
#     readonlyQuery = User.query.filter_by(username=username, email=email, isAdmin=False, canEdit=False)
#     if readonlyQuery.count() > 1:
#         return readonlyQuery.first()
#     readonly = User(username=username, email=email, isAdmin=False, canEdit=False)
#     readonly.set_password(password)
#     db.session.add(readonly)
#     db.session.commit()
#     return readonly
# 
# def createTestEditUser(username='Edit', email='edit@example.com', password="test"):
#     editQuery = User.query.filter_by(username=username, email=email, isAdmin=False, canEdit=True)
#     if editQuery.count() > 1:
#         return editQuery.first()
#     edit = User(username=username, email=email, isAdmin=False, canEdit=True)
#     edit.set_password(password)
#     db.session.add(edit)
#     db.session.commit()
#     return edit
# 
# def createRootNode():
#     admin=User.query.filter_by(username='Admin').first()
#     rootNodeQuery = Node.query.filter_by(name='Root', owner=admin, parent=None)
#     if rootNodeQuery.count() == 1:
#         return rootNodeQuery.first()
#     node = Node(name='Root', owner=admin, parent=None)
#     db.session.add(node);
#     db.session.commit()
#     return node

def create_user_with_index(username='Test', userindex=1):
    user = User(username=username + str(userindex), email=username.lower() + str(userindex) + '@example.com')
    user.set_password("password")
    db.session.add(user)
    db.session.commit()
    return user

def create_three_users():
    user1 = create_user_with_index(userindex=1)
    user2 = create_user_with_index(userindex=2)
    user3 = create_user_with_index(userindex=3)
    return [user1, user2, user3]

def create_node_for_owner_with_index(owner, nodeIndex=1, parent=None):
    node = Node(name='node:Main Node, owner:' + owner.username + '_' + str(nodeIndex), owner=owner, parent=parent)
    db.session.add(node)
    db.session.commit()
    return node
    
def create_two_main_nodes_for_owner(owner):        
    return [create_node_for_owner_with_index(owner, 1), create_node_for_owner_with_index(owner, 2)]

def create_two_sub_nodes_for_parent_node(parentNode):
    owner = parentNode.owner       
    parentNode.children=[Node(name='node:Sub Node 1, parent:' + parentNode.name, parent=parentNode, owner=owner),
                         Node(name='node:Sub Node 2, parent:' + parentNode.name, parent=parentNode, owner=owner)]
    db.session.add(parentNode)
    db.session.commit()
    return parentNode.children
