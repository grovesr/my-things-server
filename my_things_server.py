'''
Created on Jun 19, 2018

@author: grovesr
'''
#from sqlalchemy.sql.schema import ColumnDefault

"""
hello_flask: First Python-Flask webapp
"""
import os
#from mts_app import db
from mts_app import create_app, migrate
from mts_app import models
from mts_app.helpers import checkDatabasePrerequisites
from sqlalchemy.exc import OperationalError

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
if not app.config['TESTING']:
    try:
        with app.app_context():
            checkDatabasePrerequisites()
    except OperationalError:
        # we assume that flask migrate/upgrade needs to e run first
        pass
if __name__ == '__main__':
    app.run()
