'''
Created on Jun 25, 2018

@author: grovesr
'''
from mts_app.models import db
from mts_app.models import *

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

def create_node_for_owner_with_index(owner, nodeIndex=1, parent=None, type='foo'):
    node = Node(name='node:Main Node, owner:' + owner.username + '_' + str(nodeIndex), owner=owner, parent=parent, type=type)
    db.session.add(node)
    db.session.commit()
    return node

def create_two_main_nodes_for_owner(owner, parent=None, type='foo'):        
    return [create_node_for_owner_with_index(owner=owner, parent=parent, nodeIndex=1, type=type), create_node_for_owner_with_index(owner, parent=parent, nodeIndex=2, type=type)]

def create_two_sub_nodes_for_parent_node(parentNode):
    owner = parentNode.owner       
    subnode1 = Node(name='node:Sub Node 1, parent:' + parentNode.name, parent=parentNode, owner=owner, type=parentNode.type)
    subnode2 = Node(name='node:Sub Node 2, parent:' + parentNode.name, parent=parentNode, owner=owner, type=parentNode.type)
    db.session.add(subnode1)
    db.session.add(subnode2)
    db.session.commit()
    return parentNode.children
