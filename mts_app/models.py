'''
Created on Jun 20, 2018

@author: grovesr
'''
import re
import json
from flask.helpers import url_for
#from mts_app import db
from sqlalchemy.orm import backref
from sqlalchemy.orm import validates
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.mysql import JSON
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql.functions import coalesce
from flask_sqlalchemy import SQLAlchemy
from dateutil.parser import parse
import datetime

db = SQLAlchemy()


class Node(db.Model):
    id =            db.Column(db.Integer,     primary_key=True, nullable=False)
    name =          db.Column(db.String(128), unique=False, nullable=False)
    type =          db.Column(db.String(16),  unique=False, nullable=True)
    description =   db.Column(db.Text,        unique=False, nullable=True)
    nodeInfo =      db.Column(JSON,           unique=False, nullable=True)
    haveTried =     db.Column(db.Boolean,     unique=False, nullable=True, default=False)
    dateTried =     db.Column(db.Date,        unique=False, nullable=True)
    review =        db.Column(db.Text,        unique=False, nullable=True)
    rating =        db.Column(db.Integer,     unique=False, nullable=True)
    dateReviewed =  db.Column(db.Date,        unique=False, nullable=True)
    ownerId =       db.Column(db.Integer, db.ForeignKey('user.id'), unique=False, nullable=False)
    parentId =      db.Column(db.Integer, db.ForeignKey('node.id'), unique=False, nullable=True)
    owner =         db.relationship('User', lazy=True)
    children =      db.relationship('Node', backref=backref('parent', remote_side=[id]),
                                    single_parent=True, lazy=True, cascade="all, delete, delete-orphan")
    __table_args__ = (UniqueConstraint('name', 'ownerId', 'parentId'),)
    
    def __init__(self, **kwargs):
        super(Node, self).__init__(**kwargs)
        # do custom stuff

    def __repr__(self):
        return '<Node %r>' % self.name
    
    @validates('name')
    def validate_name(self, key, name):
        if len(name) > 128 or len(name) == 0:
            raise AssertionError('Provided name is either empty or > 128 characters long')    
        return name
    
    @validates('type')
    def validate_type(self, key, type):
        if len(type) > 16 or len(type) == 0:
            raise AssertionError('Provided type is either empty or > 16 characters long')    
        return type
    
    @validates('description')
    def validate_description(self, key, description):
        if not isinstance(description, str):
            raise AssertionError('Provided description is not a string')    
        return description
    
    @validates('nodeInfo')
    def validate_nodeInfo(self, key, nodeInfo):
        if not isinstance(nodeInfo, dict):
            raise AssertionError('Provided nodeInfo is not a json serializable dictionary')    
        return nodeInfo
    
    @validates('haveTried')
    def validate_have_tried(self, key, haveTried):
        try:
            if haveTried != False and haveTried != True:
                raise AssertionError('haveTired must resolve to a Boolean type')
        except:
            raise AssertionError('haveTried must resolve to a Boolean type')
        return haveTried
    
    @validates('dateTried')
    def validate_dateTried(self, key, dateTried):
        if not isinstance(dateTried, datetime.date):
            raise AssertionError('Provided dateTried is not a valid date format')    
        return dateTried
    
    @validates('review')
    def validate_review(self, key, review):
        if not isinstance(review, str):
            raise AssertionError('Provided review is not a string')    
        return review
    
    @validates('dateReviewed')
    def validate_dateReviewed(self, key, dateReviewed):
        if not isinstance(dateReviewed, datetime.date):
            raise AssertionError('Provided dateTried is not a valid date format')    
        return dateReviewed
    
    @validates('rating')
    def validate_rating(self, key, rating):
        if not isinstance(rating, int) or rating < 0 or rating > 10:
            raise AssertionError('Provided rating must be a number between 0 and 10')    
        return rating
    
    @classmethod
    def validSearchFields(self):
        return ['id',
                'name',
                'type',
                'description',
                'haveTried',
                'dateTried',
                'review',
                'dateReviewed',
                'rating',
                'ownerId',
                'parentId']
    
    @classmethod
    def validOrderByFields(self):
        return ['name',
                'type',
                'rating']
    
    def buildJson(self):
        if self.parent is None:
            parentId = ''
        else:
            parentId = self.parent.id
        if self.dateTried is None:
            dateTried = 'None'
        else:
            dateTried = self.dateTried.strftime('%Y/%m/%d')
        if self.dateReviewed is None:
            dateReviewed = 'None'
        else:
            dateReviewed = self.dateReviewed.strftime('%Y/%m/%d')
        if self.parent:
            parent = self.parent.name
        else:
            parent = 'None'
        if not self.childCount:
            self.childCount = 0;
        return {'name': self.name,
                'id': self.id, 
                'type': self.type,
                'description': self.description, 
                'nodeInfo': json.dumps(self.nodeInfo),
                'haveTried':self.haveTried, 
                'dateTried':dateTried,
                'rating':self.rating,
                'review':self.review, 
                'dateReviewed':dateReviewed,
                'ownerName': self.owner.username,
                'ownerId': self.owner.id,
                'parentName': parent,
                'parentId': parentId,
                'childCount': self.childCount}
    
    def buildPublicJson(self):
        publicJson = self.buildJson()
        publicJson['uri'] = url_for('main.getNodeFromId', nodeId=self.id, _external=True)
        return publicJson

class User(db.Model):
    id =            db.Column(db.Integer, primary_key=True)
    username =      db.Column(db.String(64),  index=True, unique=True, nullable=False)
    email =         db.Column(db.String(120),             unique=False, nullable=False)
    password_hash = db.Column(db.String(128),             unique=False, nullable=False)
    canEdit =       db.Column(db.Boolean,                 unique=False, nullable=False, default=False)
    isAdmin =       db.Column(db.Boolean,                 unique=False, nullable=False, default=False)
    nodes =    db.relationship('Node', single_parent=True, lazy=True, 
                                    cascade="all, delete, delete-orphan")
    
    @validates('email')
    def validate_email(self, key, email):
        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            raise AssertionError('Provided email is not an email address')    
        return email
    
    @validates('canEdit')
    def validate_can_edit(self, key, canEdit):
        try:
            if canEdit != False and canEdit != True:
                raise AssertionError('canEdit must resolve to a Boolean type')
        except:
            raise AssertionError('canEdit must resolve to a Boolean type')
        return canEdit
    
    @validates('isAdmin')
    def validate_is_admin(self, key, isAdmin):
        try:
            if isAdmin != False and isAdmin != True:
                raise AssertionError('isAdmin must resolve to a Boolean type')
        except:
            raise AssertionError('isAdmin must resolve to a Boolean type')
        return isAdmin
    
    def __repr__(self):
        return '<User %r>' % self.username    
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def buildJson(self):
        return {'username': self.username,
                'id': self.id, 
                'email': self.email, 
                'isAdmin':self.isAdmin, 
                'canEdit':self.canEdit}
    
    def buildPublicJson(self):
        publicJson = self.buildJson()
        publicJson['uri'] = url_for('admin.getUser', username=self.username, _external=True)
        return publicJson