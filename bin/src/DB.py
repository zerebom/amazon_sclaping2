import sqlite3
import os


class DB:
    save_user_q = 'insert into users (id, name, book, book_star, url) values(?,?,?,?,?)'

    def __init__(self, db_name):
        if not os.path.exists(db_name):
            print('this file don`t exist')

        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, isolation_level=None)
        self.c = self.conn.cursor()

    def save_user_data(self, user, sql_query=save_user_q):
        '''
        型を静的にするためにこれだけクラスを使って書いた。
        正直わかりにくかった
        '''
        self.c.execute(sql_query, user)

    def db_close(self):
        self.conn.close()
    
    def simple_insert(self,table_name,datas,column,question):
        insert_sql = f'insert into {table_name} ({column}) values ({question})'
        self.c.execute(insert_sql,datas)
    
    def simple_insert_many(self,table_name,datas,column,question):
        insert_sql = f'insert into {table_name} ({column}) values ({question})'
        self.c.executemany(insert_sql,datas)

    def save_review_data(self, user_name, review_url, products_name, products_star, table_name):
        '''
        この関数をfor文で回して各ユーザーごとのレビュー一覧を取得する。
        BS4のget_product_urlで生成したリストをいい感じにDBに格納するための関数。
        受け取ったリスト同じ長さにした名前を一緒に入れる。
        review_url,products_name,products_star→もともとリスト型になっている
        name,→自分でリストにする
        '''
        user_name = [user_name]*len(products_name)
        _id = [x for x in range(1, len(review_url)+1)]

        datas = [(i, n, r, pdn, u) for i, n, r, pdn, u in zip(
            _id, user_name, products_star, products_name, review_url)]
        insert_sql = f'insert into {table_name} (id,username,star,pd_name,url) values (?,?,?,?,?)'
        self.c.executemany(insert_sql, datas)
    
    def save_text_category_data(self,_id,products_name,info_list,table_name,anti,url):
        '''
        info_listはBS4.pyのget_category2から受け取る。
        products_nameはsqlからとってくる
        正直user名なども紐づけしたかった。
        '''
        info_list.insert(0,_id)
        info_list.insert(1,products_name)
        info_list.insert(11,anti)
        info_list.insert(12,url)

        info_list=tuple(info_list)
        insert_sql = f'insert into {table_name} (id,product_name,review_title,textlen,text,category1,category2,category3,category4,category5,anti,url) values (?,?,?,?,?,?,?,?,?,?,?,?)'
        self.c.execute(insert_sql,info_list)


    def confirm_tablename(self):
        ic=self.c.execute('select * from sqlite_master')
        for i in ic:
            print(i)
    
    def add_new_column(self,table_name,column_sentence):
        self.c.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_sentence}')
    




    def select_data(self, column_sentence, table_name, where_sentence):
        '''
        テーブル名とカラム名を指定すると、情報を持ったコントローラーを返す。
        この返り値はfor文として使うことができる。
        '''
        self.c.execute(
            f'select {column_sentence} from {table_name} {where_sentence}')
        return(self.c)

    def create_table(self, table_name, column_sentence):
        '''
        ex)create table user (id,)
        '''

        create_sql = f'''create table {table_name} ({column_sentence}) '''
        # self.c.execute(create_sql)

        try:
            self.c.execute(create_sql)
        except:
            print(' the table was made already.')
