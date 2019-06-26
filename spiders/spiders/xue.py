# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from selenium.webdriver.common.proxy import ProxyType

from xueshu.items import XueshuItem
from  pyquery import PyQuery as pq
from urllib import request
from scrapy import Selector
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
import time
import re
import random
import pymongo

class XueSpider(scrapy.Spider):
    name = 'xue'
    allowed_domains = ['https://xueshu.baidu.com/']
    start_urls = 'https://xueshu.baidu.com/'

    def parse(self, response):
         results = response.css('#container #content_left #content_leftrs div[class="result sc_default_result xpath-log"]')
         for result in results:
             paper = XueshuItem()
             paper['title'] = pq(result.css('.sc_content h3[class="t c_font"] a').extract_first()).text().replace(' ','')
             paper['abstract'] = pq(result.css('.c_abstract').extract_first()).text()
             paper['authors'] = []
             authors= result.css('.sc_info a[data-click="{\'button_tp\':\'author\'}"]')
             for author in authors:
                 paper['authors'].append(author.css('a::text').extract_first())
             paper['quote_num'] = pq(result.css('span .sc_cite_cont::text').extract_first()).text()
             paper['date'] = pq(result.css('.sc_time::text').extract_first()).text()
             yield paper

         urls = response.body.decode('utf-8')
         urls = urls.split('\t')
         browser = webdriver.PhantomJS()
         index = response.request.meta['index']
         for url in urls:
             browser.get(url)
             title = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'.main-info h3')))
             selector = Selector(text=browser.page_source)
             button = selector.css('.paper_src_wr a[class="src_tabitem savelink-tar"]')      # 用于判断是否存在免费资源
             if button==[]:
                 button=None
             if button!=None:
                 button = browser.find_element_by_css_selector('.paper_src_wr a[class="src_tabitem savelink-tar"]')
             if button!=None:
                 button.click()
             response = browser.page_source
             # response = request.urlopen(url)
             response = Selector(text=response)
             paper = XueshuItem()
             paper['index'] = index
             paperid = re.findall('.*paperid=(.*?)(&{1}.+|$)',url)[0][0]
             paper['paperid'] = paperid
             paper['title'] = pq(response.css('.main-info h3').extract_first()).text()
             paper['abstract'] = response.css('.main-info .abstract_wr .abstract::text').extract_first()
             if paper['abstract']:
                 paper['abstract'] = pq(paper['abstract']).text()
             paper['authors'] = []
             authors= response.css('.main-info .c_content .author_wr .author_text span')
             for author in authors:
                 paper['authors'].append(author.css('a::text').extract_first())
             paper['quote_num'] = response.css('.main-info .c_content .ref-wr-num a::text').extract_first()
             paper['date'] = response.css('.journal_content::text').extract_first()
             if paper['date']:
                 paper['date']=paper['date'].replace(' ','').replace('\n','')
             if paper['quote_num']:
                 paper['quote_num']=paper['quote_num'].replace(' ','').replace('\n','')
             if paper['abstract']:
                 paper['abstract'] = paper['abstract'].replace(' ','').replace('\n','')
             key_words = []
             keys = response.css('.c_content .kw_main span')
             for key in keys:
                 key_word = key.css('a::text').extract_first()
                 key_words.append(key_word)
             paper['key_words'] = key_words
             if button:
                 sources = response.css('.paper_src_wr #savelink_wr span a')
                 free_sources = []
                 for source in sources:
                     free_source = source.xpath('./@href').extract_first()
                     free_sources.append(free_source)
                     if(len(free_sources)>9):    break
                 paper['free_sources'] = free_sources
             else:
                 paper['free_sources'] = None
             yield paper
             time.sleep(1)
         browser.close()






        urls = response.body.decode('utf-8')
        index = response.request.meta['index']
        flag = True

        if flag:
            with open('/Users/renweidediannao/Desktop/key_word.txt', 'r') as file:
                num = file.readlines().__len__()
            index += 1
            new_index = index
            print(new_index)
            if index<num:
                new_keyword = None
                with open('/Users/renweidediannao/Desktop/key_word.txt','r') as file:
                    while index>0:
                        file.readline()
                        index-=1
                    new_keyword = file.readline().strip()
                    print(new_keyword)
                time.sleep(30*random.random())
                yield Request(url=self.start_urls, meta={'key_word': new_keyword, 'index': new_index},
                              callback=self.parse, dont_filter=True)





    def start_requests(self):
        key_words = []
        with open('/Users/renweidediannao/Desktop/key_words.csv') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                key_words.extend(line.split(':'))
        with open('/Users/renweidediannao/Desktop/key_word.txt','w') as file:
            for key in key_words:
                file.write(key+'\n')
        yield Request(url=self.start_urls, meta={'key_word': key_words[282], 'index': 282},
                      callback=self.parse, dont_filter=True)

