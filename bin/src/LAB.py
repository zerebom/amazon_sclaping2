'''
研究をオブジェクト指向で書く。
それぞれの作業はそれぞれLABクラスのメソッドとして実行される

'''

import pandas as pd
from DB import DB
from User import User
from BS4 import BS4


class LAB:
    def __init__(self):
        self.db_path='../../.data/db/'
        pass    
    
    def get_all_user_id(self,csv_name):
        db=DB('./1204user_data.db')
        db.create_table('users','id, name, book, book_star, url')
        df=pd.read_csv(csv_name,header=None)
        
        conserva=df.iloc[:,0].values
        liberal=df.iloc[:,1].values

        for con in conserva:
            users=BS4(con).get_user_data2()
            for user in users:
                db.save_user_data(user)

        for lib in liberal:
            if lib ==None:
                continue
            users=BS4(lib).get_user_data2()
            for user in users:
                db.save_user_data(user)

    def get_all_review(self,db_name):
        db=DB(db_name)
        c=db.select_data()
        
        



        



lab=LAB()

