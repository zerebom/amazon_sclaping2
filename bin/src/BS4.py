from robobrowser import RoboBrowser
import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
from User import User
import re
re._pattern_type = re.Pattern

class WebDriverException(Exception):
    pass

options = Options()
options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=options)


class BS4:
    '''
    BS4の操作をクラス管理する。
    基本的に
        入力:URL
        出力:ほしいデータをクラスとして返す。
    '''

    def __init__(self, url):
        self.url = url
        self.Robobrowser = RoboBrowser(
            parser='lxml',  # Beautiful Soupで使用するパーサーを指定する。
            # Cookieが使用できないと表示されてログインできない問題を回避するため、
            # 通常のブラウザーのUser-Agent（ここではFirefoxのもの）を使う。
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:45.0) Gecko/20100101 Firefox/45.0')
        options = Options()
        options.add_argument('--headless')
        self.Selebrowser = webdriver.Chrome(chrome_options=options)

        pass

    def get_html(self):
        browser.get(self.url)
        time.sleep(0.3)
        soup = BeautifulSoup(browser.page_source, 'lxml')
        return soup

    def get_user_data(self):
        '''
        I:url
        O:tuple
        robobrowser前提のコードになっています
        '''
        self.Robobrowser.open(self.url)
        j = 0
        while True:

            for i, review in enumerate(self.Robobrowser.select('.a-section .review')):
                book =      self.Robobrowser.select('.product-title')[0].text
                book_star = review.select('.a-icon-alt')[0].text
                book_star = float(re.sub('5つ星のうち', '', book_star))
                name =      review.select('.a-profile-name')[0].text
                url =       review.select('.a-profile')[0].get('href')
                user = User(j+i, name, book, book_star, url)
                yield(user.to_tuple())
                link_to_next = self.Robobrowser.get_link('次へ')

            try:
                self.Robobrowser.follow_link(link_to_next)  # 「次へ」というリンクをたどる。

            except:
                print('end')
                break
            j += 10


    def get_reviewtext_nocategory(self):
        '''
        category_dataを収集しないget_reviewtext_data関数
        usernameも取得するようにした
        ''' 
        for i in range(4):
            print('r'+str(i), end=' ')

            if i == 2:
                    user_name=review_title = text = product_url ='nodata'
                    print('nodata',end='|')
                    self.Selebrowser.quit()
                    break
            try:
                if self.Selebrowser!=None:
                    self.Selebrowser.quit()


                self.Selebrowser.get(self.url)
                soup = BeautifulSoup(self.Selebrowser.page_source, 'lxml')

                review_title = soup.select('.review-title')[0].text
                user_name = soup.select('.a-profile-name')[0].text

                text =         soup.select('.review-text')[0].text
                product_url = 'https://www.amazon.co.jp' + \
                               soup.select('.a-text-ellipsis > a')[0].get('href')

            except TimeoutError:
                print('取得できなかったので2分待ちます')
                time.sleep(120)
                self.Selebrowser.quit()
                continue
            
            except(WebDriverException):
                print('invalid URL and sleep')
                time.sleep(12)
                self.Selebrowser.quit()
                continue

            except:
                 #403エラーを回避するコード
                if soup.title.text=='Amazon CAPTCHA':
                    print('403',end='')
                    time.sleep(1)
           
                else:
                    print(soup.title)
                    print('r不明のエラー')
                self.Selebrowser.quit()
                continue

            break
        

        info_list = []
        info_list.extend([user_name,review_title, len(text), text,product_url])
        self.Selebrowser.quit()

        return(info_list)



    def get_reviewtext_data(self):
        '''
        レビューの本文とカテゴリーをURLを移動したのちに取得する
        '''
        for i in range(4):
            print('r'+str(i), end=' ')

            if i == 2:
                    user_name=review_title = text = product_url ='nodata'
                    print('nodata',end='|')
                    self.Selebrowser.quit()
                    break
            try:
                self.Selebrowser.get(self.url)
                soup = BeautifulSoup(self.Selebrowser.page_source, 'lxml')

                review_title = soup.select('.review-title')[0].text
                text =         soup.select('.review-text')[0].text
                user_name =    soup.select('.a-profile-name')[0].text
                product_url = 'https://www.amazon.co.jp' + \
                               soup.select('.a-text-ellipsis > a')[0].get('href')

            except TimeoutError:
                print('取得できなかったので2分待ちます')
                time.sleep(1)
                self.Selebrowser.quit()
                continue
            
            except(WebDriverException):
                print('invalid URL and sleep')
                time.sleep(1)
                self.Selebrowser.quit()
                continue

            except:
                try:
                    soup
                except:
                    print('no soup')
                    self.Selebrowser.quit()                
                    continue
                
                #403エラーを回避するコード
                if soup.title.text=='Amazon CAPTCHA':
                    print('403',end='')
                    time.sleep(1)
           
                else:
                    print(soup.title)
                    print('r不明のエラー')
                self.Selebrowser.quit()                
                continue

            break
        
        category = self.get_category2(product_url)

        info_list = []
        info_list.extend([user_name,review_title, len(text), text,product_url])
        info_list.extend(category)
        info_list.extend(['']*(10-len(info_list)))
        #たくさんカテゴリがあった時に5までにするように設定する
        info_list=info_list[0:10]
        self.Selebrowser.quit()
        time.sleep(3)
        return(info_list)

    def get_category2(self, category_url):
        for i in range(4):
            print('c'+str(i), end=' ')

            if i == 2:
                print('No')
                self.Selebrowser.quit()
                return('no_category')
            try:
                self.Selebrowser.get(category_url)
                soup = BeautifulSoup(self.Selebrowser.page_source, 'lxml')
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
                continue

            except(WebDriverException):
                print('invalid URL and sleep')
                time.sleep(1)
                continue


            except:
                try:
                    soup
                except:
                    print('no soup')
                    continue

                #403エラーを回避するコード
                if soup.title.text=='警告：アダルトコンテンツ':
                    self.Selebrowser.quit()
                    return(['アダルトコンテンツ'])
                
                if soup.title.text=='警告：年齢確認':
                    self.Selebrowser.quit()                    
                    return(['年齢確認'])
                
                if soup.title.text=='Amazon.co.jp: Amazon Music Unlimited':
                    self.Selebrowser.quit()                    
                    return(['Amazon Music'])

                if soup.title.text=='Amazon CAPTCHA':
                    print('403回避のため20分待ちます')
                    self.Selebrowser.quit()
                    time.sleep(12)
                
                elif soup.title.text=='ページが見つかりません':
                    self.Selebrowser.quit()
                    print('商品が存在しません')
                
                else:
                    print(soup.title)
                    print('c不明のエラー')
                self.Selebrowser.quit()
                
                continue
            break
        
        
        self.Selebrowser.quit()
        time.sleep(3)
        return(category)

    def get_product_url(self, max_url):
        self.Selebrowser.get(self.url)

        '''
        URLを取得してHTMLを取得する部分
        seleniumを使う
        listでURLと名前を返す
        スクロールして、変更があれば取得する。5回連続変更がなければ終了する
        '''
        '''-------------------------------------------------------------------'''
        lenurl = 0
        break_power = 0

        def igonre_none_product(x):
            try:
                return x.select('.profile-at-product-title-container > span')[0].text
            except:
                return('no_product')

        def igonre_none_star(x):
            try:
                return re.sub('星5つのうち', '', x.select('.profile-at-review-stars > span')[0].text)
            except:
                return('no_star')
        '''-------------------------------------------------------------------'''

        soup = BeautifulSoup(self.Selebrowser.page_source, "lxml")
        try:
            review_number = soup.select(
                '.dashboard-desktop-stat-value')[1].text
        except:
            review_number = 999999
        print(f'レビューの数は{review_number}。')

        while lenurl <= max_url:
            self.Selebrowser.execute_script(
                'scroll(0, document.body.scrollHeight)')
            soup = BeautifulSoup(self.Selebrowser.page_source, "lxml")
            review_box = soup.select('.profile-at-card')
            review_url = ['https://www.amazon.co.jp' +
                          x.select('.profile-at-review-link')[0].get('href') for x in review_box]
            products_name = [igonre_none_product(x) for x in review_box]
            products_star = [igonre_none_star(x) for x in review_box]
            lenurl2 = len(review_url)

            if lenurl+10 == lenurl2:
                break_power = 0

            if lenurl == lenurl2:
                break_power += 1

            lenurl = lenurl2

            if break_power >= 5:
                print('Break!')
                return(review_url, products_name, products_star)

            print(len(review_url), end='|')

        return(review_url, products_name, products_star)
