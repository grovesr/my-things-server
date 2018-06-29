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
from sqlalchemy.exc import IntegrityError
from flask.helpers import url_for
 
class ModelTests(unittest.TestCase):
 
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
 
    def test_create_user_password_hash(self):
        
        user = create_user_with_index(username='Test', userindex=1)
        user.set_password('foobar')
        db.session.add(user)
        db.session.commit()
        self.assertTrue(user.check_password('foobar'))
    
    def test_create_user_with_duplicate_username(self):
        
        create_user_with_index(username='Test', userindex=1)
        with self.assertRaises(IntegrityError):
            create_user_with_index(username='Test', userindex=1)
            
    def test_create_user_with_invalid_email(self):
        
        with self.assertRaises(AssertionError) as cm:
            User(username="Test1", email="foo")
        the_exception = cm.exception
        self.assertEqual('Provided email is not an email address', the_exception.args[0])
        
    def test_create_user_with_invalid_isAdmin(self):
        
        with self.assertRaises(AssertionError) as cm:
            User(username="Test1", email="test1@example.com", isAdmin=2)
        the_exception = cm.exception
        self.assertEqual('isAdmin must resolve to a Boolean type', the_exception.args[0])
        
    def test_create_user_with_invalid_canEdit(self):
        
        with self.assertRaises(AssertionError) as cm:
            User(username="Test1", email="test1@example.com", canEdit=2)
        the_exception = cm.exception
        self.assertEqual('canEdit must resolve to a Boolean type', the_exception.args[0])
        
    def test_buildJson(self):
        user = create_user_with_index(username='Test', userindex=1)
        userJson = user.buildJson()
        self.assertEqual(userJson['username'], user.username)
        self.assertEqual(userJson['id'], user.id)
        self.assertEqual(userJson['email'], user.email)
        self.assertEqual(userJson['isAdmin'], user.isAdmin)
        self.assertEqual(userJson['canEdit'], user.canEdit)
        
    def test_buildPublicJson(self):
        user = create_user_with_index(username='Test', userindex=1)
        with app.app_context():
            userJson = user.buildPublicJson()
            self.assertEqual(userJson['username'], user.username)
            self.assertEqual(userJson['email'], user.email)
            self.assertEqual(userJson['isAdmin'], user.isAdmin)
            self.assertEqual(userJson['canEdit'], user.canEdit)
            self.assertEqual(userJson['uri'], url_for('getUser', username=user.username, _external=True))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()