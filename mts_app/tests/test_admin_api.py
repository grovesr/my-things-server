'''
Created on Jun 22, 2018

@author: grovesr
'''
import unittest
from mts_app.tests.drop_all_tables import drop_all_tables
from mts_app import  create_app
from mts_app.models import User, Node, db
from mts_app.config import Config 
from mts_app.tests.helpers import *
from mts_app.tests.MyThingsTest import MyThingsTest
from base64 import b64encode
from flask import current_app
from flask.helpers import url_for
import json

authHeaders = {
    'Authorization': 'Basic %s' % b64encode(b"Admin:test").decode("ascii")
}
 
class AdminApiTests(MyThingsTest):
 
 
###############
#### tests ####
###############
    
    def test_get_user_no_auth(self):
        
        response = self.client.get('/admin/user/' + self.adminUser.username)
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_get_user_bad_login_creds(self):
        authHeaders = {'Authorization': 'Basic %s' % b64encode(b"foo:bar").decode("ascii")}
        response = self.client.get('/admin/user/' + self.adminUser.username)
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_get_users_no_auth(self):
        
        response = self.client.get('/admin/users')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_add_user_no_auth(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.client.post('/admin/add/user',
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_delete_user_no_auth(self):
        response = self.client.delete('/admin/user/' + self.readonlyUser.username)
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_update_user_no_auth(self):
        data = {"email":"test1@example.org"}
        response = self.client.put('/admin/user/' + self.readonlyUser.username,
                                data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_get_user(self):
        response = self.client.get('/admin/user/' + self.adminUser.username, headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.json)
        self.assertEqual('Admin', response.json['username'])
        self.assertIn('email', response.json)
        self.assertEqual('admin@example.com', response.json['email'])
        self.assertIn('canEdit', response.json)
        self.assertEqual(True, response.json['canEdit'])
        self.assertIn('isAdmin', response.json)
        self.assertEqual(True, response.json['isAdmin'])
        self.assertIn('uri', response.json)
        with current_app.app_context():
            self.assertEqual(url_for('admin.getUser', username=self.adminUser.username, _external=True), response.json['uri'])
     
    def test_get_user_readonlyuser_auth(self):
        authHeaders = {'Authorization': 'Basic %s' % b64encode(b"Readonly:test").decode("ascii")}
        response = self.client.get('/admin/user/' + self.readonlyUser.username, headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.json)
        self.assertEqual('Readonly', response.json['username'])
        self.assertIn('email', response.json)
        self.assertEqual('readonly@example.com', response.json['email'])
        self.assertIn('canEdit', response.json)
        self.assertEqual(False, response.json['canEdit'])
        self.assertIn('isAdmin', response.json)
        self.assertEqual(False, response.json['isAdmin'])
        self.assertIn('uri', response.json)
        with current_app.app_context():
            self.assertEqual(url_for('admin.getUser', username=self.readonlyUser.username, _external=True), response.json['uri'])
        
            
    def test_get_user_bad_method_post(self):
        response = self.client.post('/admin/user/' + self.adminUser.username, headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
        
    def test_check_user_bad_method_post(self):
        response = self.client.post('/admin/check/user/' + self.adminUser.username, headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_check_user_bad_method_put(self):
        response = self.client.put('/admin/check/user/' + self.adminUser.username, headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_check_user_bad_method_delete(self):
        response = self.client.delete('/admin/check/user/' + self.adminUser.username, headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_get_users_bad_method_post(self):
        response = self.client.post('/admin/users', headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_get_users_bad_method_put(self):
        response = self.client.put('/admin/users', headers=authHeaders)
        self.assertEqual(response.status_code, 405)
        
    def test_get_users_bad_method_delete(self):
        response = self.client.delete('/admin/users', headers=authHeaders)
        self.assertEqual(response.status_code, 405)
            
    def test_add_user_bad_method_get(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.client.get('/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 405)
        
    def test_add_user_bad_method_put(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.client.put('/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 405)
        
    def test_add_user_bad_method_delete(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.client.delete('/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 405)
        
    def test_delete_user_bad_method_post(self):
        response = self.client.post('/admin/user/' + self.readonlyUser.username, headers=authHeaders)
        self.assertEqual(response.status_code, 405)
            
    def test_get_invalid_user(self):
        response = self.client.get('/admin/user/foo', headers=authHeaders)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'User not found')
    
    def test_check_user(self):
        response = self.client.get('/admin/check/user/' + self.adminUser.username)
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json)
        self.assertEqual(self.adminUser.id, response.json['id'])
        
    def test_check_invalid_user(self):
        response = self.client.get('/admin/check/user/foo', headers=authHeaders)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'User not found')
        
    def test_get_users(self):
        response = self.client.get('/admin/users', headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('userCount', response.json)
        self.assertEqual(response.json['userCount'], 3)
        self.assertIn('users', response.json)
        self.assertEqual(len(response.json['users']), 3)
        
    def test_add_user(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.client.post('/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        user = User.query.filter_by(username='Test1').first()
        self.assertIn('username', response.json)
        self.assertEqual('Test1', response.json['username'])
        self.assertIn('email', response.json)
        self.assertEqual('test1@example.com', response.json['email'])
        self.assertIn('canEdit', response.json)
        self.assertEqual(False, response.json['canEdit'])
        self.assertIn('isAdmin', response.json)
        self.assertEqual(False, response.json['isAdmin'])
        self.assertIn('uri', response.json)
        with current_app.app_context():
            self.assertEqual(url_for('admin.getUser', username=user.username, _external=True), response.json['uri'])
            
    def test_add_user_bad_email(self):
        data = {"username":"Test1", "email":"foo", "password":"test"}
        response = self.client.post('/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertIn('bad email format', response.json['error'])                 
            
    def test_add_duplicate_user(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.client.post('/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.client.post('/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'User already exists')
    
    def test_delete_user(self):
        response = self.client.delete('/admin/user/' + self.readonlyUser.username, headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('result', response.json)
        self.assertEqual(True, response.json['result'])
        
    def test_delete_invalid_user(self):
        response = self.client.delete('/admin/user/foo', headers=authHeaders)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'User not found')
        
    def test_update_user(self):
        data = {"email":"test1@example.org"}
        response = self.client.put('/admin/user/' + self.readonlyUser.username, headers=authHeaders,
                                data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.json)
        self.assertEqual('test1@example.org', response.json['email'])
        
    def test_update_invalid_user(self):
        data = {"email":"test1@example.org"}
        response = self.client.put('/admin/user/foo', headers=authHeaders,
                                data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'User not found')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()