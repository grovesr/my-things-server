'''
Created on Jun 19, 2018

@author: grovesr
'''
#from sqlalchemy.sql.schema import ColumnDefault

"""
hello_flask: First Python-Flask webapp
"""
import os
from mts_app import db
from mts_app import create_app
from mts_app.models import User, Node
from flask_migrate import Migrate

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
if __name__ == '__main__':
    app.run()