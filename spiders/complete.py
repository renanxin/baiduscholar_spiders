# import pymongo
# from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from scrapy.http import HtmlResponse
# from logging import getLogger
# from urllib.parse import quote
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from scrapy import Selector
# from urllib import request
# import time
# from selenium.webdriver.common.action_chains import ActionChains
# from pyquery import PyQuery as pq
# import re
# import datetime
# from fake_useragent import UserAgent
# ua = UserAgent()
#
# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument('lang=zh_CN.UTF-8')
#
#
# def is_Chinese(word):
#     for ch in word:
#         if '\u4e00' <= ch <= '\u9fff':
#             return True
#     return False
#
# base_url = 'http://xueshu.baidu.com/usercenter/paper/show?paperid=%s'
# mongo_url = "mongodb://localhost:27017"
# iter = 0
#
# # for key_index in range(1):
# #     client = pymongo.MongoClient(mongo_url)
# #     browser = webdriver.Chrome(options=chrome_options)
# #     collection_name = 'keyword_%s' % key_index
# #     db = client['refer']
# #     # results = db[collection_name].find(no_cursor_timeout=True).batch_size(5)
# #     finds = db[collection_name].find()
# #     results = []
# #     for find in finds:
# #         results.append(find)
# #     for result in results:
# #         try:
# #             paperid = result['paperid']
# #             url = base_url % paperid
# #             browser.get(url)
# #             WebDriverWait(browser, 10).until(
# #                 EC.presence_of_element_located((By.CSS_SELECTOR, '#head_wr')))
# #             selector = Selector(text=browser.page_source)
# #             title = selector.css('.main-info h3')
# #             if title != []:
# #                 if iter % 100 == 0:
# #                     print(datetime.datetime.today())
# #                     print(browser.current_url + '                ' + str(key_index))
# #
# #                 title = WebDriverWait(browser, 10).until(
# #                     EC.presence_of_element_located((By.CSS_SELECTOR, '.main-info h3')))
# #                 selector = Selector(text=browser.page_source)
# #                 button = selector.css('.paper_src_wr a[class="src_tabitem savelink-tar"]')  # 用于判断是否存在免费资源
# #                 if button == []:
# #                     button = None
# #                 if button != None:
# #                     button = browser.find_element_by_css_selector('.paper_src_wr a[class="src_tabitem savelink-tar"]')
# #                 if button != None:
# #                     button.click()
# #                 response = browser.page_source
# #                 # response = request.urlopen(url)
# #                 response = Selector(text=response)
# #                 paper = {}
# #                 paper['index'] = key_index
# #                 paperid = re.findall('.*paperid=(.*?)(&{1}.+|$)', browser.current_url)[0][0]
# #                 paper['paperid'] = paperid
# #                 paper['title'] = pq('<html>' + response.css('.main-info h3').extract_first() + '</html>').text()
# #                 paper['abstract'] = response.css('.main-info .abstract_wr .abstract::text').extract_first()
# #                 if paper['abstract']:
# #                     paper['abstract'] = pq('<html>' + paper['abstract'] + '</html>').text()
# #                 paper['authors'] = []
# #                 authors = response.css('.main-info .c_content .author_wr .author_text span')
# #                 for author in authors:
# #                     paper['authors'].append(author.css('a::text').extract_first())
# #                 paper['quote_num'] = response.css('.main-info .c_content .ref-wr-num a::text').extract_first()
# #                 paper['date'] = response.css('.journal_content::text').extract_first()
# #                 if paper['date']:
# #                     paper['date'] = paper['date'].replace(' ', '').replace('\n', '')
# #                 if paper['quote_num']:
# #                     paper['quote_num'] = paper['quote_num'].replace(' ', '').replace('\n', '')
# #                 if paper['abstract']:
# #                     if is_Chinese(paper['title']):
# #                         paper['abstract'] = paper['abstract'].replace(' ', '').replace('\n', '')
# #                     else:
# #                         paper['abstract'] = paper['abstract'].replace('\n', '')
# #                 key_words = []
# #                 keys = response.css('.c_content .kw_main span')
# #                 for key in keys:
# #                     key_word_ = key.css('a::text').extract_first()
# #                     key_words.append(key_word_)
# #                 paper['key_words'] = key_words
# #                 if button:
# #                     sources = response.css('.paper_src_wr #savelink_wr span a')
# #                     free_sources = []
# #                     for source in sources:
# #                         free_source = source.xpath('./@href').extract_first()
# #                         free_sources.append(free_source)
# #                         if (len(free_sources) > 9):    break
# #                     paper['free_sources'] = free_sources
# #                 else:
# #                     paper['free_sources'] = None
# #                 db[collection_name].update_one({'paperid':paperid},{'$set':paper})
# #                 iter += 1
# #                 time.sleep(0.5)
# #         except:
# #             browser.quit()
# #             browser = webdriver.Chrome(options=chrome_options)
# #             print('出现错误！！！')
# #     iter = 0
# #     browser.quit()
# #     client.close()
# #     time.sleep(30)
#
#
# client = pymongo.MongoClient(mongo_url)
# paper_db = client['paper']
# key_len = len(paper_db.list_collection_names())
# client.close()
# try_num = 0
# result_index = 0
# usr_gent = ''
# start = 32
# while start < key_len:
#     try:
#         for key_index in range(start,key_len):
#             client = pymongo.MongoClient(mongo_url)
#             paper_db = client['paper']
#             collection_name = 'keyword_%s' % key_index
#             finds = paper_db[collection_name].find()
#             results = []
#             for find in finds:
#                 results.append(find)
#             browser = webdriver.Chrome(options=chrome_options)
#             while result_index < len(results):
#                 result = results[result_index]
#                 try:
#                     paper_id = result['paperid']
#                     url = base_url % paper_id
#                     if iter%100 == 0:
#                         browser.quit()
#                         chrome_options.add_argument('user-agent="%s"' % ua.chrome)
#                         browser = webdriver.Chrome(options=chrome_options)
#                     browser.get(url)
#                     WebDriverWait(browser, 10).until(
#                         EC.presence_of_element_located((By.CSS_SELECTOR, '#head_wr')))
#                     selector = Selector(text=browser.page_source)
#                     title = selector.css('.main-info h3')
#                     if title != []:
#                         if iter % 100 == 0:
#                             print(datetime.datetime.today())
#                             print(browser.current_url + '                ' + str(key_index))
#                         title = WebDriverWait(browser, 10).until(
#                             EC.presence_of_element_located((By.CSS_SELECTOR, '.main-info h3')))
#                         selector = Selector(text=browser.page_source)
#                         result['resource'] = selector.css('.container_right .journal_title::text').extract_first()
#                         paper_db[collection_name].update_one({'paperid': paper_id}, {'$set': {'resource':result['resource']}},upsert=True)
#                         iter += 1
#                         time.sleep(0.5)
#                     result_index += 1
#
#                 except:
#
#                     if try_num < 3:
#                         try_num += 1
#                         time.sleep(0.5*try_num)
#                     else:
#                         try_num = 0
#                         result_index += 1
#                         print('出现错误')
#                         browser.quit()
#                         new_gent = ua.chrome
#                         while new_gent == usr_gent:
#                             new_gent = ua.chrome
#                         usr_gent = new_gent
#                         chrome_options.add_argument('user-agent="%s"' % usr_gent)
#                         browser = webdriver.Chrome(options=chrome_options)
#             iter = 0
#             browser.quit()
#             client.close()
#             time.sleep(20)
#             try_num = 0
#             result_index = 0
#             start += 1
#     except:
#         time.sleep(300)
#         print('出现大错误!')



import pymongo
from bson import ObjectId
client = pymongo.MongoClient('mongodb://admin:123456@129.28.155.10:27017/professor')
client_user = pymongo.MongoClient('mongodb://admin:123456@129.28.155.10:27017/user')
db = client['professor']
db_user = client_user['user']
with open('author.txt','r') as f:
    author = f.readline()
    while author:
        try:
            author = eval(author.strip())
            result = db['professor'].find_one({'scholarID': author['scholarID']})
            db_user['user'].insert_one({'_id': ObjectId(str(result['_id'])), 'name': result['name']})
        except:
            pass
        author  =f.readline()


#
# with open('paper.txt','r') as f:
#     paper = f.readline()
#     while paper:
#         try:
#             paper = eval(paper.strip())
#             db['resource'].insert_one(paper)
#         except:
#             pass
#         finally:
#             paper = f.readline()
#
#
# with open('author.txt','r') as f:
#     author = f.readline()
#     while author:
#         try:
#             author = eval(author.strip())
#             author['field'] = author['areas']
#             del author['areas']
#             db['professor'].insert_one(author)
#             result = db['professor'].find_one({'scholarID': author['scholarID']})
#             db_user['user'].insert_one({'_id': ObjectId(str(result['_id'])), 'name': author['name']})
#         except:
#             pass
#         finally:
#             author = f.readline()

# import pymongo
# from bson import ObjectId
# import requests
# from scrapy import selector
# from fake_useragent import UserAgent
# ua = UserAgent(path='fake_useragent.json')
# usr_gent = ''
#
# base_url = 'http://xueshu.baidu.com/scholarID/%s'
# client = pymongo.MongoClient('mongodb://admin:123456@129.28.155.10:27017/professor')
# client_user = pymongo.MongoClient('mongodb://admin:123456@129.28.155.10:27017/user')
# db = client['professor']
# db_user = client_user['user']
# iter = 0
# with open('author.txt') as f:
#     author = f.readline()
#     while author:
#         author = eval(author.strip())
#         # result = db['professor'].find_one({'scholarID':author['scholarID']})
#         if 'name' not in author.keys():
#             if iter % 100 == 0:
#                 print(iter)
#                 new_gent = ua.chrome
#                 while new_gent == usr_gent:
#                     new_gent = ua.chrome
#                 usr_gent = new_gent
#             res = requests.get(base_url % author['scholarID'],headers = {'User-Agent': usr_gent})
#
#             select =  selector.Selector(text=res.text.encode('ISO-8859-1').decode(res.apparent_encoding))
#             name = select.css('.p_name::text').extract_first()
#             db['professor'].update_one({'scholarID':author['scholarID']},{'$set':{'name':name}},upsert=True)
#             iter += 1
#         author = f.readline()

