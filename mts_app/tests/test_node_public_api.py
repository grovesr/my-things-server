'''
Created on Jun 22, 2018

@author: grovesr
'''
import unittest
from mts_app.tests.drop_all_tables import drop_all_tables
from mts_app import app, db
from mts_app.models import *
from mts_app.config import Config 
from mts_app.tests.helpers import *
from mts_app.helpers import checkDatabasePrerequisites
from sqlalchemy.exc import IntegrityError
from base64 import b64encode
from flask import current_app
from flask.helpers import url_for
import json
from werkzeug.exceptions import BadRequest, HTTPException

authHeaders = {
    'Authorization': 'Basic %s' % b64encode(b"Admin:test").decode("ascii")
}
 
class NodeApiTests(unittest.TestCase):
    adminUser = None
    readonlyUser = None
    editUser = None
    rootNode = None
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        app.config['SERVER_NAME'] = 'localhost:5000'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql://' + 
            Config.DATABASE_USER + ':' +
            Config.DATABASE_PASSWORD + '@' + 
            Config.TEST_DB)
        self.app = app.test_client()                
        db.session.close()
        drop_all_tables(db)
        db.create_all()
        self.createTestAdminUser()
        self.createTestEditUser()
        self.createTestReadonlyUser()
        self.createRootNode()
        self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        db.session.close()
        drop_all_tables(db)
        pass
 
    def createTestAdminUser(self, username='Admin', email='admin@example.com', password="test"):
        self.adminUser = User(username=username, email=email, isAdmin=True, canEdit=True)
        self.adminUser.set_password(password)
        db.session.add(self.adminUser)
        db.session.commit()
        
    def createTestEditUser(self, username='EditUser1', email='edituser1@example.com', password="test"):
        self.editUser = User(username=username, email=email, isAdmin=False, canEdit=True)
        self.editUser.set_password(password)
        db.session.add(self.editUser)
        db.session.commit()
    
    def createTestReadonlyUser(self, username='ReadonlyUser1', email='readonlyuser1@example.com', password="test"):
        self.readonlyUser = User(username=username, email=email, isAdmin=False, canEdit=False)
        self.readonlyUser.set_password(password)
        db.session.add(self.readonlyUser)
        db.session.commit()
        
    def createRootNode(self):
        self.rootNode = Node(name='Root', owner=self.adminUser, parent=None)
        db.session.add(self.rootNode);
        db.session.commit()
        
###############
#### tests ####
###############
    
    def test_get_main_nodes_no_auth(self):

        response = self.app.get(Config.API_PREFIX + '/get/main/nodes')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_get_main_nodes_no_nodes_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"ReadonlyUser1:test").decode("ascii")
        }
        
        response = self.app.get(Config.API_PREFIX + '/get/main/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual('No main nodes found', response.json['error'])
    
    def test_get_main_nodes_no_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"EditUser1:test").decode("ascii")
        }
        
        response = self.app.get(Config.API_PREFIX + '/get/main/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual('No main nodes found', response.json['error'])
    
    
    def test_add_main_node_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"EditUser1:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.id, 'parent':self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        self.assertIn('name', response.json)
        self.assertEqual('MainNode1', response.json['name'])
        self.assertIn('owner', response.json)
        self.assertEqual(self.editUser.id, response.json['owner'])
        self.assertIn('parent', response.json)
        self.assertEqual(self.rootNode.id, response.json['parent'])
        self.assertIn('uri', response.json)
        with app.app_context():
            self.assertEqual(url_for('getNode',nodeName='Mainode1', 
                                     owner=self.editUser.id, parent=self.rootNode.id, 
                                     _external=True), response.json['uri'])
        
    def test_add_main_node_bad_owner_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"EditUser1:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':'foo', 'parent':self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 404)  
        self.assertIn('error', response.json)
        self.assertEqual('Owner not found. Can''t create node', response.json['error'])
    
    def test_add_main_node_bad_parent_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"EditUser1:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.id, 'parent':'foo'}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 404)  
        self.assertIn('error', response.json)
        self.assertEqual('Parent not found. Can''t create node', response.json['error'])        
    
    def test_add_main_node_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"ReadonlyUser1:test").decode("ascii")
        }
        data={'name':'ParentNode1', 'owner':self.editUser.id, 'parent':self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('User doesn''t have edit permission', response.json['error'])
        
    def test_add_main_node_bad_owner_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"EditUser1:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':'foo', 'parent':self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 403)  
        self.assertIn('error', response.json)
        self.assertEqual('User doesn''t have edit permission', response.json['error'])
    
    def test_add_main_node_bad_parent_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"EditUser1:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.id, 'parent':'foo'}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 403)  
        self.assertIn('error', response.json)
        self.assertEqual('User doesn''t have edit permission', response.json['error'])
        
    def test_get_main_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"EditUser1:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.id, 'parent':self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode2', 'owner':self.editUser.id, 'parent':self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201) 
        response = self.app.get(Config.API_PREFIX + '/get/parent/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(2, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        mainNodeJson1 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'MainNode1'][0]
        mainNodeJson2 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'MainNode2'][0]
        self.assertIn('name', mainNodeJson1)
        self.assertEqual('MainNode1', mainNodeJson1['name'])
        self.assertIn('owner', mainNodeJson1)
        self.assertEqual(self.editUser.id, mainNodeJson1['owner'])
        self.assertIn('parent', mainNodeJson1)
        self.assertEqual(self.rootNode.id, mainNodeJson1['parent'])
        self.assertIn('uri',mainNodeJson1)
        self.assertIn('uri',mainNodeJson1)
        with app.app_context():
            self.assertEqual(url_for('getNode',nodeName='MainNode1', 
                                     owner=self.editUser.id, parent=self.rootNode.id, 
                                     _external=True), mainNodeJson1['uri'])
        self.assertIn('name', mainNodeJson2)
        self.assertEqual('MainNode2', mainNodeJson2['name'])
        self.assertIn('owner', mainNodeJson2)
        self.assertEqual(self.editUser.id, mainNodeJson2['owner'])
        self.assertIn('parent', mainNodeJson2)
        self.assertEqual(self.rootNode.id, mainNodeJson2['parent'])
        self.assertIn('uri',mainNodeJson2)
        self.assertIn('uri',mainNodeJson2)
        with app.app_context():
            self.assertEqual(url_for('getNode',nodeName='MainNode2', 
                                     owner=self.editUser.id, parent=self.rootNode.id, 
                                     _external=True), mainNodeJson2['uri'])
            
    def test_get_parent_nodes_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"EditUser1:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.id, 'parent':self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode2', 'owner':self.editUser.id, 'parent':self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201) 
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"ReadonlyUser1:test").decode("ascii")
        }
        response = self.app.get(Config.API_PREFIX + '/get/parent/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(2, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        mainNodeJson1 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'MainNode1'][0]
        mainNodeJson2 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'MainNode2'][0]
        self.assertIn('name', mainNodeJson1)
        self.assertEqual('MainNode1', mainNodeJson1['name'])
        self.assertIn('owner', mainNodeJson1)
        self.assertEqual(self.editUser.id, mainNodeJson1['owner'])
        self.assertIn('parent', mainNodeJson1)
        self.assertEqual(self.rootNode.id, mainNodeJson1['parent'])
        self.assertIn('uri',mainNodeJson1)
        self.assertIn('uri',mainNodeJson1)
        with app.app_context():
            self.assertEqual(url_for('getNode',nodeName='MainNode1', 
                                     owner=self.editUser.id, parent=self.rootNode.id, 
                                     _external=True), mainNodeJson1['uri'])
        self.assertIn('name', mainNodeJson2)
        self.assertEqual('MainNode2', mainNodeJson2['name'])
        self.assertIn('owner', mainNodeJson2)
        self.assertEqual(self.editUser.id, mainNodeJson2['owner'])
        self.assertIn('parent', mainNodeJson2)
        self.assertEqual(self.rootNode.id, mainNodeJson2['parent'])
        self.assertIn('uri',mainNodeJson2)
        self.assertIn('uri',mainNodeJson2)
        with app.app_context():
            self.assertEqual(url_for('getNode',nodeName='MainNode2', 
                                     owner=self.editUser.id, parent=self.rootNode.id, 
                                     _external=True), mainNodeJson2['uri'])
        
    def test_create_two_equal_main_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"EditUser1:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.id, 'parent':self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        data={'name':'MainNode1', 'owner':self.editUser.id, 'parent':self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertIn('error', response.json)
        self.assertIn('This node already exists:', response.json['error'])
        
    def test_create_two_equal_sub_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"EditUser1:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.id, 'root':self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'SubNode1', 'owner':self.editUser.id, 'parent': self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        data={'name':'SubNode1', 'owner':self.editUser.id, 'parent': self.rootNode.id}
        response = self.app.post(Config.API_PREFIX + '/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertIn('error', response.json)
        self.assertIn('This node already exists:', response.json['error'])
        
    
    def test_create_two_main_nodes_each_with_two_subnodes_each_with_two_subsubnodes_for_user_edit_access(self):
        user = create_user_with_index('Test', 1)
        mainNodes = create_two_main_nodes_for_owner(user)
        for mainNode in mainNodes:
            subNodes = create_two_sub_nodes_for_parent_node(mainNode)
            for subNode in subNodes:
                create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy we can test against
        self.assertEqual(1, 1)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()