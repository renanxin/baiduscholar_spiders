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
import time
from scrapy import Selector
from urllib import request
import time
from selenium.webdriver.common.action_chains import ActionChains
import re
import datetime
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-gpu')

base_url = 'http://xueshu.baidu.com/usercenter/paper/show?paperid=%s'
mongo_url = "mongodb://localhost:27017"

try_num = 0

for index in range(1):
    client = pymongo.MongoClient(mongo_url)
    db = client['paper']
    collection_name = 'keyword_%s' % index
    browser = webdriver.Chrome(options=chrome_options)
    results = db[collection_name].find()
    paper_list = []
    try:
        item_index = 0
        # while item_index < db:
        for item_index,result in enumerate(results[0:10]):
            try:
                paperid = result['paperid']
                url = base_url % paperid
                browser.get(url)
                time.sleep(1)
                # WebDriverWait(browser,2).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#container #dtl_l .list-tab-out p[type="reference"]')))
                page_source = browser.page_source
                selector = Selector(text=page_source)
                title = selector.css('.main-info h3')
                if title != []:
                    button = selector.css('#container #dtl_l .list-tab-out p[type="reference"]')
                    if button != []:
                        button = browser.find_element_by_css_selector('#container #dtl_l .list-tab-out p[type="reference"]')
                        ActionChains(browser).move_to_element(button).perform()
                        ActionChains(browser).click().perform()
                        WebDriverWait(browser, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.reference_lists')))
                        page_source = browser.page_source
                        selector = Selector(text=page_source)
                        references = selector.css('.con_reference .reference_lists .rel_title')
                        for refer in references:
                            title = refer.css('a::text').extract_first()
                            paperid = refer.xpath('./a/@href').extract_first()
                            paper = {}
                            paper['title'] = title
                            paper['paperid'] = re.findall('.*paperid=(.*?)(&{1}.+|$)',paperid)[0][0]
                            paper['index'] = 0
                            paper['abstract'] = ''
                            paper['authors'] = []
                            paper['quote_num'] = ''
                            paper['date'] = ''
                            paper['key_words'] = ''
                            paper['free_sources'] = ''
                            paper_list.append(paper)
                        if len(paper_list) > 100:
                            time.sleep(4)
                            print(datetime.datetime.today())
                            db_refer = client['refer']
                            for paper in paper_list:
                                paperid = paper['paperid']
                                if db_refer[collection_name].find({'paperid':paperid}).count() == 0:
                                    db_refer[collection_name].insert_one(paper)
                            paper_list = []
                item_index += 1
            except:
                print('发生异常')
                try_num += 1
                if try_num > 3:
                    item_index += 1
                    try_num = 0
        if len(paper_list) > 0:
            db_refer = client['refer']
            for paper in paper_list:
                paperid = paper['paperid']
                if db_refer[collection_name].find({'paperid': paperid}).count() == 0:\
                    db_refer[collection_name].insert_one(paper)
            paper_list = []
    except:
        print('发生错误！！')
    finally:
        client.close()
        browser.quit()