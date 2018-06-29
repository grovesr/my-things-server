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
from base64 import b64encode
from flask import current_app
from flask.helpers import url_for
import json

authHeaders = {
    'Authorization': 'Basic %s' % b64encode(b"Admin:test").decode("ascii")
}
 
class AdminApiTests(unittest.TestCase):
 
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
        createTestAdminUser(username='Admin', email='admin@example.com', password="test")
        self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        db.session.close()
        drop_all_tables(db)
        pass
 
 
###############
#### tests ####
###############
    
    def test_get_user_Admin_no_auth(self):
        
        response = self.app.get(Config.API_PREFIX + '/admin/get/user/Admin')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_check_user_Admin_no_auth(self):
        
        response = self.app.get(Config.API_PREFIX + '/admin/check/user/Admin')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_get_users_no_auth(self):
        
        response = self.app.get(Config.API_PREFIX + '/admin/get/users')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_add_user_no_auth(self):
        #authHeaders['ContentType'] = 'application/json'
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.app.post(Config.API_PREFIX + '/admin/add/user',
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_delete_user_no_auth(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.app.post(Config.API_PREFIX + '/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response = self.app.delete(Config.API_PREFIX + '/admin/delete/user/Test1')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_update_user_no_auth(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.app.post(Config.API_PREFIX + '/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = {"email":"test1@example.org"}
        response = self.app.put(Config.API_PREFIX + '/admin/update/user/Test1',
                                data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)
        self.assertEqual('Unauthorized access', response.json['error'])
        
    def test_get_user_Admin(self):
        response = self.app.get(Config.API_PREFIX + '/admin/get/user/Admin', headers=authHeaders)
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
        with app.app_context():
            self.assertEqual(url_for('getUser', username='Admin', _external=True), response.json['uri'])
            
    def test_get_invalid_user(self):
        response = self.app.get(Config.API_PREFIX + '/admin/get/user/foo', headers=authHeaders)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'User not found')
    
    def test_check_user_Admin(self):
        response = self.app.get(Config.API_PREFIX + '/admin/check/user/Admin', headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Admin exists', response.json)
        self.assertEqual(response.json['Admin exists'], True)
        
    def test_check_invalid_user(self):
        response = self.app.get(Config.API_PREFIX + '/admin/check/user/foo', headers=authHeaders)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'User not found')
        
    def test_get_users(self):
        response = self.app.get(Config.API_PREFIX + '/admin/get/users', headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('userCount', response.json)
        self.assertEqual(response.json['userCount'], 1)
        self.assertIn('users', response.json)
        self.assertEqual(len(response.json['users']), 1)
        
    def test_add_user(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.app.post(Config.API_PREFIX + '/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('username', response.json)
        self.assertEqual('Test1', response.json['username'])
        self.assertIn('email', response.json)
        self.assertEqual('test1@example.com', response.json['email'])
        self.assertIn('canEdit', response.json)
        self.assertEqual(False, response.json['canEdit'])
        self.assertIn('isAdmin', response.json)
        self.assertEqual(False, response.json['isAdmin'])
        self.assertIn('uri', response.json)
        with app.app_context():
            self.assertEqual(url_for('getUser', username='Test1', _external=True), response.json['uri'])
            
    def test_add_duplicate_user(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.app.post(Config.API_PREFIX + '/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.app.post(Config.API_PREFIX + '/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'User already exists')
    
    def test_delete_user(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.app.post(Config.API_PREFIX + '/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response = self.app.delete(Config.API_PREFIX + '/admin/delete/user/Test1', headers=authHeaders)
        self.assertEqual(response.status_code, 200)
        self.assertIn('result', response.json)
        self.assertEqual(True, response.json['result'])
        
    def test_delete_invalid_user(self):
        response = self.app.delete(Config.API_PREFIX + '/admin/delete/user/foo', headers=authHeaders)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'User not found')
        
    def test_update_user(self):
        data = {"username":"Test1", "email":"test1@example.com", "password":"test"}
        response = self.app.post(Config.API_PREFIX + '/admin/add/user', headers=authHeaders,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = {"email":"test1@example.org"}
        response = self.app.put(Config.API_PREFIX + '/admin/update/user/Test1', headers=authHeaders,
                                data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.json)
        self.assertEqual('test1@example.org', response.json['email'])
        
    def test_update_invalid_user(self):
        data = {"email":"test1@example.org"}
        response = self.app.put(Config.API_PREFIX + '/admin/update/user/foo', headers=authHeaders,
                                data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'User not found')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()