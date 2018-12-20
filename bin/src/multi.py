from multiprocessing import Pool
from DB import *
from BS4 import *
from robobrowser import RoboBrowser
import subprocess
import slackweb
slack = slackweb.Slack(url='https://hooks.slack.com/services/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')
options = Options()
options.add_argument('--headless')
global retry_num
retry_num=0

def get_category2(category_url):
    Selebrowser = webdriver.Chrome(chrome_options=options)
    
    try:
        Selebrowser.get(category_url)
        soup = BeautifulSoup(Selebrowser.page_source, 'lxml')
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
            soup
        except:
            print('no soup')

        #403エラーを回避するコード
        if soup.title.text=='警告：アダルトコンテンツ':
            Selebrowser.quit()
            return(['アダルトコンテンツ'])
        
        if soup.title.text=='警告：年齢確認':
            Selebrowser.quit()                    
            return(['年齢確認'])
        
        if soup.title.text=='Amazon.co.jp: Amazon Music Unlimited':
            Selebrowser.quit()                    
            return(['Amazon Music'])

        if soup.title.text=='Amazon CAPTCHA':
            print('403回避のため20分待ちます')
            Selebrowser.quit()
            retry_num+=1

            if retry_num<=2:
                get_category2(category_url)
            else:
                retry_num=0
                return('403error')
            time.sleep(12)
        
        elif soup.title.text=='ページが見つかりません':
            Selebrowser.quit()
            return('商品が存在しません')
        
        else:
            print(soup.title)
            print('c不明のエラー')
    
    Selebrowser.quit()
    time.sleep(3)
    return(category)

def get_reviewtext_data(url):
    options = Options()
    options.add_argument('--headless')
    Selebrowser = webdriver.Chrome(chrome_options=options)
    try:
        Selebrowser.get(url)
        soup = BeautifulSoup(Selebrowser.page_source, 'lxml')
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
    
    Selebrowser.quit()
    time.sleep(3)
    return(info_list)



def get_sclaping_datas(user_id,pd_name,rv_url,star):
    anti=0
    infolist=BS4(rv_url).get_reviewtext_data()
    infolist.insert(0,user_id)
    infolist.insert(2,pd_name)
    infolist.insert(6,anti)
    infolist.insert(7,rv_url)
    infolist=tuple(infolist)
    return(infolist)

def get_sclaping_datas2(user_id,pd_name,rv_url,star):
    anti=1
    infolist=BS4(rv_url).get_reviewtext_data()
    infolist.insert(0,user_id)
    infolist.insert(2,pd_name)
    infolist.insert(6,anti)
    infolist.insert(7,rv_url)
    infolist=tuple(infolist)
    return(infolist)

def wrapper_params(args):
    '''
    引数をまとめる関数
    '''
    return get_sclaping_datas(*args)

def wrapper_params2(args):
    '''
    引数をまとめる関数
    '''
    return get_sclaping_datas2(*args)

def sql_get_6rows(db_name):
    db_path='../../data/db/'
    Rdb=DB(db_path+db_name)
    Rc=Rdb.select_data('id,pd_name,url,star','review','where id <= 100')
    rows=[]
    for i,row in enumerate(Rc):
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
    IP_endnum=list(range(17,32))
    cmd4=fr'C:\Users\k-higuchi\Desktop\IP変更\do_admin.bat C:\Users\k-higuchi\Desktop\IP変更\nw_office1.bat {IP_endnum[ip_num]}'
    subprocess.call(cmd4,shell=True)


if __name__=='__main__':
    rows_generator=sql_get_6rows('1206supconserva_review.db')
    init_sql()
    start_time=time.time()
    count=0
    for i,rows in enumerate(rows_generator):
        if i<=38:
            continue
        print(i)
        end_time=time.time()
        p=Pool(6)
        list_rows=[list(row) for row in rows]
        infolists=p.map(wrapper_params,list_rows)
        Wdb.simple_insert_many(table_name='category',\
                               datas=infolists,\
                               column='user_id,user_name,pd_name,rv_title,rv_len,rv_text,anti,pd_url,rv_url,category1,category2,category3,category4,category5',\
                               question='?,?,?,?,?,?,?,?,?,?,?,?,?,?')
        if i%10==0:
            slack.notify(text=f"並列処理により{i*6}件のデータが集まりました")

        if end_time-start_time>600:
            start_time=time.time()
            end_time=time.time()
            count+=1
            ipnum=count%16
            print(f'ipを{ipnum+16}に変更し、1分待ちます')
            slack.notify(text=f'ipを{ipnum+17}に変更し、1分待ちます')
            change_ip(ipnum)
            time.sleep(60)
    
    rows_generator=sql_get_6rows('1206anticonserva_review.db')
    init_sql()
    start_time=time.time()
    count=0
    for i,rows in enumerate(rows_generator):
        end_time=time.time()
        p=Pool(6)
        list_rows=[list(row) for row in rows]
        infolists=p.map(wrapper_params2,list_rows)
        Wdb.simple_insert_many(table_name='category',\
                               datas=infolists,\
                               column='user_id,user_name,pd_name,rv_title,rv_len,rv_text,anti,pd_url,rv_url,category1,category2,category3,category4,category5',\
                               question='?,?,?,?,?,?,?,?,?,?,?,?,?,?')
        if i%10==0:
            slack.notify(text=f"並列処理により{i*6}件のデータが集まりました")

        if end_time-start_time>600:
            start_time=time.time()
            end_time=time.time()
            count+=1
            ipnum=count%16
            print(f'ipを{ipnum+16}に変更し、1分待ちます')
            slack.notify(text=f'ipを{ipnum+17}に変更し、1分待ちます')
            change_ip(ipnum)
            time.sleep(60)



        

'''
get_sclaping_datasですべての情報をまとめた状態でreturnする
その後if __name__内でexcutemanyで一度にSQLITEに保存する（速度維持のため）
あと時間見てIPアドレスは変更する
sleepした時の挙動とか考えないといけない（でもIP16個あるから頻繁に変えてもいいかもしれない）
'''