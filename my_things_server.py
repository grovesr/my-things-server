'''
Created on Jun 19, 2018

@author: grovesr
'''
#from sqlalchemy.sql.schema import ColumnDefault

"""
hello_flask: First Python-Flask webapp
"""
from mts_app.config import Config
from mts_app import db
from mts_app import app

#db.create_all()

if __name__ == '__main__':
    app.run(debug = Config.DEBUG)
    #app.run(debug = 0)