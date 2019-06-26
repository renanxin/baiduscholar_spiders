# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from logging import getLogger
from urllib.parse import quote
import time
from scrapy import Selector
import random
from xueshu.items import XueshuItem
import re
import time
import re
import random
from pyquery import PyQuery as pq
import pymongo
from selenium.webdriver.chrome.options import Options
import datetime
chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')


class seleniumMiddle(object):
    def __init__(self):
        # self.browser = webdriver.Chrome(options=chrome_options)
        self.browser = webdriver.PhantomJS()
        self.wait = WebDriverWait(self.browser,10)
        self.logger = getLogger(__name__)

    def __del__(self):
        print('The browser has been delete')
        self.browser.close()

    def process_request(self,request,spider):
        try:
            key_word = request.meta['key_word']
            index = request.meta['index']
            # self.browser.delete_all_cookies()
            self.browser.quit()
            self.browser = webdriver.PhantomJS()
            # self.browser = webdriver.Chrome(options=chrome_options)
            self.browser.get(request.url)
            input = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.s_ipt_wr #kw')))
            submit = WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.s_btn_wr #su')))
            input.clear()
            input.send_keys(key_word)
            submit.click()
            print()
            # return HtmlResponse(url=request.url,body=self.browser.page_source,status=200,request=request,encoding='utf-8')
            body = []
            i = 0
            while True:
                nums = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                            '#container #content_left #content_leftrs div[class="result sc_default_result xpath-log"]')))
                results = self.browser.find_elements_by_css_selector(
                    '#container #content_left #content_leftrs div[class="result sc_default_result xpath-log"]')
                items = []
                current_url = self.browser.current_url
                for result_index in range(len(results)):
                    # print(result_index)
                    result = results[result_index]
                    time.sleep(1*random.random())
                    a = result.find_element_by_css_selector('.sc_content h3 a')
                    # print(a)
                    a.click()
                    handles = self.browser.window_handles
                    self.browser.switch_to_window(handles[-1])
                    title = WebDriverWait(self.browser, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#head_wr')))
                    selector = Selector(text=self.browser.page_source)
                    title = selector.css('.main-info h3')
                    # body.append(self.browser.current_url)
                    # selector = Selector(text=self.browser.page_source)
                    # title = selector.css('.main-info h3')  # 用于判断是否存在免费资源
                    # if title == []:
                    #     for k in range(5):
                    #         print('k        '+str(k))
                    #         self.browser.close()
                    #         handles = self.browser.window_handles
                    #         self.browser.switch_to_window(handles[0])
                    #         a = result.find_element_by_css_selector('.sc_content h3 a')
                    #         a.click()
                    #         time.sleep(k)
                    #         handles = self.browser.window_handles
                    #         self.browser.switch_to_window(handles[1])
                    #         title = self.browser.find_element_by_css_selector('.main-info h3')
                    #         if title != []:
                    #             break
                    if title!=[]:
                        if i%100 == 0:
                            print(datetime.datetime.today())
                            print(self.browser.current_url+'                '+key_word)


                        title = WebDriverWait(self.browser, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.main-info h3')))
                        selector = Selector(text=self.browser.page_source)
                        button = selector.css('.paper_src_wr a[class="src_tabitem savelink-tar"]')      # 用于判断是否存在免费资源
                        if button == []:
                            button = None
                        if button != None:
                            button = self.browser.find_element_by_css_selector('.paper_src_wr a[class="src_tabitem savelink-tar"]')
                        if button!=None:
                            button.click()
                        response = self.browser.page_source
                        # response = request.urlopen(url)
                        response = Selector(text=response)
                        paper = XueshuItem()
                        paper['index'] = index
                        paperid = re.findall('.*paperid=(.*?)(&{1}.+|$)',self.browser.current_url)[0][0]
                        paper['paperid'] = paperid
                        paper['title'] = pq('<html>'+response.css('.main-info h3').extract_first()+'</html>').text()
                        paper['abstract'] = response.css('.main-info .abstract_wr .abstract::text').extract_first()
                        if paper['abstract']:
                                paper['abstract'] = pq('<html>'+paper['abstract']+'</html>').text()
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
                            if index % 2 == 0:
                                paper['abstract'] = paper['abstract'].replace(' ','').replace('\n','')
                            else:
                                paper['abstract'] = paper['abstract'].replace('\n', '')
                        key_words = []
                        keys = response.css('.c_content .kw_main span')
                        for key in keys:
                            key_word_ = key.css('a::text').extract_first()
                            key_words.append(key_word_)
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
                        items.append(paper)

                        time.sleep(0.5*random.random())
                    # handles = self.browser.window_handles
                    # while handles.__len__()>1:
                    #     self.browser.switch_to_window(handles[1])
                    #     if self.browser.current_url != current_url:
                    #         self.browser.close()
                    #     else:
                    #         self.browser.switch_to_window(handles[0])
                    #         self.browser.close()
                    #     handles = self.browser.window_handles
                    while len(self.browser.window_handles)>1:
                        handles = self.browser.window_handles
                        self.browser.switch_to_window(handles[1])
                        self.browser.close()
                        self.browser.switch_to_window(handles[0])
                    handles = self.browser.window_handles
                    self.browser.switch_to_window(handles[0])
                    nums = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                                '#container #content_left #content_leftrs div[class="result sc_default_result xpath-log"]')))
                    results = self.browser.find_elements_by_css_selector(
                        '#container #content_left #content_leftrs div[class="result sc_default_result xpath-log"]')
                    i+=1
                mongo_url = "mongodb://localhost:27017"
                client = pymongo.MongoClient(mongo_url)
                db = client['paper']
                collection_name = 'keyword_%s' % index
                for item in items:
                    db[collection_name].insert(dict(item))
                client.close()
                items = []
                if len(body)>1000:
                    break
                # 尝试寻找d下一页
                selector = Selector(text=self.browser.page_source)
                button = selector.css('.content_left_ls #page a[style="margin-right: 19px;"]')
                if button == []:
                    break
                button = WebDriverWait(self.browser,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.content_left_ls #page a[style="margin-right: 19px;"]')))
                button.click()
                time.sleep(0.5*random.random())

            body = "\t".join(body)
            return HtmlResponse(url=request.url, body=body, status=200, request=request,
                               encoding='utf-8')

        except TimeoutException:
            while len(self.browser.window_handles) > 0:
                handles = self.browser.window_handles
                self.browser.switch_to_window(handles[0])
                self.browser.close()
            self.browser.quit()
            self.browser = webdriver.PhantomJS()
            # self.browser = webdriver.Chrome(options=chrome_options)
            print("出现错误！！！")
            return HtmlResponse(url=request.url,status=200,body='500',request=request,encoding='utf-8')
        except Exception:
            self.browser.quit()
            print('未知错误')






class XueshuSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class XueshuDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# import json
# mongo_url = "mongodb://localhost:27017"
# client = pymongo.MongoClient(mongo_url)
# db = client['paper']
# # num = 0
# # for i in range(84):
# #     collection_name = 'keyword_%s' % i
# #     num += db[collection_name].find().count()
# # print(num)
# # client.close()
# basedir = '/Users/renweidediannao/Desktop/database/'
# collection_name = 'keyword_%s' % 75
# result = db[collection_name].find()
# try:
#     for index in range(276,280):
#         file_name = basedir + ('keyword_%s.txt' % index)
#         results = db['keyword_%s' % index].find()
#         with open(file_name,'w') as f:
#             for i in results:
#                 i = dict(i)
#                 i.pop('_id')
#                 f.write(json.dumps(dict(i))+'\n')
# finally:
#     client.close()


# try:
#     for index in range(75,151):
#         collection_name = 'keyword_%s' % index
#         db[collection_name].drop()
# finally:
#     client.close()

# import pymongo
# mongo_url = "mongodb://localhost:27017"
# client = pymongo.MongoClient(mongo_url)
# db = client['paper']
# num = 0
# for i in range(280):
#     collection_name = 'keyword_%s' % i
#     num += db[collection_name].find().count()
#
# print(num)
# client.close()