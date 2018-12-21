from multiprocessing import Pool
from DB import *
from robobrowser import RoboBrowser
import subprocess
import gc
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import slackweb
import time
import re
import random

'''
multiprocessingで爆速データ収集する。
ゾンビ化を防ぐためにいろいろな工夫を凝らした。
なるべくメモリをすぐ開放するようにする
サブCPUに渡すデータは小さくする
lxmlが優秀なのでエラーハンドリングが適当でも何とかなる。
'''

class WebDriverException(Exception):
    pass

slack = slackweb.Slack(url='https://hooks.slack.com/services/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')
options = Options()
options.add_argument('--headless')
global retry_num
retry_num=0

def confirm_url(url):
    Selebrowser = webdriver.Chrome(chrome_options=options)
    try:
        Selebrowser.get(url)
    except:
        return('can`t open url')
    soup = BeautifulSoup(Selebrowser.page_source, 'lxml')
    Selebrowser.quit()
    del Selebrowser
    gc.collect()
    return(soup)



def get_category2(category_url):
    soup=confirm_url(category_url)
    
    try:
        category = soup.select('.a-unordered-list')[0].text
        category = re.sub('›', '', category)
        category = re.sub('\n', '', category)
        category = category.strip()
        category = category.split()
    
        if len(category)>5:
            category=category[0:5]

    except (TimeoutError):
        print('取得できなかったので2分待ちます')
        time.sleep(1)

    except(WebDriverException):
        print('invalid URL and sleep')
        time.sleep(1)
    except:
        try:
            a=soup.title.text
        except:
            return(['nothing_soup'])
            
        #403エラーを回避するコード
        if soup.title.text=='警告：アダルトコンテンツ':
            return(['アダルトコンテンツ'])
        
        if soup.title.text=='警告：年齢確認':
            return(['年齢確認'])
        
        if soup.title.text=='Amazon.co.jp: Amazon Music Unlimited':
            return(['Amazon Music'])

        if soup.title.text=='Amazon CAPTCHA':
            print('403です')
            return(['403error'])
        
        elif soup.title.text=='ページが見つかりません':
            return(['商品が存在しません'])
        
        else:
            return(['c不明のエラー'])
    
    return(category)

def get_reviewtext_data(url):
    soup=confirm_url(url)
    try:
        review_title = soup.select('.review-title')[0].text
        text =         soup.select('.review-text')[0].text
        user_name =    soup.select('.a-profile-name')[0].text
        product_url = 'https://www.amazon.co.jp' + \
                        soup.select('.a-text-ellipsis > a')[0].get('href')
    
    except:
        user_name=review_title = text = product_url ='nodata'

    
    category = get_category2(product_url)

    info_list = []
    info_list.extend([user_name,review_title, len(text), text,product_url])
    info_list.extend(category)
    info_list.extend(['']*(10-len(info_list)))
    
    time.sleep(3)
    return(info_list)



def get_sclaping_datas(user_id,pd_name,rv_url,star,anti):
    infolist=get_reviewtext_data(rv_url)
    infolist.insert(0,user_id)
    infolist.insert(2,pd_name)
    infolist.insert(6,anti)
    infolist.insert(7,rv_url)
    infolist=tuple(infolist)
    gc.collect()
    return(infolist)

def wrapper_params(args):
    '''
    引数をまとめる関数
    '''
    return get_sclaping_datas(*args)

def sql_get_6rows(db_name,anti):
    db_path='../../data/db/'
    Rdb=DB(db_path+db_name)
    Rc=Rdb.select_data('id,pd_name,url,star','review','where id <= 100')
    rows=[]
    for i,row in enumerate(Rc):
        row=list(row)
        row.append(anti)
        row=tuple(row)
        rows.append(row)
        if i!=0 and i%6==0:
            yield rows
            rows=[]


def init_sql():
    db_path='../../data/db/'
    global Wdb
    Wdb=DB(db_path+'1220conserva_category.db')
    Wdb.create_table('category','user_id,user_name,pd_name,rv_title,rv_len,rv_text,anti,pd_url,rv_url,category1,category2,category3,category4,category5')


def change_ip(ip_num):
    cmd4=fr'C:\Users\k-higuchi\Desktop\IP変更\do_admin.bat C:\Users\k-higuchi\Desktop\IP変更\nw_office1.bat {ip_num}'
    subprocess.call(cmd4,shell=True)

def wrapper_sclaping(rows,count,start_time):
    p=Pool(6)
    list_rows=[list(row) for row in rows]
    infolists=p.map(wrapper_params,list_rows)
    #multiprocessingのゾンビ化を防ぐ↓
    p.terminate()
    Wdb.simple_insert_many(table_name='category',\
                            datas=infolists,\
                            column='user_id,user_name,pd_name,rv_title,rv_len,rv_text,anti,pd_url,rv_url,category1,category2,category3,category4,category5',\
                            question='?,?,?,?,?,?,?,?,?,?,?,?,?,?')
    if i%10==0:
        slack.notify(text=f"並列処理により{i*6}件のデータが集まりました")

    if i%50==0:
        ip_num=random.randrange(17, 32)
        print(f'ipを{ip_num}に変更し、1分待ちます')
        slack.notify(text=f'ipを{ip_num}に変更し、30秒待ちます')
        change_ip(ip_num)
        time.sleep(30)


if __name__=='__main__':
    rows_generator=sql_get_6rows('1206supconserva_review.db',0)
    init_sql()
    start_time=time.time()
    count=0
    for i,rows in enumerate(rows_generator):
        if i<=260:
            continue
        print(i)
        print(rows)
        wrapper_sclaping(rows,count,start_time)
        
    
    rows_generator=sql_get_6rows('1206anticonserva_review.db',1)
    start_time=time.time()
    count=0
    for i,rows in enumerate(rows_generator):
        if i<=0:
            continue
        print(i)
        wrapper_sclaping(rows,count,start_time)


        

'''
get_sclaping_datasですべての情報をまとめた状態でreturnする
その後if __name__内でexcutemanyで一度にSQLITEに保存する（速度維持のため）
あと時間見てIPアドレスは変更する
sleepした時の挙動とか考えないといけない（でもIP16個あるから頻繁に変えてもいいかもしれない）
'''