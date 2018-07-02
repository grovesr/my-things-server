'''
Created on Jun 22, 2018

@author: grovesr
'''
import unittest
from mts_app.tests.drop_all_tables import drop_all_tables

from mts_app import create_app
from flask import current_app
from mts_app.models import User, Node, db
from mts_app.tests.helpers import *
from mts_app.tests.MyThingsTest import MyThingsTest
from sqlalchemy.exc import IntegrityError
from flask.helpers import url_for
 
class ModelTests(MyThingsTest):
 
 
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
        userJson = user.buildPublicJson()
        self.assertEqual(userJson['username'], user.username)
        self.assertEqual(userJson['email'], user.email)
        self.assertEqual(userJson['isAdmin'], user.isAdmin)
        self.assertEqual(userJson['canEdit'], user.canEdit)
        self.assertEqual(userJson['uri'], url_for('admin.getUser', username=user.username, _external=True))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()