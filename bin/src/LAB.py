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
        pass    
    
    def get_all_user_id(self,csv_name):
        db=DB('./1204user_data.db')
        df=pd.read_csv(csv_name)
        
        conserva=df[0,1].values
        liberal=df[1,:].values
        for con in conserva:
            user=BS4(con).get_user_data()
            db.save_user_data(user)

        for lib in liberal:
            user=BS4(lib).get_user_data()
            db.save_user_data(user)



            


    pass






lab=LAB()