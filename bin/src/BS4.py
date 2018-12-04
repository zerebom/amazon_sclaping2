import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
from User import User

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
    def __init__(self,url):
        self.url=url
        pass
    
    def get_html(self):
        browser.get(self.url)
        time.sleep(0.3) 
        soup = BeautifulSoup(browser.page_source, 'lxml')
        return soup
    
    def get_user_data(self):
        soup=self.get_html()
        review_area=soup.select('#cm_cr-review_list')[0]
        each_reviews=review_area.select('.a-section.review')
        for j,review in enumerate(each_reviews):
            _id=j
            if len(review.select('.a-profile-name'))==0:
                continue
            book=soup.select('.product-title')[0].text
            rate=review.select('.a-icon-alt')[0].text
            book_star=float(re.sub('5つ星のうち','',rate))
            name=review.select('.a-profile')[0].text
            url=review.select('.a-profile')[0].get('href')
            user=User(_id,name,book,book_star,url)
            return(user)
    

    def get_review_data(self):
        pass

        


        