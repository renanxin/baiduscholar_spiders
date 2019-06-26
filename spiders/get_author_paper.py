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
  # chrome_options.add_argument('--headless')
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument('--disable-gpu')

  author_base_url = 'http://xueshu.baidu.com/scholarID/%s'
  paper_base_url = 'http://xueshu.baidu.com/usercenter/paper/show?paperid=%s'
  mongo_url = "mongodb://localhost:27017"
  start_url = 'http://xueshu.baidu.com/usercenter/data/authorchannel?cmd=inject_page&author=%s&affiliate='

  client =  pymongo.MongoClient(mongo_url)
  db = client['author']
  num = 0
  results = db['authors'].find()
  for result in results:
      if 'papers' in result.keys():
          num += len(result['papers'])
  client = pymongo.MongoClient(mongo_url)
  db = client['author']
  with open('scholarID.txt','w') as file:
      authors = db['authors'].find()
      for author in authors[0:16000]:
          if 'scholarID' in author.keys() and 'papers' not in author.keys():
              file.write(author['scholarID']+'\n')
  client.close()

  try_num = 0

  with open('scholarID.txt', 'r') as file:
      scholarID = file.readline().strip()
      while scholarID != None:
          browser = webdriver.Chrome(options=chrome_options)
          client = pymongo.MongoClient(mongo_url)
          try:
              browser.get(author_base_url % scholarID)
              WebDriverWait(browser,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'.p_name')))
              author = {}
              author['name'] = browser.find_element_by_css_selector('.p_name').text
              print(author['name'])
              arrow = ['a']
              author['papers'] = []
              WebDriverWait(browser,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'span[class="filter_sel_text"]')))
              while arrow != []:
                  time.sleep(1)
                  select = Selector(text=browser.page_source)
                  papers = select.css('.in_conternt_reslist .result .reqdata')
                  for paper in papers:
                      paperID = paper.xpath('./@data-longsign').extract_first()
                      author['papers'].append(paperID)
                  arrow = select.css('a[class="c-icon-page-next-hover res-page-next pagenumber"]')
                  if arrow != [] :
                      try:
                          WebDriverWait(browser,5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'a[class="c-icon-page-next-hover res-page-next pagenumber"]')))
                      except:
                          pass
                      button = browser.find_element_by_css_selector('a[class="c-icon-page-next-hover res-page-next pagenumber"]')
                      ActionChains(browser).move_to_element(button).click().perform()
              db = client['author']
              db['authors'].update_one({'scholarID': scholarID}, {'$set': {'name':author['name'],'papers':author['papers']}},upsert=True)
              client.close()
              browser.quit()
              scholarID = file.readline().strip()
              time.sleep(120)
          except:
              try_num += 1
              browser.quit()
              client.close()
              if try_num > 3:
                  scholarID = file.readline().strip()
                  try_num = 0
              time.sleep(20)

          new_gent = ua.chrome
          while new_gent == usr_gent:
              new_gent = ua.chrome
          usr_gent = new_gent
          chrome_options.add_argument('user-agent="%s"' % usr_gent)
 
  display.stop()

  import json
  client = pymongo.MongoClient('mongodb://admin:123456@129.28.155.10:27017/user')
  db = client['user']
  a = list(db['user'].find())[0]
  a['_id'] = str(a['_id'])
  print(json.dumps(a))
  client.close()
#
#

'''
   爬取对应的图片
'''
import requests
import random
import datetime
from scrapy import Selector
import pymongo
import os
from fake_useragent import UserAgent
import time

location ='/Users/renweidediannao/Downloads/fake_useragent.json'
ua = UserAgent(path=location)
usr_gent = ua.chrome

base_url = 'http://xueshu.baidu.com/usercenter/journal/navigation?query=&language=1&page=%s'
img_filename = '/Users/renweidediannao/Downloads/images/%s.jpg'
iter = 0
# while True:
    # paperid = get_paperid()
    # if paperid is None:
    #     with open('log.txt', 'w') as f:
    #         f.write('finish')
    #     break
    # res = requests.get(base_url % paperid, headers={'User-Agent': usr_gent})
    # select = Selector(text=res.text)
    # img_href = select.css('a[class="img_link"]').xpath('./img/@src').extract_first()
    # if img_href:
    #     try:
    #         img = requests.get(img_href, headers={'User-Agent': usr_gent})
    #         with open(img_filename % paperid, 'wb') as f:
    #             f.write(img.content)
    #         iter += 1
    #     except:
    #         print('获取图片失败!')
    # if iter % 50 == 0:
    #     if iter % 100 == 0:
    #         print(datetime.datetime.today(), ' ' * 10, iter)
    #     new_gent = ua.chrome
    #     while new_gent == usr_gent:
    #         new_gent = ua.chrome
    #     usr_gent = new_gent
    # if iter > 1000:
    #     exit()

for index in range(1,716):
    if index % 20 ==0:
        new_gent = ua.chrome
        while new_gent == usr_gent:
            new_gent = ua.chrome
        usr_gent = new_gent
    page = requests.get(base_url % index , headers={'User-Agent': usr_gent})
    select = Selector(text=page.text)
    results = select.css('.journal_detail' )
    for result in results:
        name = result.css('a[class = "journal_title LOG_WR"]::text').extract_first()
        img_url = result.xpath('./a/img/@src').extract_first()
        img = requests.get(img_url, headers={'User-Agent': usr_gent})
        try:
            with open(img_filename % name,'wb') as f:
                f.write(img.content)
        except:
            print('出错！')
    time.sleep(1)
