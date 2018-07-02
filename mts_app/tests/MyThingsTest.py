'''
Created on Jul 1, 2018

@author: grovesr
'''

import unittest
from mts_app.models import User, Node, db
from mts_app import create_app
from mts_app.tests.drop_all_tables import drop_all_tables
from flask import current_app

class MyThingsTest(unittest.TestCase):
    '''
    classdocs
    '''
    adminUser = None
    readonlyUser = None
    editUser = None
    rootNode = None
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.session.remove()
        drop_all_tables(db)
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.adminUser = self.createTestAdminUser(username='Admin', email='admin@example.com', password="test")
        self.rootNode = self.createRootNode()
        self.editUser = self.createTestEditUser()
        self.readonlyUser = self.createTestReadonlyUser()
        self.assertEqual(current_app.debug, False)
 
    # executed after each test
    def tearDown(self):
        db.session.remove()
        drop_all_tables(db)
        self.app_context.pop()
        pass

    def createTestAdminUser(self, username='Admin', email='admin@example.com', password="test"):
        adminQuery = User.query.filter_by(username=username, email=email, isAdmin=True, canEdit=True)
        if adminQuery.count() > 1:
            return adminQuery.first()
        admin = User(username=username, email=email, isAdmin=True, canEdit=True)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        return admin
     
    def createTestReadonlyUser(self, username='Readonly', email='readonly@example.com', password="test"):
        readonlyQuery = User.query.filter_by(username=username, email=email, isAdmin=False, canEdit=False)
        if readonlyQuery.count() > 1:
            return readonlyQuery.first()
        readonly = User(username=username, email=email, isAdmin=False, canEdit=False)
        readonly.set_password(password)
        db.session.add(readonly)
        db.session.commit()
        return readonly
     
    def createTestEditUser(self, username='Edit', email='edit@example.com', password="test"):
        editQuery = User.query.filter_by(username=username, email=email, isAdmin=False, canEdit=True)
        if editQuery.count() > 1:
            return editQuery.first()
        edit = User(username=username, email=email, isAdmin=False, canEdit=True)
        edit.set_password(password)
        db.session.add(edit)
        db.session.commit()
        return edit
     
    def createRootNode(self):
        admin=User.query.filter_by(username='Admin').first()
        rootNodeQuery = Node.query.filter_by(name='Root', owner=admin, parent=None)
        if rootNodeQuery.count() == 1:
            return rootNodeQuery.first()
        node = Node(name='Root', owner=admin, parent=None)
        db.session.add(node);
        db.session.commit()
        return node
        