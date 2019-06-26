import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from logging import getLogger
from urllib.parse import quote
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from scrapy import Selector
from urllib import request
import time
from selenium.webdriver.common.action_chains import ActionChains
from pyquery import PyQuery as pq
import re
import datetime
import random
from fake_useragent import UserAgent


ua = UserAgent()
usr_gent = ''

from pyvirtualdisplay import Display
display = Display(visible=0, size=(1024, 768))
display.start()
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-gpu')


def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

base_url = 'http://xueshu.baidu.com/usercenter/paper/show?paperid=%s'
mongo_url = "mongodb://localhost:27017"
start_url = 'http://xueshu.baidu.com/usercenter/data/authorchannel?cmd=inject_page&author=%s&affiliate='
authors = []
iter = 0
name_index = 0
try_num = 0

# client = pymongo.MongoClient(mongo_url)
# db = client['author']
# collection = db['authors']
# with open('authors.txt','w') as file:
#     for author in collection.find():
#         file.write(author['name']+'\n')
# client.close()

with open('authors.txt','r') as file:
    author_name = file.readline().strip()
    while author_name:
        name_index = 0
        if iter % 100 == 0:
            print(datetime.datetime.today())
            print('iter:  %d' % iter)
            # 还要修改浏览器的usr-gent
        browser = webdriver.Chrome(options=chrome_options)
        try:
            browser.get(start_url % author_name)
            WebDriverWait(browser,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'.tipWords')))
            personName = browser.find_elements_by_css_selector('.personName')
            # for Name in personName:
            sel = Selector(text=browser.page_source)
            next_arrorw = ['a']
            while(next_arrorw!=[]):
                time.sleep(2)
                personName = browser.find_elements_by_css_selector('.personName')
                while name_index < len(personName):
                    time.sleep(0.2)
                    try:
                        name = personName[name_index]
                        name.click()
                        handles = browser.window_handles
                        browser.switch_to_window(handles[1])
                        WebDriverWait(browser,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'.p_name')))
                        author = {}
                        html = browser.page_source
                        select = Selector(text=html)
                        author['organ'] = select.css('.p_affiliate::text').extract_first()
                        author['quote_num'] = select.css('.p_ach_num::text').extract_first()
                        author['works_num'] = select.css('.p_ach_num::text')[1:].extract_first()
                        author['areas'] = []
                        areas = select.css('span[class="person_domain person_text"] a')
                        for area in areas:
                            author['areas'].append(area.css('a::text').extract_first())
                        author['works_type'] = []
                        types = select.css('.pie_map_wrapper .pieText .number')
                        for type in types:
                            author['works_type'].append(type.css('p::text').extract_first())
                        author['works_type'].append(select.css('.pieMapTotal .number::text').extract_first())
                        author['scholarID'] = re.findall('.*?scholarID/(.*)',browser.current_url)[0]
                        authors.append(author)
                        name_index += 1
                        browser.close()
                        handles = browser.window_handles
                        browser.switch_to_window(handles[0])
                        print(author)
                    except:
                        try_num += 1
                        if try_num > 3:
                            try_num = 0
                            name_index += 1
                if(len(authors)>15):
                    break
                arrow = browser.find_element_by_css_selector('a[class="c-icon-page-next-hover res-page-next pagenumber"]')
                ActionChains(browser).move_to_element(arrow).click().perform()
                WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.searchSubhead')))
                sel = Selector(text=browser.page_source)
                next_arrorw = sel.css('a[class="c-icon-page-next-hover res-page-next pagenumber"]')
                name_index = 0
            browser.quit()
        except:
            browser.quit()

        client = pymongo.MongoClient(mongo_url)
        db = client['author']
        for author in authors:
            db['authors'].insert_one(author)
        client.close()
        iter += len(authors)
        authors = []

        new_gent = ua.chrome
        while new_gent == usr_gent:
            new_gent = ua.chrome
        usr_gent = new_gent
        chrome_options.add_argument('user-agent="%s"' % usr_gent)

        author_name = file.readline().strip()
        # author_name = None
        time.sleep(120)

display.stop()