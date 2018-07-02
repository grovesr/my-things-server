'''
Created on Jun 22, 2018

@author: grovesr
'''

from mts_app import create_app
from mts_app.models import User, Node, db
from mts_app.config import Config 
from mts_app.tests.helpers import *
from mts_app.tests.MyThingsTest import MyThingsTest
from mts_app.helpers import checkDatabasePrerequisites
from sqlalchemy.exc import IntegrityError
from base64 import b64encode
from flask import current_app
from flask.helpers import url_for
import json
from werkzeug.exceptions import BadRequest, HTTPException
from mts_app.admin.routes import auth

authHeaders = {
    'Authorization': 'Basic %s' % b64encode(b"Admin:test").decode("ascii")
}
 
class NodeApiTests(MyThingsTest):
    
###############
#### tests ####
###############
    
    def test_get_main_nodes_no_auth(self):

        response = self.client.get('/get/main/nodes')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_get_main_nodes_bad_login_creds(self):
        authHeaders = {'Authorization': 'Basic %s' % b64encode(b"foo:bar").decode("ascii")
                       }
        response = self.client.get('/get/main/nodes')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_get_main_nodes_no_nodes_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        
        response = self.client.get('/get/main/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual('No main nodes found', response.json['error'])
    
    def test_get_main_nodes_no_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        
        response = self.client.get('/get/main/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual('No main nodes found', response.json['error'])
    
    
    def test_add_node_bad_method_get(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.get('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)  
        
    def test_add_node_bad_method_put(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.put('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405) 
        
    def test_add_node_bad_method_delete(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.delete('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405) 
    
    def test_update_node_bad_method_post(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode1new', 'type':'newType', 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5} 
        response = self.client.post('/update/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_update_node_bad_method_get(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode1new', 'type':'newType', 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5} 
        response = self.client.get('/update/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_update_node_bad_method_delete(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode1new', 'type':'newType', 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5} 
        response = self.client.delete('/update/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    
    def test_get_main_nodes_bad_method_post(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode2', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201) 
        response = self.client.post('/get/main/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_get_main_nodes_bad_method_put(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode2', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201) 
        response = self.client.put('/get/main/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_get_main_nodes_bad_method_delete(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode2', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201) 
        response = self.client.delete('/get/main/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 405)
    
    def test_get_nodes_bad_method_post(self):
        users = [create_user_with_index('Test', 1),
                 create_user_with_index('Test', 2)]
        for user in users:
            mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
            for mainNode in mainNodes:
                subNodes = create_two_sub_nodes_for_parent_node(mainNode)
                for subNode in subNodes:
                    create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy for two different users we can test against
        response = self.client.post('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 405)
        
    def test_get_nodes_bad_method_put(self):
        users = [create_user_with_index('Test', 1),
                 create_user_with_index('Test', 2)]
        for user in users:
            mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
            for mainNode in mainNodes:
                subNodes = create_two_sub_nodes_for_parent_node(mainNode)
                for subNode in subNodes:
                    create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy for two different users we can test against
        response = self.client.put('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 405)
        
    def test_get_nodes_bad_method_delete(self):
        users = [create_user_with_index('Test', 1),
                 create_user_with_index('Test', 2)]
        for user in users:
            mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
            for mainNode in mainNodes:
                subNodes = create_two_sub_nodes_for_parent_node(mainNode)
                for subNode in subNodes:
                    create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy for two different users we can test against
        response = self.client.delete('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 405)
    
    def test_get_node_bad_method_put(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        response = self.client.put('/get/node/' + str(response.json['id']),
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)
    
    def test_get_node_bad_method_postt(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        response = self.client.post('/get/node/' + str(response.json['id']),
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_get_node_bad_method_delete(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        response = self.client.delete('/get/node/' + str(response.json['id']),
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)
    
    def test_delete_node_bad_method_post(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        response = self.client.post('/delete/node/' + str(response.json['id']),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_delete_node_bad_method_get(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        response = self.client.get('/delete/node/' + str(response.json['id']),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_delete_node_bad_method_put(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        response = self.client.put('/delete/node/' + str(response.json['id']),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)
    
    def test_add_main_node_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        self.assertIn('name', response.json)
        self.assertEqual('MainNode1', response.json['name'])
        self.assertIn('ownerName', response.json)
        self.assertEqual(self.editUser.username, response.json['ownerName'])
        self.assertIn('ownerId', response.json)
        self.assertEqual(self.editUser.id, response.json['ownerId'])
        self.assertIn('parentName', response.json)
        self.assertEqual(self.rootNode.name, response.json['parentName'])
        self.assertIn('parentId', response.json)
        self.assertEqual(self.rootNode.id, response.json['parentId'])
        self.assertIn('uri', response.json)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNode',nodeId=response.json['id'], 
                                     _external=True), response.json['uri'])
        
    def test_get_node_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        response = self.client.get('/get/node/' + str(response.json['id']),
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.json)
        self.assertEqual('MainNode1', response.json['name'])
        self.assertIn('uri', response.json)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNode',nodeId=response.json['id'], 
                                     _external=True), response.json['uri'])
        
    def test_update_node_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode1new', 'type':'newType', 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5} 
        response = self.client.put('/update/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.json)
        self.assertEqual('MainNode1new', response.json['name'])
        self.assertIn('type', response.json)
        self.assertEqual('newType', response.json['type'])
        self.assertIn('description', response.json)
        self.assertEqual('newDescription', response.json['description'])
        self.assertIn('nodeInfo', response.json)
        self.assertEqual(json.dumps({"new":"info"}), response.json['nodeInfo'])
        self.assertIn('haveTried', response.json)
        self.assertEqual(True, response.json['haveTried'])
        self.assertIn('review', response.json)
        self.assertEqual('newReview', response.json['review'])
        self.assertIn('rating', response.json)
        self.assertEqual(5, response.json['rating'])
        self.assertIn('uri', response.json)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNode',nodeId=response.json['id'], 
                                     _external=True), response.json['uri'])
            
    def test_update_node_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        data={'name':'MainNode1new', 'type':'newType', 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5} 
        response = self.client.put('/update/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('User doesn''t have edit permission', response.json['error'])
        
        
    def test_add_main_node_bad_owner_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':'foo'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 404)  
        self.assertIn('error', response.json)
        self.assertEqual('Owner not found. Can''t create node', response.json['error'])
    
    def test_add_main_node_bad_parent_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'parentId':'foo'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 404)  
        self.assertIn('error', response.json)
        self.assertEqual('Parent not found. Can''t create node', response.json['error'])        
    
    def test_add_main_node_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        data={'name':'ParentNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('User doesn''t have edit permission', response.json['error'])
        
    def test_add_main_node_bad_owner_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':'foo', 'parentId':self.rootNode.id}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 403)  
        self.assertIn('error', response.json)
        self.assertEqual('User doesn''t have edit permission', response.json['error'])
    
    def test_add_main_node_bad_parent_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'parentId':'foo'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 403)  
        self.assertIn('error', response.json)
        self.assertEqual('User doesn''t have edit permission', response.json['error'])
        
    def test_get_main_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode2', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201) 
        response = self.client.get('/get/main/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(2, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        mainNodeJson1 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'MainNode1'][0]
        mainNodeJson2 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'MainNode2'][0]
        self.assertIn('name', mainNodeJson1)
        self.assertEqual('MainNode1', mainNodeJson1['name'])
        self.assertIn('ownerName', mainNodeJson1)
        self.assertEqual(self.editUser.username, mainNodeJson1['ownerName'])
        self.assertIn('ownerId', mainNodeJson1)
        self.assertEqual(self.editUser.id, mainNodeJson1['ownerId'])
        self.assertIn('parentName', mainNodeJson1)
        self.assertEqual(self.rootNode.name, mainNodeJson1['parentName'])
        self.assertIn('parentId', mainNodeJson1)
        self.assertEqual(self.rootNode.id, mainNodeJson1['parentId'])
        self.assertIn('uri',mainNodeJson1)
        self.assertIn('uri',mainNodeJson1)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNode',nodeId=mainNodeJson1['id'], 
                                     _external=True), mainNodeJson1['uri'])
        self.assertIn('name', mainNodeJson2)
        self.assertEqual('MainNode2', mainNodeJson2['name'])
        self.assertIn('ownerName', mainNodeJson2)
        self.assertEqual(self.editUser.username, mainNodeJson2['ownerName'])
        self.assertIn('ownerId', mainNodeJson2)
        self.assertEqual(self.editUser.id, mainNodeJson2['ownerId'])
        self.assertIn('parentName', mainNodeJson2)
        self.assertEqual(self.rootNode.name, mainNodeJson2['parentName'])
        self.assertIn('parentId', mainNodeJson2)
        self.assertEqual(self.rootNode.id, mainNodeJson2['parentId'])
        self.assertIn('uri',mainNodeJson2)
        self.assertIn('uri',mainNodeJson2)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNode',nodeId=mainNodeJson2['id'],
                                     _external=True), mainNodeJson2['uri'])
            
    def test_get_main_nodes_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode2', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201) 
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        response = self.client.get('/get/main/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(2, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        mainNodeJson1 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'MainNode1'][0]
        mainNodeJson2 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'MainNode2'][0]
        self.assertIn('name', mainNodeJson1)
        self.assertEqual('MainNode1', mainNodeJson1['name'])
        self.assertIn('ownerName', mainNodeJson1)
        self.assertEqual(self.editUser.username, mainNodeJson1['ownerName'])
        self.assertIn('ownerId', mainNodeJson1)
        self.assertEqual(self.editUser.id, mainNodeJson1['ownerId'])
        self.assertIn('parentName', mainNodeJson1)
        self.assertEqual(self.rootNode.name, mainNodeJson1['parentName'])
        self.assertIn('parentId', mainNodeJson1)
        self.assertEqual(self.rootNode.id, mainNodeJson1['parentId'])
        self.assertIn('uri',mainNodeJson1)
        self.assertIn('uri',mainNodeJson1)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNode',nodeId=mainNodeJson1['id'],
                                     _external=True), mainNodeJson1['uri'])
        self.assertIn('name', mainNodeJson2)
        self.assertEqual('MainNode2', mainNodeJson2['name'])
        self.assertIn('ownerName', mainNodeJson2)
        self.assertEqual(self.editUser.username, mainNodeJson2['ownerName'])
        self.assertIn('ownerId', mainNodeJson2)
        self.assertEqual(self.editUser.id, mainNodeJson2['ownerId'])
        self.assertIn('parentName', mainNodeJson2)
        self.assertEqual(self.rootNode.name, mainNodeJson2['parentName'])
        self.assertIn('parentId', mainNodeJson2)
        self.assertEqual(self.rootNode.id, mainNodeJson2['parentId'])
        self.assertIn('uri',mainNodeJson2)
        self.assertIn('uri',mainNodeJson2)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNode',nodeId=mainNodeJson2['id'],
                                     _external=True), mainNodeJson2['uri'])
        
    def test_create_two_equal_main_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertIn('This node already exists:', response.json['error'])
        
    def test_delete_node_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        response = self.client.delete('/delete/node/' + str(response.json['id']),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('result', response.json)
        self.assertEqual(True, response.json['result'])
        
    def test_delete_node_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        response = self.client.delete('/delete/node/' + str(response.json['id']),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('User doesn''t have edit permission', response.json['error'])
        
    def test_delete_root_node_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        response = self.client.delete('/delete/node/' + str(self.rootNode.id),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Deletion of the Root node is not permitted', response.json['error'])
        
    def test_create_duplicate_root_node(self):
        data={'name':'Root', 'owner':self.adminUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 403)  
        self.assertIn('error', response.json)
        self.assertIn('There can be only one Root node', response.json['error'])
        
    def test_create_two_equal_sub_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        parentId = response.json['id']
        self.assertEqual(response.status_code, 201)
        data={'name':'SubNode1', 'owner':self.editUser.username, 'parentId': parentId}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        data={'name':'SubNode1', 'owner':self.editUser.username, 'parentId': parentId}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertIn('This node already exists:', response.json['error'])
        
    
    def test_create_two_main_nodes_each_with_two_subnodes_each_with_two_subsubnodes_for_user_edit_access(self):
        user = create_user_with_index('Test', 1)
        mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
        for mainNode in mainNodes:
            subNodes = create_two_sub_nodes_for_parent_node(mainNode)
            for subNode in subNodes:
                create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy we can test against
        response = self.client.get('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(response.json['nodeCount'], 14)
        response = self.client.get('/get/main/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(response.json['nodeCount'], 2)
        
    def test_get_nodes_three_level_single_user_edit_access(self):
        users = [create_user_with_index('Test', 1),
                 create_user_with_index('Test', 2)]
        for user in users:
            mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
            for mainNode in mainNodes:
                subNodes = create_two_sub_nodes_for_parent_node(mainNode)
                for subNode in subNodes:
                    create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy for two different users we can test against
        response = self.client.get('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(response.json['nodeCount'], 28)
        
    def test_create_two_main_nodes_each_with_two_subnodes_each_with_two_subsubnodes_for_two_users_edit_access(self):
        users = [create_user_with_index('Test', 1),
                 create_user_with_index('Test', 2)]
        for user in users:
            mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
            for mainNode in mainNodes:
                subNodes = create_two_sub_nodes_for_parent_node(mainNode)
                for subNode in subNodes:
                    create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy for two different users we can test against
        response = self.client.get('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(response.json['nodeCount'], 28)
        response = self.client.get('/get/main/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(response.json['nodeCount'], 4)
        
    def test_create_two_main_nodes_each_with_two_subnodes_each_with_two_subsubnodes_for_two_users_delete_one_main_node_edit_access(self):
        users = [create_user_with_index('Test', 1),
                 create_user_with_index('Test', 2)]
        for user in users:
            mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
            for mainNode in mainNodes:
                subNodes = create_two_sub_nodes_for_parent_node(mainNode)
                for subNode in subNodes:
                    create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy for two different users we can test against
        response = self.client.get('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(response.json['nodeCount'], 28)
        mainNode = Node.query.filter(Node.owner==users[0], Node.parent==self.rootNode).first()
        response = self.client.delete('/delete/node/' + str(mainNode.id), headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(response.json['nodeCount'], 21)
        
    def test_create_two_main_nodes_each_with_two_subnodes_each_with_two_subsubnodes_for_two_users_delete_one_sub_node_edit_access(self):
        users = [create_user_with_index('Test', 1),
                 create_user_with_index('Test', 2)]
        for user in users:
            mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
            for mainNode in mainNodes:
                subNodes = create_two_sub_nodes_for_parent_node(mainNode)
                for subNode in subNodes:
                    create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy for two different users we can test against
        response = self.client.get('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(response.json['nodeCount'], 28)
        mainNode = Node.query.filter(Node.owner==users[0], Node.parent==self.rootNode).first()
        subNode = mainNode.children[0]
        response = self.client.delete('/delete/node/' + str(subNode.id), headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(response.json['nodeCount'], 25)
        
    def test_create_two_main_nodes_each_with_two_subnodes_each_with_two_subsubnodes_for_two_users_delete_one_user_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        users = [create_user_with_index('Test', 1),
                 create_user_with_index('Test', 2)]
        for user in users:
            mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
            for mainNode in mainNodes:
                subNodes = create_two_sub_nodes_for_parent_node(mainNode)
                for subNode in subNodes:
                    create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy for two different users we can test against
        response = self.client.get('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(response.json['nodeCount'], 28)
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Admin:test").decode("ascii")
        }
        response = self.client.delete('/admin/delete/user/' + users[0].username, headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/get/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(response.json['nodeCount'], 14)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()