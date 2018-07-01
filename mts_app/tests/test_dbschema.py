'''
Created on Jun 22, 2018

@author: grovesr
'''
import unittest
from mts_app.tests.drop_all_tables import drop_all_tables

from mts_app import db, create_app
from mts_app.models import *
from mts_app.config import Config
from mts_app.tests.helpers import * 
from mts_app.tests.MyThingsTest import MyThingsTest
from sqlalchemy.exc import IntegrityError

class DBSchemaTests(MyThingsTest):
 
###############
#### tests ####
###############
 
    def test_create_user(self):
        
        create_user_with_index(username='Test', userindex=1)
        testUserName = User.query.filter_by(username='Test1').first().username
        self.assertEqual(testUserName, 'Test1')
    
    def test_create_three_users(self):
        
        create_three_users()
        testUserName = User.query.filter_by(username='Test1').first().username
        self.assertEqual(testUserName, 'Test1')
        testUserName = User.query.filter_by(username='Test2').first().username
        self.assertEqual(testUserName, 'Test2')
        testUserName = User.query.filter_by(username='Test3').first().username
        self.assertEqual(testUserName, 'Test3')
        
    def test_create_two_main_nodes_for_each_of_three_owners(self):
        
        users = create_three_users()
        for user in users:
            create_two_main_nodes_for_owner(user)
        mainNodesUser1 = Node.query.filter_by(owner=users[0]).all()
        mainNodesUser2 = Node.query.filter_by(owner=users[1]).all()
        mainNodesUser3 = Node.query.filter_by(owner=users[2]).all()
        self.assertEqual(len(mainNodesUser1), 2)
        self.assertEqual(len(mainNodesUser2), 2)
        self.assertEqual(len(mainNodesUser3), 2)
        
    def test_create_two_main_nodes_for_owner_with_same_name_and_parent(self):
        
        user = create_user_with_index(username='Test', userindex=1)
        node = Node.query.filter_by(owner=self.adminUser).first()
        with self.assertRaises(IntegrityError) as cm:
            user.nodes=[Node(name='node:Main Node, user:' + user.username , parent=self.rootNode, owner=user),
                        Node(name='node:Main Node, user:' + user.username , parent=self.rootNode, owner=user)]
        the_exception = cm.exception
        self.assertIn('Duplicate entry', the_exception.args[0])
        
    def test_create_two_sub_nodes_for_owner_with_same_name_and_parent(self):
        
        user = create_user_with_index(username='Test', userindex=1)
        node = Node.query.filter_by(owner=self.adminUser).first()
        with self.assertRaises(IntegrityError) as cm:
            user.nodes=[Node(name='node:Main Node, user:' + user.username , parent=node, owner=user),
                        Node(name='node:Main Node, user:' + user.username , parent=node, owner=user)]
        the_exception = cm.exception
        self.assertIn('Duplicate entry', the_exception.args[0])
        
    def test_create_two_main_nodes_for_owner_each_with_two_subnodes(self):
        user = create_user_with_index(username='Test', userindex=1)
        db.session.add(user)
        db.session.commit()
        mainNodes = create_two_main_nodes_for_owner(user)
        for mainNode in mainNodes:
            create_two_sub_nodes_for_parent_node(mainNode)
        subNodesOfParentNode1 = Node.query.filter_by(parent=mainNodes[0]).all()
        subNodesOfParentNode2 = Node.query.filter_by(parent=mainNodes[1]).all()
        self.assertEqual(len(subNodesOfParentNode1), 2)
        self.assertEqual(len(subNodesOfParentNode2), 2)
        self.assertEqual(subNodesOfParentNode1[0].parent.name, mainNodes[0].name)
        self.assertEqual(subNodesOfParentNode1[1].parent.name, mainNodes[0].name)
        self.assertEqual(subNodesOfParentNode2[0].parent.name, mainNodes[1].name)
        self.assertEqual(subNodesOfParentNode2[1].parent.name, mainNodes[1].name)
        self.assertEqual(len(mainNodes[0].children), 2)
        self.assertEqual(len(mainNodes[1].children), 2)
        
    def test_create_two_main_nodes_for_owner_each_with_two_subnodes_each_with_two_subsubnodes(self):
        user = create_user_with_index(username='Test', userindex=1)
        db.session.add(user)
        db.session.commit()
        mainNodes = create_two_main_nodes_for_owner(user)
        for mainNode in mainNodes:
            subNodes = create_two_sub_nodes_for_parent_node(mainNode)
            for subNode in subNodes:
                subSubNodes = create_two_sub_nodes_for_parent_node(subNode)
        subNodesOfParentNode1 = Node.query.filter_by(parent=mainNodes[0]).all()
        subNodesOfParentNode2 = Node.query.filter_by(parent=mainNodes[1]).all()
        self.assertEqual(len(subNodesOfParentNode1), 2)
        self.assertEqual(len(subNodesOfParentNode2), 2)
        self.assertEqual(subNodesOfParentNode1[0].parent.name, mainNodes[0].name)
        self.assertEqual(subNodesOfParentNode1[1].parent.name, mainNodes[0].name)
        self.assertEqual(subNodesOfParentNode2[0].parent.name, mainNodes[1].name)
        self.assertEqual(subNodesOfParentNode2[1].parent.name, mainNodes[1].name)
        self.assertEqual(len(mainNodes[0].children), 2)
        self.assertEqual(len(mainNodes[1].children), 2)
        subNodesOfSubNode1OfParentNode1 = Node.query.filter_by(parent=mainNodes[0].children[0]).all()
        subNodesOfSubNode2OfParentNode1 = Node.query.filter_by(parent=mainNodes[0].children[1]).all()
        subNodesOfSubNode1OfParentNode2 = Node.query.filter_by(parent=mainNodes[1].children[0]).all()
        subNodesOfSubNode2OfParentNode2 = Node.query.filter_by(parent=mainNodes[1].children[1]).all()
        self.assertEqual(len(subNodesOfSubNode1OfParentNode1), 2)
        self.assertEqual(len(subNodesOfSubNode2OfParentNode1), 2)
        self.assertEqual(len(subNodesOfSubNode1OfParentNode2), 2)
        self.assertEqual(len(subNodesOfSubNode2OfParentNode2), 2)
        self.assertEqual(subNodesOfSubNode1OfParentNode1[0].parent.name, subNodesOfParentNode1[0].name)
        self.assertEqual(subNodesOfSubNode1OfParentNode1[1].parent.name, subNodesOfParentNode1[0].name)
        self.assertEqual(subNodesOfSubNode2OfParentNode1[0].parent.name, subNodesOfParentNode1[1].name)
        self.assertEqual(subNodesOfSubNode2OfParentNode1[1].parent.name, subNodesOfParentNode1[1].name)
        self.assertEqual(subNodesOfSubNode1OfParentNode2[0].parent.name, subNodesOfParentNode2[0].name)
        self.assertEqual(subNodesOfSubNode1OfParentNode2[1].parent.name, subNodesOfParentNode2[0].name)
        self.assertEqual(subNodesOfSubNode2OfParentNode2[0].parent.name, subNodesOfParentNode2[1].name)
        self.assertEqual(subNodesOfSubNode2OfParentNode2[1].parent.name, subNodesOfParentNode2[1].name)
        self.assertEqual(len(subNodesOfParentNode1[0].children), 2)
        self.assertEqual(len(subNodesOfParentNode1[1].children), 2)
        self.assertEqual(len(subNodesOfParentNode2[0].children), 2)
        self.assertEqual(len(subNodesOfParentNode2[1].children), 2)
        
    def test_remove_all_nodes_for_single_owner(self):
        user1 = create_user_with_index(username='Test', userindex=1)
        user2 = create_user_with_index(username='Test', userindex=2)
        db.session.add_all([user1, user2])
        db.session.commit()
        mainNodes1 = create_two_main_nodes_for_owner(user1)
        mainNodes2 = create_two_main_nodes_for_owner(user2)
        for mainNode in mainNodes1:
            create_two_sub_nodes_for_parent_node(mainNode)
        for mainNode in mainNodes2:
            create_two_sub_nodes_for_parent_node(mainNode)
        self.assertEqual(Node.query.filter_by(owner=user1).count(), 6)
        self.assertEqual(Node.query.filter_by(owner=user2).count(), 6)
        db.session.delete(user1)
        db.session.commit()
        self.assertEqual(Node.query.filter_by(owner=user1).count(), 0)
        self.assertEqual(Node.query.filter_by(owner=user2).count(), 6)
        
    def test_remove_all_nested_subnodes_for_mainnode(self):
        user = create_user_with_index(username='Test', userindex=1)
        db.session.add(user)
        db.session.commit()
        mainNodes = create_two_main_nodes_for_owner(user)
        for mainNode in mainNodes:
            subNodes = create_two_sub_nodes_for_parent_node(mainNode)
            for subNode in subNodes:
                subSubNodes = create_two_sub_nodes_for_parent_node(subNode)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[0]).count(), 2)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[1]).count(), 2)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[0].children[0]).count(), 2)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[0].children[1]).count(), 2)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[1].children[0]).count(), 2)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[1].children[1]).count(), 2)
        db.session.delete(mainNodes[0])
        db.session.commit()
        self.assertEqual(Node.query.count(), 8)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[0]).count(), 0)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[1]).count(), 2)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[0].children[0]).count(), 0)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[0].children[1]).count(), 0)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[1].children[0]).count(), 2)
        self.assertEqual(Node.query.filter_by(parent=mainNodes[1].children[1]).count(), 2)
        db.session.delete(mainNodes[1])
        db.session.commit()
        self.assertEqual(Node.query.count(), 1)

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()