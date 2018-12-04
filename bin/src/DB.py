import sqlite3

class DB:
    def __init__(self,db_name):
        self.db_name=db_name
        self.conn=sqlite3.connect(db_name,isolation_level=None)       
        self.c=db_name.cursor()
    
    def save_user_data(self,user,sql_query):
        sql_query=''
        self.c.execute(self.db_name,user)
        


