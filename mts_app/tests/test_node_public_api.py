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
from dateutil.parser import parser

authHeaders = {
    'Authorization': 'Basic %s' % b64encode(b"Admin:test").decode("ascii")
}
 
class NodeApiTests(MyThingsTest):
    
###############
#### tests ####
###############
    
    def test_get_main_nodes_no_auth(self):

        response = self.client.get('/main/nodes')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_get_main_nodes_bad_login_creds(self):
        authHeaders = {'Authorization': 'Basic %s' % b64encode(b"foo:bar").decode("ascii")
                       }
        response = self.client.get('/main/nodes')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_get_main_nodes_no_nodes_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        
        response = self.client.get('/main/nodes', headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(1, response.json['nodeCount'])
    
    def test_get_main_nodes_no_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        
        response = self.client.get('/main/nodes', headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(1, response.json['nodeCount'])
    
    
    def test_add_node_bad_method_get(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.get('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)  
        
    def test_add_node_bad_method_put(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.put('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405) 
        
    def test_add_node_bad_method_delete(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.delete('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405) 
    
    def test_update_node_bad_method_post(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode1new', 'type':'newType', 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5} 
        response = self.client.post('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)
    
    def test_get_main_nodes_bad_method_post(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode2', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201) 
        response = self.client.post('/main/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_get_main_nodes_bad_method_put(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode2', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201) 
        response = self.client.put('/main/nodes', headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_get_main_nodes_bad_method_delete(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode2', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201) 
        response = self.client.delete('/main/nodes', headers=authHeaders)
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
        response = self.client.post('/nodes', headers=authHeaders, 
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
        response = self.client.put('/nodes', headers=authHeaders, 
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
        response = self.client.delete('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 405)
    
    def test_get_node_bad_method_post(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        response = self.client.post('/node/' + str(response.json['id']),
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)
    
    def test_delete_node_bad_method_post(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        response = self.client.post('/node/' + str(response.json['id']),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 405)

    def test_add_node_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner': self.editUser.username, 'type':'Type', 'description':'Description',
              'nodeInfo':{'node':'info'}, 'haveTried':True, 'review':'Review',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)  
        self.assertIn('name', response.json)
        self.assertEqual('MainNode1', response.json['name'])
        self.assertIn('type', response.json)
        self.assertEqual('Type', response.json['type'])
        self.assertIn('description', response.json)
        self.assertEqual('Description', response.json['description'])
        self.assertIn('nodeInfo', response.json)
        self.assertEqual({'node':'info'}, response.json['nodeInfo'])
        self.assertIn('haveTried', response.json)
        self.assertEqual(True, response.json['haveTried'])
        self.assertIn('dateTried', response.json)
        self.assertEqual('2018/06/11', response.json['dateTried'])
        self.assertIn('review', response.json)
        self.assertEqual('Review', response.json['review'])
        self.assertIn('rating', response.json)
        self.assertEqual(5, response.json['rating'])
        self.assertIn('dateReviewed', response.json)
        self.assertEqual('2018/06/11', response.json['dateReviewed'])
        self.assertIn('uri', response.json)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNodeFromId',nodeId=response.json['id'], 
                                     _external=True), response.json['uri'])
        
    def test_get_node_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        response = self.client.get('/node/' + str(response.json['id']),
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.json)
        self.assertEqual('MainNode1', response.json['name'])
        self.assertIn('uri', response.json)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNodeFromId',nodeId=response.json['id'], 
                                     _external=True), response.json['uri'])
            
    def test_update_node_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(response.status_code, 201)
        data={'name':'MainNode1new', 'type':'newType', 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018',
              'sortIndex':4, 'need':False} 
        response = self.client.put('/node/' + str(response.json['id']),
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
        self.assertEqual({'new':'info'}, response.json['nodeInfo'])
        self.assertIn('haveTried', response.json)
        self.assertEqual(True, response.json['haveTried'])
        self.assertIn('dateTried', response.json)
        self.assertEqual('2018/06/11', response.json['dateTried'])
        self.assertIn('review', response.json)
        self.assertEqual('newReview', response.json['review'])
        self.assertIn('rating', response.json)
        self.assertEqual(5, response.json['rating'])
        self.assertIn('dateReviewed', response.json)
        self.assertEqual('2018/06/11', response.json['dateReviewed'])
        self.assertIn('sortIndex', response.json)
        self.assertEqual(4, response.json['sortIndex'])
        self.assertIn('need', response.json)
        self.assertEqual(False, response.json['need'])
        self.assertIn('uri', response.json)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNodeFromId',nodeId=response.json['id'], 
                                     _external=True), response.json['uri'])
    
    def test_update_node_empty_name(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'', 'type':'newType', 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided name is either empty or > 128 characters long', response.json['error'])
    
    def test_update_node_long_name(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':''.join('x' for i in range(129)), 'type':'newType', 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided name is either empty or > 128 characters long', response.json['error'])
        
    def test_update_node_empty_type(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'', 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided type is either empty or > 16 characters long', response.json['error'])
        
    def test_update_node_null_type(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type':'type'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':None, 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('type', response.json)
        self.assertEqual(None, response.json['type'])
        
    def test_update_node_long_type(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':''.join('x' for i in range(17)), 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided type is either empty or > 16 characters long', response.json['error'])
        
    def test_update_node_non_string_description(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':0,
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided description is not a string', response.json['error'])
        
    def test_update_node_null_description(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'description':'description', 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':None,
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('description', response.json)
        self.assertEqual(None, response.json['description'])
        
    def test_update_node_non_dict_nodeInfo(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':'foo', 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided nodeInfo is not json serializable', response.json['error'])
        
    def test_update_node_non_boolean_haveTried(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':'foo', 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('haveTried must resolve to a Boolean type', response.json['error'])
        
    def test_update_node_non_boolean_need(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018',
              'need': 'foo'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('need must resolve to a Boolean type', response.json['error'])
    
    def test_update_node_non_string_review(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':0,
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided review is not a string', response.json['error'])
        
    def test_update_node_null_review(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'review':'review', 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':None,
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('review', response.json)
        self.assertEqual(None, response.json['review'])
        
    def test_update_node_non_numeric_rating(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':'foo', 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided rating must resolve to a number', response.json['error'])
        
    def test_update_node_null_rating(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'rating':5, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':None, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('rating', response.json)
        self.assertEqual(None, response.json['rating'])
        
    def test_update_node_empty_rating(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'rating':5, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':'', 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('rating', response.json)
        self.assertEqual(None, response.json['rating'])
        
    def test_update_node_negative_rating(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':-1, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided rating must be a number between 0 and 10', response.json['error'])
        
    def test_update_node_greater_than_10_rating(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':11, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided rating must be a number between 0 and 10', response.json['error'])
        
    def test_update_node_invalid_dateTried(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'foo', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided dateTried is not a valid date format', response.json['error'])
        
    def test_update_node_null_dateTried(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'dateTried':'06/11/2018', 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':None, 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('dateTried', response.json)
        self.assertEqual(None, response.json['dateTried'])
        
    def test_update_node_empty_dateTried(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'dateTried':'06/11/2018', 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'', 'dateReviewed':'06/11/2018'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('dateTried', response.json)
        self.assertEqual(None, response.json['dateTried'])
        
    def test_update_node_invalid_dateReviewed(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'foo'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided dateReviewed is not a valid date format', response.json['error'])
        
    def test_update_node_null_dateReviewed(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'dateReviewed':'06/11/2018', 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':None} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('dateReviewed', response.json)
        self.assertEqual(None, response.json['dateReviewed'])    
    
    def test_update_node_empty_dateReviewed(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'dateReviewed':'06/11/2018', 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':''} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('dateReviewed', response.json)
        self.assertEqual(None, response.json['dateReviewed'])
    
    def test_update_node_invalid_sortIndex(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018',
              'sortIndex':'foo'} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided sortIndex must resolve to a number', response.json['error'])
        
    def test_update_node_negative_sortIndex(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018',
              'sortIndex':-1} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Provided sortIndex must be an integer > 0', response.json['error'])
        
    def test_update_node_null_sortIndex(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'sortIndex':5, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018',
              'sortIndex':None} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('sortIndex', response.json)
        self.assertEqual(None, response.json['sortIndex'])
        
    def test_update_node_empty_sortIndex(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'sortIndex':5, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode1', 'type':'newType', 'description':'newDescriotion',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5, 'dateTried':'06/11/2018', 'dateReviewed':'06/11/2018',
              'sortIndex':''} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('sortIndex', response.json)
        self.assertEqual(None, response.json['sortIndex'])
        
    def test_update_node_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        data={'name':'MainNode1new', 'type':'newType', 'description':'newDescription',
              'nodeInfo':{'new':'info'}, 'haveTried':True, 'review':'newReview',
              'rating':5} 
        response = self.client.put('/node/' + str(response.json['id']),
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(403, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('User doesn''t have edit permission', response.json['error'])
        
        
    def test_add_main_node_bad_owner_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':'foo', 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(404, response.status_code)  
        self.assertIn('error', response.json)
        self.assertIn('Owner not found. Can''t create node', response.json['error'])
    
    def test_add_main_node_bad_parent_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'parentId':'foo', 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(404, response.status_code)  
        self.assertIn('error', response.json)
        self.assertIn('Parent not found. Can''t create node', response.json['error'])        
    
    def test_add_main_node_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        data={'name':'ParentNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(403, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('User doesn''t have edit permission', response.json['error'])
        
    def test_add_main_node_bad_owner_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':'foo', 'parentId':self.rootNode.id, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(403, response.status_code)  
        self.assertIn('error', response.json)
        self.assertIn('User doesn''t have edit permission', response.json['error'])
    
    def test_add_main_node_bad_parent_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'parentId':'foo', 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(403, response.status_code)  
        self.assertIn('error', response.json)
        self.assertIn('User doesn''t have edit permission', response.json['error'])
        
    def test_add_main_node_no_name(self):
        data={'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)  
        self.assertIn('error', response.json)
        self.assertIn('No name specified in add/node request', response.json['error'])
        
    def test_add_main_node_no_type(self):
        data={'name':'MainNode1', 'owner':self.editUser.username}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)  
        self.assertIn('error', response.json)
        self.assertIn('No type specified in add/node request', response.json['error'])
        
    def test_add_main_node_no_owner(self):
        data={'name':'MainNode1', 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)  
        self.assertIn('error', response.json)
        self.assertIn('No owner specified in add/node request', response.json['error'])
        
    def test_add_main_node_null_dateTried(self):
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books', 'dateTried': None}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)  
    
    def test_add_main_node_null_dateReviewed(self):
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books', 'dateReviewed': None}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)  
        
    def test_get_main_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        response = self.client.get('/main/nodes', headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(3, response.json['nodeCount'])
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
            self.assertEqual(url_for('main.getNodeFromId',nodeId=mainNodeJson1['id'], 
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
            self.assertEqual(url_for('main.getNodeFromId',nodeId=mainNodeJson2['id'],
                                     _external=True), mainNodeJson2['uri'])
            
    def test_get_main_nodes_with_info_3_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        user = self.editUser
        mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
        leafRating = 0
        need = False
        haveTried = False
        for mainNode in mainNodes:
            need = not(need)
            haveTried = not(haveTried)
            subNodes = create_two_sub_nodes_for_parent_node(mainNode)
            for subNode in subNodes:
                for leaf in create_two_sub_nodes_for_parent_node(subNode):
                    leafRating += 1
                    leaf.rating = leafRating
                    leaf.need = need
                    leaf.haveTried = haveTried
        # we now have a three level hierarchy we can test against
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(15, response.json['nodeCount'])
        response = self.client.get('/main/nodes/info/depth/3?ownerId='+str(user.id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(3, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        mainNodeJson1 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'node:Main Node, owner:Edit_1'][0]
        mainNodeJson2 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'node:Main Node, owner:Edit_2'][0]
        self.assertIn('nodeInfo', mainNodeJson1)
        self.assertIn('numberSubs', mainNodeJson1['nodeInfo'])
        self.assertEqual(2, mainNodeJson1['nodeInfo']['numberSubs'])
        self.assertIn('averageLeafRating', mainNodeJson1['nodeInfo'])
        self.assertEqual(3, mainNodeJson1['nodeInfo']['averageLeafRating'])
        self.assertIn('needLeaves', mainNodeJson1['nodeInfo'])
        self.assertEqual(4, mainNodeJson1['nodeInfo']['needLeaves'])
        self.assertIn('numberLeaves', mainNodeJson1['nodeInfo'])
        self.assertEqual(4, mainNodeJson1['nodeInfo']['numberLeaves'])
        self.assertIn('haveTriedLeaves', mainNodeJson1['nodeInfo'])
        self.assertEqual(4, mainNodeJson1['nodeInfo']['haveTriedLeaves'])
        self.assertIn('nodeInfo', mainNodeJson2)
        self.assertIn('numberSubs', mainNodeJson2['nodeInfo'])
        self.assertEqual(2, mainNodeJson2['nodeInfo']['numberSubs'])
        self.assertIn('averageLeafRating', mainNodeJson2['nodeInfo'])
        self.assertEqual(7, mainNodeJson2['nodeInfo']['averageLeafRating'])
        self.assertIn('needLeaves', mainNodeJson2['nodeInfo'])
        self.assertEqual(0, mainNodeJson2['nodeInfo']['needLeaves'])
        self.assertIn('numberLeaves', mainNodeJson2['nodeInfo'])
        self.assertEqual(4, mainNodeJson2['nodeInfo']['numberLeaves'])
        self.assertIn('haveTriedLeaves', mainNodeJson2['nodeInfo'])
        self.assertEqual(0, mainNodeJson2['nodeInfo']['haveTriedLeaves'])
    
    
    def test_get_main_nodes_with_info_3_no_leaf_info(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        user = self.editUser
        mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
        for mainNode in mainNodes:
            for subNode in create_two_sub_nodes_for_parent_node(mainNode):
                create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy we can test against
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(15, response.json['nodeCount'])
        response = self.client.get('/main/nodes/info/depth/3?ownerId='+str(user.id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(3, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        mainNodeJson1 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'node:Main Node, owner:Edit_1'][0]
        mainNodeJson2 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'node:Main Node, owner:Edit_2'][0]
        self.assertIn('nodeInfo', mainNodeJson1)
        self.assertIn('numberSubs', mainNodeJson1['nodeInfo'])
        self.assertEqual(2, mainNodeJson1['nodeInfo']['numberSubs'])
        self.assertIn('averageLeafRating', mainNodeJson1['nodeInfo'])
        self.assertEqual(None, mainNodeJson1['nodeInfo']['averageLeafRating'])
        self.assertIn('needLeaves', mainNodeJson1['nodeInfo'])
        self.assertEqual(0, mainNodeJson1['nodeInfo']['needLeaves'])
        self.assertIn('numberLeaves', mainNodeJson1['nodeInfo'])
        self.assertEqual(4, mainNodeJson1['nodeInfo']['numberLeaves'])
        self.assertIn('haveTriedLeaves', mainNodeJson1['nodeInfo'])
        self.assertEqual(0, mainNodeJson1['nodeInfo']['haveTriedLeaves'])
        self.assertIn('nodeInfo', mainNodeJson2)
        self.assertIn('numberSubs', mainNodeJson2['nodeInfo'])
        self.assertEqual(2, mainNodeJson2['nodeInfo']['numberSubs'])
        self.assertIn('averageLeafRating', mainNodeJson2['nodeInfo'])
        self.assertEqual(None, mainNodeJson2['nodeInfo']['averageLeafRating'])
        self.assertIn('needLeaves', mainNodeJson2['nodeInfo'])
        self.assertEqual(0, mainNodeJson2['nodeInfo']['needLeaves'])
        self.assertIn('numberLeaves', mainNodeJson2['nodeInfo'])
        self.assertEqual(4, mainNodeJson2['nodeInfo']['numberLeaves'])
        self.assertIn('haveTriedLeaves', mainNodeJson2['nodeInfo'])
        self.assertEqual(0, mainNodeJson2['nodeInfo']['haveTriedLeaves'])
    
    def test_get_main_nodes_with_info_3_no_sub_info(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        user = self.editUser
        mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
        # we now have a three level hierarchy we can test against
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(3, response.json['nodeCount'])
        response = self.client.get('/main/nodes/info/depth/3?ownerId='+str(user.id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(3, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        mainNodeJson1 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'node:Main Node, owner:Edit_1'][0]
        mainNodeJson2 = [nodeJson for nodeJson in response.json['nodes'] if nodeJson['name'] == 'node:Main Node, owner:Edit_2'][0]
        self.assertIn('nodeInfo', mainNodeJson1)
        self.assertIn('numberSubs', mainNodeJson1['nodeInfo'])
        self.assertEqual(0, mainNodeJson1['nodeInfo']['numberSubs'])
        self.assertIn('averageLeafRating', mainNodeJson1['nodeInfo'])
        self.assertEqual(None, mainNodeJson1['nodeInfo']['averageLeafRating'])
        self.assertIn('needLeaves', mainNodeJson1['nodeInfo'])
        self.assertEqual(0, mainNodeJson1['nodeInfo']['needLeaves'])
        self.assertIn('numberLeaves', mainNodeJson1['nodeInfo'])
        self.assertEqual(0, mainNodeJson1['nodeInfo']['numberLeaves'])
        self.assertIn('haveTriedLeaves', mainNodeJson1['nodeInfo'])
        self.assertEqual(0, mainNodeJson1['nodeInfo']['haveTriedLeaves'])
        
    def test_get_full_tree3_from_main_node(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        user = self.editUser
        mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
        for mainNode in mainNodes:
            for subNode in create_two_sub_nodes_for_parent_node(mainNode):
                create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy we can test against
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(15, response.json['nodeCount'])
        response = self.client.get('/tree/depth/3/'+str(mainNodes[0].id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(7, response.json['nodeCount'])
    
    def test_get_full_tree3_from_sub_node(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        user = self.editUser
        mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
        for mainNode in mainNodes:
            for subNode in create_two_sub_nodes_for_parent_node(mainNode):
                create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy we can test against
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(15, response.json['nodeCount'])
        response = self.client.get('/tree/depth/3/'+str(mainNodes[0].children[0].id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(7, response.json['nodeCount'])
    
    def test_get_full_tree3_from_leaf_node(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        user = self.editUser
        mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
        for mainNode in mainNodes:
            for subNode in create_two_sub_nodes_for_parent_node(mainNode):
                create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy we can test against
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(15, response.json['nodeCount'])
        response = self.client.get('/tree/depth/3/'+str(mainNodes[0].children[0].children[0].id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(7, response.json['nodeCount'])
        
    def test_get_partial_tree3_from_main_node(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        user = self.editUser
        mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
        for mainNode in mainNodes:
            create_two_sub_nodes_for_parent_node(mainNode)
        create_two_sub_nodes_for_parent_node(mainNodes[1].children[0])
                
        # we now have a three level hierarchy we can test against
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(9, response.json['nodeCount'])
        response = self.client.get('/tree/depth/3/'+str(mainNodes[0].id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(3, response.json['nodeCount'])
            
    def test_get_partial_tree3_from_sub_node(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        user = self.editUser
        mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
        for mainNode in mainNodes:
            create_two_sub_nodes_for_parent_node(mainNode)
        create_two_sub_nodes_for_parent_node(mainNodes[1].children[0])
                
        # we now have a three level hierarchy we can test against
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(9, response.json['nodeCount'])
        response = self.client.get('/tree/depth/3/'+str(mainNodes[0].children[0].id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(3, response.json['nodeCount'])
    
    def test_get_main_nodes_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        response = self.client.get('/main/nodes', headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(3, response.json['nodeCount'])
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
            self.assertEqual(url_for('main.getNodeFromId',nodeId=mainNodeJson1['id'],
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
            self.assertEqual(url_for('main.getNodeFromId',nodeId=mainNodeJson2['id'],
                                     _external=True), mainNodeJson2['uri'])
        
    def test_get_main_nodes_filter_owner(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.adminUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        response = self.client.get('/main/nodes?ownerId=' + str(self.editUser.id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(2, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        nodeResponse = response.json['nodes'][0]
        self.assertIn('name', nodeResponse)
        self.assertEqual('MainNode1', nodeResponse['name'])
        self.assertIn('ownerName', nodeResponse)
        self.assertEqual(self.editUser.username, nodeResponse['ownerName'])
        self.assertIn('ownerId', nodeResponse)
        self.assertEqual(self.editUser.id, nodeResponse['ownerId'])
        self.assertIn('parentName',nodeResponse)
        self.assertEqual(self.rootNode.name, nodeResponse['parentName'])
        self.assertIn('parentId', nodeResponse)
        self.assertEqual(self.rootNode.id, nodeResponse['parentId'])
        self.assertIn('uri',nodeResponse)
        self.assertIn('uri',nodeResponse)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNodeFromId',nodeId=nodeResponse['id'], 
                                     _external=True), nodeResponse['uri'])
            
    def test_get_main_nodes_filter_bad_owner(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.adminUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        response = self.client.get('/main/nodes?ownerId=999', headers=authHeaders)
        self.assertEqual(404, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Invalid ownername specified in main/nodes request, so no nodes could be found', response.json['error'])
            
    def test_get_main_nodes_filter_wrong_owner(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        response = self.client.get('/main/nodes?ownerId=' + str(self.adminUser.id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(1, response.json['nodeCount'])
            
    def test_get_main_nodes_filter_type(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type':'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.editUser.username, 'type':'beer'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        response = self.client.get('/main/nodes?type=beer', headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(2, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        nodeResponse = response.json['nodes'][0]
        self.assertIn('name', nodeResponse)
        self.assertEqual('MainNode2', nodeResponse['name'])
        self.assertIn('type', nodeResponse)
        self.assertEqual('beer', nodeResponse['type'])
        self.assertIn('ownerName', nodeResponse)
        self.assertEqual(self.editUser.username, nodeResponse['ownerName'])
        self.assertIn('ownerId', nodeResponse)
        self.assertEqual(self.editUser.id, nodeResponse['ownerId'])
        self.assertIn('parentName',nodeResponse)
        self.assertEqual(self.rootNode.name, nodeResponse['parentName'])
        self.assertIn('parentId', nodeResponse)
        self.assertEqual(self.rootNode.id, nodeResponse['parentId'])
        self.assertIn('uri',nodeResponse)
        self.assertIn('uri',nodeResponse)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNodeFromId',nodeId=nodeResponse['id'], 
                                     _external=True), nodeResponse['uri'])
            
    def test_get_main_nodes_filter_wrong_type(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type':'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.editUser.username, 'type':'beer'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        response = self.client.get('/main/nodes?type=foo', headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(1, response.json['nodeCount'])
        
    def test_get_nodes_filter_owner(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.adminUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        response = self.client.get('/nodes?ownerId=' + str(self.editUser.id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(2, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        nodeResponse = response.json['nodes'][0]
        self.assertIn('name', nodeResponse)
        self.assertEqual('MainNode1', nodeResponse['name'])
        self.assertIn('ownerName', nodeResponse)
        self.assertEqual(self.editUser.username, nodeResponse['ownerName'])
        self.assertIn('ownerId', nodeResponse)
        self.assertEqual(self.editUser.id, nodeResponse['ownerId'])
        self.assertIn('parentName',nodeResponse)
        self.assertEqual(self.rootNode.name, nodeResponse['parentName'])
        self.assertIn('parentId', nodeResponse)
        self.assertEqual(self.rootNode.id, nodeResponse['parentId'])
        self.assertIn('uri',nodeResponse)
        self.assertIn('uri',nodeResponse)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNodeFromId',nodeId=nodeResponse['id'], 
                                     _external=True), nodeResponse['uri'])
            
    def test_get_nodes_filter_bad_owner(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.adminUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        response = self.client.get('/nodes?ownerId=999', headers=authHeaders)
        self.assertEqual(404, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Invalid ownername specified in nodes request, so no nodes could be found', response.json['error'])
            
    def test_get_nodes_filter_wrong_owner(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        response = self.client.get('/nodes?ownerId=' + str(self.adminUser.id), headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(1, response.json['nodeCount'])
            
    def test_get_nodes_filter_type(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type':'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.editUser.username, 'type':'beer'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        response = self.client.get('/nodes?type=beer', headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(2, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        nodeResponse = response.json['nodes'][0]
        self.assertIn('name', nodeResponse)
        self.assertEqual('MainNode2', nodeResponse['name'])
        self.assertIn('type', nodeResponse)
        self.assertEqual('beer', nodeResponse['type'])
        self.assertIn('ownerName', nodeResponse)
        self.assertEqual(self.editUser.username, nodeResponse['ownerName'])
        self.assertIn('ownerId', nodeResponse)
        self.assertEqual(self.editUser.id, nodeResponse['ownerId'])
        self.assertIn('parentName',nodeResponse)
        self.assertEqual(self.rootNode.name, nodeResponse['parentName'])
        self.assertIn('parentId', nodeResponse)
        self.assertEqual(self.rootNode.id, nodeResponse['parentId'])
        self.assertIn('uri',nodeResponse)
        self.assertIn('uri',nodeResponse)
        with current_app.app_context():
            self.assertEqual(url_for('main.getNodeFromId',nodeId=nodeResponse['id'], 
                                     _external=True), nodeResponse['uri'])
            
    def test_get_nodes_filter_wrong_type(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type':'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)
        data={'name':'MainNode2', 'owner':self.editUser.username, 'type':'beer'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code) 
        response = self.client.get('/nodes?type=foo', headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(1, response.json['nodeCount'])

    def test_create_two_equal_main_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)  
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('This node already exists', response.json['error'])
        
    def test_delete_node_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)  
        response = self.client.delete('/node/' + str(response.json['id']),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(200, response.status_code)
        self.assertIn('result', response.json)
        self.assertEqual(True, response.json['result'])
        
    def test_delete_node_read_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)  
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")
        }
        response = self.client.delete('/node/' + str(response.json['id']),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(403, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('User doesn''t have edit permission', response.json['error'])
        
    def test_delete_root_node_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        response = self.client.delete('/node/' + str(self.rootNode.id),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(403, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('Deletion of the Root node is not permitted', response.json['error'])
        
    def test_create_duplicate_root_node(self):
        data={'name':'Root', 'owner':self.adminUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(403, response.status_code)  
        self.assertIn('error', response.json)
        self.assertIn('There can be only one Root node', response.json['error'])
        
    def test_create_two_equal_sub_nodes_edit_access(self):
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Edit:test").decode("ascii")
        }
        data={'name':'MainNode1', 'owner':self.editUser.username, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        parentId = response.json['id']
        self.assertEqual(201, response.status_code)
        data={'name':'SubNode1', 'owner':self.editUser.username, 'parentId': parentId, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(201, response.status_code)  
        data={'name':'SubNode1', 'owner':self.editUser.username, 'parentId': parentId, 'type': 'books'}
        response = self.client.post('/add/node',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=authHeaders)
        self.assertEqual(400, response.status_code)
        self.assertIn('error', response.json)
        self.assertIn('This node already exists', response.json['error'])
        
    
    def test_create_two_main_nodes_each_with_two_subnodes_each_with_two_subsubnodes_for_user_edit_access(self):
        user = create_user_with_index('Test', 1)
        mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
        for mainNode in mainNodes:
            subNodes = create_two_sub_nodes_for_parent_node(mainNode)
            for subNode in subNodes:
                create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy we can test against
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(15, response.json['nodeCount'])
        response = self.client.get('/main/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(3, response.json['nodeCount'])
        
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
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(29, response.json['nodeCount'])
        
    def test_get_nodes_three_level_child_count(self):
        users = [create_user_with_index('Test', 1),
                 create_user_with_index('Test', 2)]
        for user in users:
            mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
            for mainNode in mainNodes:
                subNodes = create_two_sub_nodes_for_parent_node(mainNode)
                for subNode in subNodes:
                    create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy for two different users we can test against
        response = self.client.get('/main/nodes?ownerId=' + str(users[0].id), headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(3, response.json['nodeCount'])
        self.assertIn('nodes', response.json)
        self.assertEqual(3, len(response.json['nodes']))
        self.assertIn('childCount', response.json['nodes'][0])
        self.assertEqual(2, response.json['nodes'][0]['childCount'])
        
        
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
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(29, response.json['nodeCount'])
        response = self.client.get('/main/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(5, response.json['nodeCount'])
        
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
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(29, response.json['nodeCount'])
        mainNode = Node.query.filter(Node.owner==users[0], Node.parent==self.rootNode).first()
        response = self.client.delete('/node/' + str(mainNode.id), headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(22, response.json['nodeCount'])
        
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
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(29, response.json['nodeCount'])
        mainNode = Node.query.filter(Node.owner==users[0], Node.parent==self.rootNode).first()
        subNode = mainNode.children[0]
        response = self.client.delete('/node/' + str(subNode.id), headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(26, response.json['nodeCount'])
        
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
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(29, response.json['nodeCount'])
        authHeaders = {
            'Authorization': 'Basic %s' % b64encode(b"Admin:test").decode("ascii")
        }
        response = self.client.delete('/admin/user/' + users[0].username, headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(15, response.json['nodeCount'])
        
    def test_create_two_main_nodes_each_with_two_subnodes_each_with_two_subsubnodes_for_two_users_get_main_nodes_filter_user1(self):
        users = [create_user_with_index('Test', 1),
                 create_user_with_index('Test', 2)]
        for user in users:
            mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
            for mainNode in mainNodes:
                subNodes = create_two_sub_nodes_for_parent_node(mainNode)
                for subNode in subNodes:
                    create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy for two different users we can test against
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(29, response.json['nodeCount'])
        response = self.client.get('/main/nodes', query_string={'ownerId':users[0].id}, 
                                   headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(3, response.json['nodeCount'])
        
    def test_create_two_main_nodes_each_with_two_subnodes_each_with_two_subsubnodes_for_two_users_get_nodes_filter_user1(self):
        users = [create_user_with_index('Test', 1),
                 create_user_with_index('Test', 2)]
        for user in users:
            mainNodes = create_two_main_nodes_for_owner(user, parent=self.rootNode)
            for mainNode in mainNodes:
                subNodes = create_two_sub_nodes_for_parent_node(mainNode)
                for subNode in subNodes:
                    create_two_sub_nodes_for_parent_node(subNode)
        # we now have a three level hierarchy for two different users we can test against
        response = self.client.get('/nodes', headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(29, response.json['nodeCount'])
        response = self.client.get('/nodes', query_string={'ownerId':users[0].id}, 
                                   headers=authHeaders, 
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIn('nodeCount', response.json)
        self.assertEqual(15, response.json['nodeCount'])
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()