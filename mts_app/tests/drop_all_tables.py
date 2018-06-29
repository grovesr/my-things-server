'''
Created on Jun 22, 2018

@author: https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/DropEverything
'''
from sqlalchemy.engine import reflection
#from sqlalchemy import create_engine
from sqlalchemy.schema import (
    MetaData,
    Table,
    DropTable,
    ForeignKeyConstraint,
    DropConstraint,
    )
def drop_all_tables(db):
    engine = db.engine
    #engine = create_engine('mssql+pyodbc://scott:tiger@ms_2005/', echo=True)
    
    conn = engine.connect()
    
    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()
    
    inspector = reflection.Inspector.from_engine(engine)
    
    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in 
    # a transaction.
    
    metadata = MetaData()
    
    tbs = []
    all_fks = []
    
    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(
                ForeignKeyConstraint((),(),name=fk['name'])
                )
        t = Table(table_name,metadata,*fks)
        tbs.append(t)
        all_fks.extend(fks)
    
    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))
    
    for table in tbs:
        conn.execute(DropTable(table))
    
    trans.commit()